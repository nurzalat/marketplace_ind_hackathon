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


def send_order_notification(user, id, code):
    to_email = user.email
    full_link = f'http://localhost:8000/api/v1/order/activate/{code}'
    send_mail(
        'Order Notification',
        f'You have created an order: #{id}.\nConfirm order through the link: {full_link}.'
        f'\nThanks for choosing us.',
        'orders@marketeer.com',
        [to_email],
        fail_silently=False,
    )


def send_payment_notification(user, id):
    to_email = user.email
    send_mail(
        'Order Payment Success',
        f'Payment for an order: #{id} was successful.\nShipping will take ~1 week.\nThanks for choosing us.',
        'orders@marketeer.com',
        [to_email],
        fail_silently=False,
    )


def send_product_notification(user, id, title, price, description, category):
    to_email = user.email
    send_mail(
        'New Product Notification',
        f'You have created a product: #{id}.\nName: {title}\nPrice: {price}\n'
        f'Description: {description}\nCategory: {category}'
        f'\nThanks for choosing us.',
        'orders@marketeer.com',
        [to_email],
        fail_silently=False,
    )
