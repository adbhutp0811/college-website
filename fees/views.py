import hashlib
import hmac
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from students.models import Student
from .models import FeeStructure, OnlinePayment, Payment

try:
    import razorpay
    HAS_RAZORPAY = True
except ImportError:
    HAS_RAZORPAY = False

try:
    import stripe as stripe_lib
    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False


class StudentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_portal')
        self.student = get_object_or_404(Student, pk=student_id)
        return super().dispatch(request, *args, **kwargs)


class FeeListView(ListView):
    model = FeeStructure
    template_name = 'fees/fee_list.html'
    context_object_name = 'fee_structures'


class StudentFeeListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'fees/student_fees.html'
    context_object_name = 'payments'

    def get_queryset(self):
        student_id = self.request.session.get('student_id')
        if student_id:
            return Payment.objects.filter(student_id=student_id).select_related('fee_structure')
        return Payment.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        if student_id:
            ctx['fee_structures'] = FeeStructure.objects.all()
            ctx['student'] = get_object_or_404(Student, pk=student_id)
            total_due = sum(fs.amount for fs in FeeStructure.objects.all())
            total_paid = sum(p.amount_paid for p in Payment.objects.filter(student_id=student_id))
            ctx['total_due'] = total_due
            ctx['total_paid'] = total_paid
            ctx['balance'] = total_due - total_paid
        return ctx


class FeePaymentView(LoginRequiredMixin, View):
    def get(self, request, pk):
        fee = get_object_or_404(FeeStructure, pk=pk)
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id) if student_id else None
        return render(request, 'fees/fee_payment.html', {'fee': fee, 'student': student})

    def post(self, request, pk):
        fee = get_object_or_404(FeeStructure, pk=pk)
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_portal')
        student = get_object_or_404(Student, pk=student_id)
        amount = request.POST.get('amount', fee.amount)
        Payment.objects.create(
            student=student,
            fee_structure=fee,
            amount_paid=amount,
            status='paid',
            transaction_id=f'TXN{uuid.uuid4().hex[:12].upper()}',
        )
        messages.success(request, f'Payment of ₹{amount} successful! Transaction ID: {Payment.objects.last().transaction_id}')
        return redirect('fees:student_fees')


# ─── Online Payment Views ───────────────────────────────────────────────

class FeeSelectionView(StudentRequiredMixin, View):
    def get(self, request):
        fee_structures = FeeStructure.objects.all()
        unpaid_fees = []
        for f in fee_structures:
            total_paid_for_fee = sum(
                p.amount_paid for p in Payment.objects.filter(
                    student=self.student, fee_structure=f
                )
            )
            if total_paid_for_fee < f.amount:
                unpaid_fees.append(f)

        all_payments = Payment.objects.filter(student=self.student)
        total_paid = sum(p.amount_paid for p in all_payments)
        total_due = sum(f.amount for f in fee_structures)

        return render(request, 'fees/fee_selection.html', {
            'student': self.student,
            'unpaid_fees': unpaid_fees,
            'total_due': total_due,
            'total_paid': total_paid,
            'balance': total_due - total_paid,
        })


