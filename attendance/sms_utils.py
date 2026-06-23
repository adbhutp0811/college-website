import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(phone_number, message):
    """
    Send SMS via configured provider.
    For development, logs to console.
    To use a real provider, add SMS_API config in settings.py.
    """
    if not phone_number:
        return False

    api_key = getattr(settings, 'SMS_API_KEY', '')
    provider = getattr(settings, 'SMS_PROVIDER', 'console')

    if provider == 'console' or not api_key:
        logger.info(f'SMS to {phone_number}: {message}')
        print(f'[SMS] To: {phone_number} | Message: {message}')
        return True

    if provider == 'msg91':
        import requests
        url = 'https://api.msg91.com/api/sendhttp.php'
        params = {
            'authkey': api_key,
            'mobiles': phone_number,
            'message': message,
            'sender': getattr(settings, 'SMS_SENDER_ID', 'MITKNP'),
            'route': '4',
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            return resp.ok
        except Exception as e:
            logger.error(f'SMS failed to {phone_number}: {e}')
            return False

    if provider == 'twilio':
        from twilio.rest import Client
        try:
            client = Client(
                getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
                getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            )
            client.messages.create(
                body=message,
                from_=getattr(settings, 'TWILIO_FROM_NUMBER', ''),
                to=phone_number
            )
            return True
        except Exception as e:
            logger.error(f'Twilio SMS failed: {e}')
            return False

    return True
