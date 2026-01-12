import stripe
from django.conf import settings


def _get_stripe_api_key():
    """Получает API ключ Stripe из настроек"""
    if not stripe.api_key:
        stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe.api_key


def create_stripe_product(course_name, course_description):
    """
    Создает продукт в Stripe
    
    Args:
        course_name: Название курса
        course_description: Описание курса
    
    Returns:
        str: ID продукта в Stripe
    """
    _get_stripe_api_key()
    product = stripe.Product.create(
        name=course_name,
        description=course_description,
    )
    return product.id


def create_stripe_price(product_id, amount):
    """
    Создает цену для продукта в Stripe
    
    Args:
        product_id: ID продукта в Stripe
        amount: Сумма в рублях (в копейках, например 10000 = 100.00 руб)
    
    Returns:
        str: ID цены в Stripe
    """
    _get_stripe_api_key()
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,  # Сумма в копейках
        currency='rub',  # Валюта - рубли
    )
    return price.id


def create_stripe_session(price_id, success_url, cancel_url):
    """
    Создает сессию оплаты в Stripe
    
    Args:
        price_id: ID цены в Stripe
        success_url: URL для редиректа после успешной оплаты
        cancel_url: URL для редиректа при отмене оплаты
    
    Returns:
        dict: Объект сессии с полями 'id' и 'url'
    """
    _get_stripe_api_key()
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {
        'id': session.id,
        'url': session.url
    }
    