class InitiatePaymentView(StudentRequiredMixin, View):
    def get(self, request, fee_id):
        fee = get_object_or_404(FeeStructure, pk=fee_id)

        if Payment.objects.filter(
            student=self.student, fee_structure=fee, status='paid'
        ).exists():
            messages.info(request, 'This fee has already been paid.')
            return redirect('fees:fee_selection')

        gateway = settings.PAYMENT_GATEWAY
        amount_paise = int(fee.amount * 100)

        has_keys = (
            bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
            if gateway == 'razorpay' else
            bool(settings.STRIPE_PUBLISHABLE_KEY and settings.STRIPE_SECRET_KEY)
            if gateway == 'stripe' else False
        )

        if not has_keys:
            order_id = f'demo_{uuid.uuid4().hex[:12]}'
            OnlinePayment.objects.create(
                student=self.student,
                fee_structure=fee,
                amount=fee.amount,
                order_id=order_id,
                status='created',
                gateway='demo',
            )
            return render(request, 'fees/checkout.html', {
                'student': self.student,
                'fee': fee,
                'gateway': 'demo',
                'amount': fee.amount,
                'order_id': order_id,
            })

        if gateway == 'razorpay' and HAS_RAZORPAY:
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET
            ))
            receipt = f'rec_{self.student.pk}_{fee.pk}_{uuid.uuid4().hex[:6]}'
            try:
                order = client.order.create({
                    'amount': amount_paise,
                    'currency': 'INR',
                    'receipt': receipt,
                    'payment_capture': 1,
                })
            except Exception as e:
                messages.error(request, f'Failed to create payment order: {e}')
                return redirect('fees:fee_selection')

            OnlinePayment.objects.create(
                student=self.student,
                fee_structure=fee,
                amount=fee.amount,
                order_id=order['id'],
                status='created',
                gateway='razorpay',
            )
            return render(request, 'fees/checkout.html', {
                'student': self.student,
                'fee': fee,
                'gateway': 'razorpay',
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id': order['id'],
                'amount_paise': amount_paise,
                'amount': fee.amount,
            })

        elif gateway == 'stripe' and HAS_STRIPE:
            stripe_lib.api_key = settings.STRIPE_SECRET_KEY
            try:
                session = stripe_lib.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {'name': fee.name},
                            'unit_amount': amount_paise,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(
                        reverse('fees:payment_success')
                    ) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri(
                        reverse('fees:fee_selection')
                    ),
                    client_reference_id=str(self.student.pk),
                )
            except Exception as e:
                messages.error(request, f'Failed to create Stripe session: {e}')
                return redirect('fees:fee_selection')

            OnlinePayment.objects.create(
                student=self.student,
                fee_structure=fee,
                amount=fee.amount,
                order_id=session['id'],
                status='created',
                gateway='stripe',
            )
            return redirect(session['url'])

        messages.error(request, 'No payment gateway configured.')
        return redirect('fees:fee_selection')

    def post(self, request, fee_id):
        fee = get_object_or_404(FeeStructure, pk=fee_id)
        order_id = f'demo_{uuid.uuid4().hex[:12]}'
        online_payment = OnlinePayment.objects.create(
            student=self.student,
            fee_structure=fee,
            amount=fee.amount,
            order_id=order_id,
            status='paid',
            gateway='demo',
        )
        online_payment.gateway_payment_id = f'demo_{uuid.uuid4().hex[:12]}'
        online_payment.save()

        payment = Payment.objects.create(
            student=self.student,
            fee_structure=fee,
            amount_paid=fee.amount,
            status='paid',
            transaction_id=online_payment.gateway_payment_id,
            gateway='demo',
        )
        online_payment.payment_record = payment
        online_payment.save()

        messages.success(request, f'Demo payment of ₹{fee.amount} successful!')
        return render(request, 'fees/payment_success.html', {
            'payment': payment,
            'online_payment': online_payment,
            'gateway': 'demo',
        })


