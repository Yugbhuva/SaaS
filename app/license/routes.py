from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.license import bp
from app.models.models import License
from app.license.utils import generate_jwt_license, validate_jwt_license
from app import db

@bp.route('/generate', methods=['POST'])
@login_required
def generate_license():
    """Generate a new license key for the current user"""
    if not current_user.has_active_subscription():
        return jsonify({'error': 'Active subscription required'}), 403
    
    product_name = request.json.get('product_name', 'Default Product')
    
    license = License(
        user_id=current_user.id,
        product_name=product_name
    )
    license.generate_key()
    
    db.session.add(license)
    db.session.commit()
    
    return jsonify({
        'license_key': license.key,
        'product_name': license.product_name,
        'created_at': license.created_at.isoformat()
    })

@bp.route('/validate', methods=['POST'])
def validate_license():
    """Validate a license key via API"""
    license_key = request.json.get('license_key')
    product_name = request.json.get('product_name')
    
    if not license_key:
        return jsonify({'valid': False, 'error': 'License key required'}), 400
    
    license = License.query.filter_by(key=license_key).first()
    
    if not license:
        return jsonify({'valid': False, 'error': 'License not found'}), 404
    
    if product_name and license.product_name != product_name:
        return jsonify({'valid': False, 'error': 'Invalid product'}), 400
    
    if not license.is_valid():
        return jsonify({'valid': False, 'error': 'License expired or inactive'}), 400
    
    # Increment activation count
    license.current_activations += 1
    db.session.commit()
    
    return jsonify({
        'valid': True,
        'user_email': license.user.email,
        'product_name': license.product_name,
        'expires_at': license.expires_at.isoformat() if license.expires_at else None,
        'activations_remaining': license.max_activations - license.current_activations
    })

@bp.route('/my-licenses')
@login_required
def my_licenses():
    """Show user's licenses"""
    licenses = License.query.filter_by(user_id=current_user.id).all()
    return render_template('license/my_licenses.html', licenses=licenses)

@bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate_license():
    """Deactivate a license key"""
    license_key = request.json.get('license_key')
    
    license = License.query.filter_by(
        key=license_key,
        user_id=current_user.id
    ).first()
    
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    license.is_active = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'License deactivated'})