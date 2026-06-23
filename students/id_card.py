from io import BytesIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image as PILImage, ImageDraw
from .models import Student
import os
from django.conf import settings


class StudentIDCardView(LoginRequiredMixin, View):
    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{student.roll_number}_id_card.pdf"'

        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=landscape(A5))
        w, h = landscape(A5)

        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'college-logo.png')

        # Background
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Top dark band
        c.setFillColorRGB(0.01, 0.12, 0.30)
        c.rect(0, h-14*mm, w, 14*mm, fill=1, stroke=0)

        # Bottom dark band
        c.setFillColorRGB(0.01, 0.12, 0.30)
        c.rect(0, 0, w, 6*mm, fill=1, stroke=0)

        # Gold accent line
        c.setFillColorRGB(0.77, 0.65, 0.29)
        c.rect(0, 6*mm, w, 0.5*mm, fill=1, stroke=0)

        # Card border
        c.setStrokeColorRGB(0.01, 0.12, 0.30)
        c.setLineWidth(0.8)
        c.rect(1.5*mm, 1.5*mm, w-3*mm, h-3*mm, fill=0, stroke=1)

        # Logo
        if os.path.exists(logo_path):
            try:
                logo = PILImage.open(logo_path)
                logo.thumbnail((9*mm, 9*mm))
                lb = BytesIO()
                logo.save(lb, format='PNG')
                lb.seek(0)
                c.drawImage(lb, 3*mm, h-12*mm, width=8*mm, height=8*mm, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(13*mm, h-9.5*mm, "MIRACLE INSTITUTE OF TECHNOLOGY, KANPUR")
        c.setFont("Helvetica", 4.5)
        c.drawString(13*mm, h-12*mm, "AKTU Affiliated | AICTE Approved | NAAC A+ Accredited")

        # Card type
        c.setFillColorRGB(0.77, 0.65, 0.29)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(3*mm, h-17*mm, "STUDENT IDENTITY CARD")

        # Separator
        c.setStrokeColorRGB(0.85, 0.85, 0.85)
        c.setLineWidth(0.3)
        c.line(3*mm, h-18.5*mm, w-3*mm, h-18.5*mm)

        # ---- PHOTO (left) ----
        px, py = 4*mm, h-52*mm
        ps = 27*mm

        c.setStrokeColorRGB(0.01, 0.12, 0.30)
        c.setLineWidth(0.6)
        c.rect(px, py, ps, ps, fill=0, stroke=1)

        photo_ok = False
        if student.profile_photo and os.path.exists(student.profile_photo.path):
            try:
                img = PILImage.open(student.profile_photo.path).convert('RGBA')
                img = img.resize((100, 100), PILImage.LANCZOS)

                circ = PILImage.new('RGBA', (100, 100), (0, 0, 0, 0))
                m = ImageDraw.Draw(circ)
                m.ellipse((2, 2, 97, 97), fill=(255, 255, 255, 255))
                img = PILImage.composite(img, circ, circ)

                temp = BytesIO()
                img.save(temp, format='PNG')
                temp.seek(0)
                c.drawImage(temp, px+0.5*mm, py+0.5*mm, width=ps-1*mm, height=ps-1*mm, preserveAspectRatio=True, mask='auto')
                photo_ok = True
            except Exception:
                pass

        if not photo_ok:
            c.setFillColorRGB(0.92, 0.94, 0.96)
            c.rect(px+0.5*mm, py+0.5*mm, ps-1*mm, ps-1*mm, fill=1, stroke=0)
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.setFont("Helvetica-Bold", 14)
            init = (student.first_name[0] + student.last_name[0]).upper()
            tw = c.stringWidth(init, "Helvetica-Bold", 14)
            c.drawString(px + (ps - tw)/2, py + ps/2 - 5, init)

        # ---- NAME & ROLL (right of photo) ----
        rx = px + ps + 5*mm

        c.setFillColorRGB(0.01, 0.12, 0.30)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(rx, py+ps-3*mm, student.full_name.upper())

        c.setFillColorRGB(0.77, 0.65, 0.29)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(rx, py+ps-9*mm, f"Roll: {student.roll_number}")

        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.setFont("Helvetica", 6.5)
        c.drawString(rx, py+ps-14*mm, f"B.Tech {student.student_class.name}")
        c.drawString(rx, py+ps-18.5*mm, f"{student.student_class.section}  |  {student.student_class.academic_year}")

        # ---- DETAILS GRID ----
        dx = rx
        dy = py + ps - 26*mm
        col_w = 34*mm
        row_h = 4.2*mm
        label_c = (0.5, 0.5, 0.5)
        val_c = (0.02, 0.02, 0.02)

        data = [
            (0, 0, "Date of Birth", student.date_of_birth.strftime('%d-%b-%Y') if hasattr(student.date_of_birth, 'strftime') else str(student.date_of_birth)),
            (1, 0, "Gender", student.get_gender_display()),
            (0, 1, "Blood Group", getattr(student, 'blood_group', 'N/A')),
            (1, 1, "Admission", student.admission_date.strftime('%d-%b-%Y') if hasattr(student.admission_date, 'strftime') else str(student.admission_date)),
            (0, 2, "Father's Name", student.father_name),
            (1, 2, "Mother's Name", student.mother_name),
            (0, 3, "Guardian Ph", student.guardian_contact),
            (1, 3, "Contact", student.contact_number),
            (0, 4, "Email", student.email or 'N/A'),
        ]

        for col, row, label, value in data:
            x = dx + col * col_w
            y = dy - row * row_h
            c.setFillColorRGB(*label_c)
            c.setFont("Helvetica", 5)
            c.drawString(x, y, label)
            c.setFillColorRGB(*val_c)
            c.setFont("Helvetica-Bold", 5.5)
            c.drawString(x, y - 2.5*mm, str(value)[:28])

        # ---- ADDRESS ----
        addr_y = dy - 6 * row_h
        c.setFillColorRGB(*label_c)
        c.setFont("Helvetica", 5)
        c.drawString(dx, addr_y, "Address")
        c.setFillColorRGB(*val_c)
        c.setFont("Helvetica-Bold", 5.5)
        c.drawString(dx, addr_y - 2.5*mm, str(student.address)[:65])

        # ---- SIGNATURE & VALIDITY ----
        bot_y = addr_y - 8*mm
        if bot_y < 14*mm:
            bot_y = 14*mm

        c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.setLineWidth(0.3)
        c.line(dx, bot_y, dx+38*mm, bot_y)

        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Helvetica", 5)
        c.drawString(dx, bot_y - 3*mm, "Authorised Signatory")

        if hasattr(student.admission_date, 'year'):
            vt = f"Valid: {student.admission_date.year}-{student.admission_date.year+4}"
        else:
            vt = "Valid: Current Session"
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.setFont("Helvetica", 5)
        c.drawRightString(w - 5*mm, bot_y - 3*mm, vt)

        # Footer
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Oblique", 4.5)
        c.drawCentredString(w/2, 3*mm, "Computer-generated ID card | Verify at student.miracle.ac.in")

        c.showPage()
        c.save()

        buf.seek(0)
        response.write(buf.read())
        return response
