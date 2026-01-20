import stripe
from django.conf import settings


class StripeServiceError(Exception):
    """Ошибка взаимодействия со Stripe API."""


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
    try:
        product = stripe.Product.create(
            name=course_name,
            description=course_description,
        )
        return product.id
    except stripe.error.StripeError as exc:
        message = getattr(exc, "user_message", None) or str(exc)
        raise StripeServiceError(f"Не удалось создать продукт в Stripe: {message}") from exc


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
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount,  # Сумма в копейках
            currency='rub',  # Валюта - рубли
        )
        return price.id
    except stripe.error.StripeError as exc:
        message = getattr(exc, "user_message", None) or str(exc)
        raise StripeServiceError(f"Не удалось создать цену в Stripe: {message}") from exc


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
    try:
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
    except stripe.error.StripeError as exc:
        message = getattr(exc, "user_message", None) or str(exc)
        raise StripeServiceError(f"Не удалось создать сессию оплаты Stripe: {message}") from exc


def cleanup_stripe_resources(product_id=None, price_id=None, session_id=None):
    """Best-effort очистка Stripe ресурсов, если что-то пошло не так."""
    _get_stripe_api_key()

    if session_id:
        try:
            stripe.checkout.Session.expire(session_id)
        except stripe.error.StripeError:
            pass

    if price_id:
        try:
            stripe.Price.modify(price_id, active=False)
        except stripe.error.StripeError:
            pass

    if product_id:
        try:
            stripe.Product.delete(product_id)
        except stripe.error.StripeError:
            pass
    