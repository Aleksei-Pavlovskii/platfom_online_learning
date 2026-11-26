import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str, description: str = '') -> dict:
    """Создаёт продукт в Stripe. Возвращает dict с id."""
    product = stripe.Product.create(
        name=name,
        description=description,
    )
    return {'id': product.id, 'name': product.name}


def create_stripe_price(product_id: str, amount: int, currency: str = 'usd') -> dict:
    """Создаёт цену в Stripe."""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency=currency,
    )
    return {'id': price.id, 'unit_amount': price.unit_amount, 'currency': price.currency}


def create_stripe_checkout_session(
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict | None = None,
) -> dict:
    """Создаёт сессию оплаты. Возвращает dict с url и id."""
    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata or {},
    )
    return {'id': session.id, 'url': session.url}


def retrieve_stripe_session(session_id: str) -> dict:
    """Получает данные сессии по id (для проверки статуса)."""
    session = stripe.checkout.Session.retrieve(session_id)
    return {
        'id': session.id,
        'status': session.status,
        'payment_status': session.payment_status,
        'url': session.url,
    }
