from marketeer.celery import app
from account import send_email
from django.contrib.auth import get_user_model

User = get_user_model()


@app.task
def send_activation_email(email):
    user = User.objects.get(email=email)
    send_email.send_confirmation_email(user)


@app.task
def send_reset_password_email(email):
    user = User.objects.get(email=email)
    send_email.send_reset_passwor_email(user)


@app.task
def send_order_notif(email, id):
    user = User.objects.get(email=email)
    send_email.send_reset_passwor_email(user, id)


@app.task
def send_payment_notif(email, id):
    user = User.objects.get(email=email)
    send_email.send_payment_notification(user, id)


@app.task
def send_prod_create_notif(email, id, title, price, description, category):
    user = User.objects.get(email=email)
    send_email.send_product_notification(user, id, title, price, description, category)
