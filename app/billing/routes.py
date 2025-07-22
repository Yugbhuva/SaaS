from flask import request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.billing import bp
from app.models.models import User
from app import db
import stripe
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

# Pricing plans
PRICING_PLANS = {
    'basic': {
        'name': 'Basic Plan',
        'price': 999,  # $9.99 in cents
        'interval': 'month'
    },
    'pro': {
        'name': 'Pro Plan', 
        'price': 2999,  # $29.99 in cents
        'interval': 'month'
    }
}

@bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        plan = request.form.get('plan')
        if plan not in PRICING_PLANS:
            flash('Invalid plan selected')
            return redirect(url_for('pricing'))
        
        plan_info = PRICING_PLANS[plan]
        
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan_info['name'],
                    },
                    'unit_amount': plan_info['price'],
                    'recurring': {
                        'interval': plan_info['interval']
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('billing.success', _external=True),
            cancel_url=url_for('pricing', _external=True),
        )
        
        return redirect(checkout_session.url, code=303)
    
    except Exception as e:
        flash('Error creating checkout session')
        return redirect(url_for('pricing'))

@bp.route('/success')
@login_required
def success():
    return render_template('billing/success.html')

@bp.route('/cancel')
@login_required
def cancel():
    return render_template('billing/cancel.html')

@bp.route('/customer-portal')
@login_required
def customer_portal():
    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for('dashboard', _external=True)
        )
        return redirect(session.url, code=303)
    except Exception as e:
        flash('Error accessing customer portal')
        return redirect(url_for('dashboard'))

@bp.route('/subscription-status')
@login_required
def subscription_status():
    return jsonify({
        'status': current_user.subscription_status,
        'expires': current_user.current_period_end.isoformat() if current_user.current_period_end else None
    })