from django.core.mail import send_mail


def send_confirmation_email(user):
    code = user.activation_code
    full_link = f'http://localhost:8000/api/v1/account/activate/{code}'
    to_email = user.email
    send_mail(
        'Hi, please activate your account!',
        f'Follow the link to activate: {full_link}',
        'account@marketeer.com',
        [to_email],
        fail_silently=False,
    )


def send_reset_passwor_email(user):
    code = user.activation_code
    to_email = user.email
    send_mail(
        'Password reset',
        f'Your code: {code}',
        'account@marketeer.com',
        [to_email],
        fail_silently=False,
    )


def send_order_notification(user, id):
    to_email = user.email
    send_mail(
        'Order Notification',
        f'You have created an order: #{id}.\nShipping will take ~1 week.\nThanks for choosing us.',
        'orders@marketeer.com',
        [to_email],
        fail_silently=False,
    )
