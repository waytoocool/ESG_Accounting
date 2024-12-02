from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from ..models.user import User
from ..models.entity import Entity
from ..models.framework import Framework
from ..extensions import db
from ..services.email import send_registration_email
from ..services.token import generate_registration_token
from ..services.redis import check_rate_limit

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'Admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/home')
@admin_required
def home():
    return render_template('admin/home.html')

@admin_bp.route('/data_hierarchy', methods=['GET', 'POST'])
@admin_required
def data_hierarchy():
    def build_hierarchy(entity, visited, all_entities):
        if entity.id in visited:
            return None
        visited.add(entity.id)
        users = [{"name": user.username, "email": user.email} for user in entity.users]
        children = [
            build_hierarchy(child, visited, all_entities)
            for child in all_entities if child.parent_id == entity.id
        ]
        children = [child for child in children if child is not None]
        return {
            'name': entity.name or "Unnamed Entity",
            'details': entity.entity_type or "Unknown Type",
            'users': users,
            'children': children
        }

    if request.method == 'POST':
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid request method'}), 400
        
        try:
            name = request.form.get('name')
            entity_type = request.form.get('entity_type')
            parent_id = request.form.get('parent_id')

            if not name or not entity_type or not parent_id:
                return jsonify({'success': False, 'message': 'Name, entity type, and parent are required.'}), 400

            if Entity.query.filter_by(name=name).first():
                return jsonify({'success': False, 'message': 'Entity with this name already exists.'}), 400
            
            max_hierarchy_level = 3
            parent = Entity.query.get(parent_id)

            if parent.get_hierarchy_level >= max_hierarchy_level:
                response = {
                    'success': False,
                    'message': 'Maximum hierarchy level of {max_hierarchy_level} reached.'
                }
                return jsonify(response) if request.headers.get('X-Requested-With') else redirect(url_for('data_hierarchy'))

            new_entity = Entity(name=name, entity_type=entity_type, parent_id=parent_id)
            db.session.add(new_entity)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Entity created successfully!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'An error occurred while creating the entity'})
   
    entities = Entity.query.all()
    hierarchy_data = [
        build_hierarchy(entity, set(), entities) 
        for entity in entities if entity.parent_id is None
    ]
    hierarchy_data = [item for item in hierarchy_data if item is not None]

    return render_template('admin/data_hierarchy.html', 
                         entities=entities, 
                         hierarchy_data=hierarchy_data)

@admin_bp.route('/frameworks', methods=['GET', 'POST'])
@admin_required
def frameworks():
    if request.method == 'POST':
        framework_name = request.form['framework_name']
        data_point_names = request.form.getlist('data_point_name')
        data_point_value_types = request.form.getlist('data_point_value_type')
        data_point_units = request.form.getlist('data_point_unit')

        framework = Framework(name=framework_name)
        db.session.add(framework)
        db.session.commit()

        for i in range(len(data_point_names)):
            new_data_point = DataPoint(
                name=data_point_names[i],
                value_type=data_point_value_types[i],
                unit=data_point_units[i],
                framework_id=framework.id
            )
            db.session.add(new_data_point)
        db.session.commit()

        return redirect(url_for('admin.frameworks'))

    frameworks = Framework.query.all()
    return render_template('admin/frameworks.html', 
                         frameworks=frameworks, 
                         entities=Entity.query.all())

@admin_bp.route('/assign_data_points', methods=['GET', 'POST'])
@admin_required
def assign_data_points():
    if request.method == 'POST':
        entity_id = request.form['entity']
        selected_data_points = request.form.getlist('data_points')
        entity = Entity.query.get(entity_id)

        for dp_id in selected_data_points:
            data_point = DataPoint.query.get(dp_id)
            if data_point not in entity.data_points:
                entity.data_points.append(data_point)
        db.session.commit()

        return redirect(url_for('admin.home'))

    entities = Entity.query.all()
    data_points = DataPoint.query.all()
    return render_template('admin/assign_data_points.html', 
                         entities=entities, 
                         data_points=data_points)

@admin_bp.route('/create_user', methods=['POST'])
@admin_required
def create_user():
    username = request.form.get('username')
    email = request.form['email']
    entity_id = request.form['entity_id']
    
    new_user = User(
        username=username, 
        email=email, 
        entity_id=entity_id, 
        role="User", 
        is_email_verified=False
    )
    db.session.add(new_user)
    db.session.commit()

    token = generate_registration_token(new_user.id)
    send_registration_email(email, token)

    return jsonify({
        'success': True, 
        'message': 'User created successfully. An email has been sent for registration.'
    })



@admin_bp.route('/resend_verification', methods=['POST'])
@login_required
@admin_required  # Restrict access to Admins
def resend_verification():
    """
    Admin route to resend verification email for a user.

    Request Body:
        email (str): Email address of the user to resend verification.

    Returns:
        JSON response with success or failure status.
    """
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'})

        # Check if user exists and needs verification
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})

        if user.is_email_verified:
            return jsonify({'success': False, 'message': 'User is already verified'})

        # Use the rate limit helper function
        can_send, limit_message = check_rate_limit(email)
        if not can_send:
            return jsonify({'success': False, 'message': limit_message})

        # Generate and send new token
        token = generate_registration_token(user.id)
        send_registration_email(email, token)

        return jsonify({
            'success': True,
            'message': 'Verification email has been sent successfully.'
        })

    except Exception as e:
        current_app.logger.error(f'Error in resend_verification: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your request.'
        })