class PaymentSuccessView(View):
    def get(self, request):
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_portal')
        student = get_object_or_404(Student, pk=student_id)

        razorpay_payment_id = request.GET.get('razorpay_payment_id')
        razorpay_order_id = request.GET.get('razorpay_order_id')
        razorpay_signature = request.GET.get('razorpay_signature')

        if razorpay_order_id and razorpay_payment_id:
            online_payment = get_object_or_404(
                OnlinePayment, order_id=razorpay_order_id, student=student
            )
            if online_payment.status == 'paid':
                messages.info(request, 'This payment has already been processed.')
                return render(request, 'fees/payment_success.html', {
                    'payment': online_payment.payment_record,
                    'online_payment': online_payment,
                    'gateway': 'razorpay',
                })

            expected_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
                hashlib.sha256,
            ).hexdigest()

            if expected_signature == razorpay_signature:
                online_payment.status = 'paid'
                online_payment.gateway_payment_id = razorpay_payment_id
                online_payment.signature = razorpay_signature
                online_payment.save()

                payment = Payment.objects.create(
                    student=student,
                    fee_structure=online_payment.fee_structure,
                    amount_paid=online_payment.amount,
                    status='paid',
                    transaction_id=razorpay_payment_id,
                    gateway='razorpay',
                    razorpay_order_id=razorpay_order_id,
                    payment_intent_id=razorpay_payment_id,
                )
                online_payment.payment_record = payment
                online_payment.save()

                messages.success(request, f'Payment of ₹{online_payment.amount} successful via Razorpay!')
                return render(request, 'fees/payment_success.html', {
                    'payment': payment,
                    'online_payment': online_payment,
                    'gateway': 'razorpay',
                })
            else:
                online_payment.status = 'failed'
                online_payment.save()
                messages.error(request, 'Payment verification failed. Signature mismatch.')
                return redirect('fees:fee_selection')

        session_id = request.GET.get('session_id')
        if session_id and HAS_STRIPE:
            stripe_lib.api_key = settings.STRIPE_SECRET_KEY
            try:
                session = stripe_lib.checkout.Session.retrieve(session_id)
            except Exception:
                messages.error(request, 'Failed to verify Stripe session.')
                return redirect('fees:fee_selection')

            if session.payment_status == 'paid':
                online_payment = get_object_or_404(
                    OnlinePayment, order_id=session_id, student=student
                )
                if online_payment.status == 'paid':
                    messages.info(request, 'This payment has already been processed.')
                    return render(request, 'fees/payment_success.html', {
                        'payment': online_payment.payment_record,
                        'online_payment': online_payment,
                        'gateway': 'stripe',
                    })

                online_payment.status = 'paid'
                online_payment.gateway_payment_id = session.get('payment_intent', session_id)
                online_payment.save()

                payment = Payment.objects.create(
                    student=student,
                    fee_structure=online_payment.fee_structure,
                    amount_paid=online_payment.amount,
                    status='paid',
                    transaction_id=session.get('payment_intent', session_id),
                    gateway='stripe',
                    stripe_session_id=session_id,
                    payment_intent_id=session.get('payment_intent', ''),
                )
                online_payment.payment_record = payment
                online_payment.save()

                messages.success(request, f'Payment of ₹{online_payment.amount} successful via Stripe!')
                return render(request, 'fees/payment_success.html', {
                    'payment': payment,
                    'online_payment': online_payment,
                    'gateway': 'stripe',
                })
            else:
                messages.error(request, f'Stripe payment status: {session.payment_status}')
                return redirect('fees:fee_selection')

        demo_order_id = request.GET.get('demo_order_id')
        if demo_order_id:
            online_payment = get_object_or_404(
                OnlinePayment, order_id=demo_order_id, student=student
            )
            if online_payment.status == 'paid':
                messages.info(request, 'This payment has already been processed.')
                return render(request, 'fees/payment_success.html', {
                    'payment': online_payment.payment_record,
                    'online_payment': online_payment,
                    'gateway': 'demo',
                })

            online_payment.status = 'paid'
            online_payment.gateway_payment_id = f'demo_{uuid.uuid4().hex[:12]}'
            online_payment.save()

            payment = Payment.objects.create(
                student=student,
                fee_structure=online_payment.fee_structure,
                amount_paid=online_payment.amount,
                status='paid',
                transaction_id=online_payment.gateway_payment_id,
                gateway='demo',
            )
            online_payment.payment_record = payment
            online_payment.save()

            messages.success(request, f'Demo payment of ₹{online_payment.amount} successful!')
            return render(request, 'fees/payment_success.html', {
                'payment': payment,
                'online_payment': online_payment,
                'gateway': 'demo',
            })

        messages.error(request, 'Invalid payment response.')
        return redirect('fees:fee_selection')


class OnlinePaymentHistoryView(StudentRequiredMixin, View):
    def get(self, request):
        online_payments = OnlinePayment.objects.filter(
            student=self.student
        ).select_related('fee_structure', 'payment_record')
        return render(request, 'fees/payment_history.html', {
            'student': self.student,
            'online_payments': online_payments,
        })
