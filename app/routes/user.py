from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models.data_point import DataPoint
from ..models.esg_data import ESGData
from ..extensions import db

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'User':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard', methods=['GET','POST'])
@user_required
def dashboard():
    if not current_user.entity_id:
        flash('No entity assigned to user', 'error')
        return redirect(url_for('auth.login'))
        
    assigned_data_points = DataPoint.query.filter(
        DataPoint.entities.any(id=current_user.entity_id)
    ).all()

    entity_data_entries = {
        data_point.data_point_id: data_point.value 
        for data_point in ESGData.query.filter_by(entity_id=current_user.entity_id).all()
    }

    return render_template('user_dashboard.html',
                         data_points=assigned_data_points,
                         entity_data_entries=entity_data_entries)

@user_bp.route('/submit_data', methods=['POST'])
@user_required
def submit_data():
    if not current_user.entity_id:
        flash('No entity assigned to user', 'error')
        return redirect(url_for('user.dashboard'))

    entity_id = current_user.entity_id

    # Iterate over submitted form data to save values
    for key, value in request.form.items():
        if key.startswith('data_point_'):
            data_point_id = int(key.split('_')[2])
            value = float(value) if value else None

            # Check if an entry already exists for this data point and entity
            esg_data = ESGData.query.filter_by(
                entity_id=entity_id,
                data_point_id=data_point_id
            ).first()

            if esg_data:
                esg_data.value = value
            else:
                esg_data = ESGData(
                    account="Account Name",
                    metric="Metric Name",
                    value=value,
                    entity_id=entity_id,
                    data_point_id=data_point_id
                )
                db.session.add(esg_data)

    db.session.commit()
    flash('Data submitted successfully', 'success')
    return redirect(url_for('user.dashboard'))
