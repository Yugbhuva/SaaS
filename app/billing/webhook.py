from flask import request, abort
from app.billing import bp
from app.models.models import User
from app import db
import stripe
from config import Config
from datetime import datetime

stripe.api_key = Config.STRIPE_SECRET_KEY
webhook_secret = Config.STRIPE_WEBHOOK_SECRET

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        abort(400)
    except stripe.error.SignatureVerificationError as e:
        abort(400)

    # Handle the event
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])

    return '', 200

def handle_subscription_created(subscription):
    user = User.query.filter_by(stripe_customer_id=subscription['customer']).first()
    if user:
        user.subscription_id = subscription['id']
        user.subscription_status = subscription['status']
        user.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
        db.session.commit()

def handle_subscription_updated(subscription):
    user = User.query.filter_by(stripe_customer_id=subscription['customer']).first()
    if user:
        user.subscription_status = subscription['status']
        user.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
        db.session.commit()

def handle_subscription_deleted(subscription):
    user = User.query.filter_by(stripe_customer_id=subscription['customer']).first()
    if user:
        user.subscription_status = 'cancelled'
        user.subscription_id = None
        db.session.commit()

def handle_payment_succeeded(invoice):
    # You can add logic here for successful payments
    # e.g., send receipt email, generate license keys, etc.
    pass

def handle_payment_failed(invoice):
    # Handle failed payments
    # e.g., send notification email, update user status, etc.
    pass
