from flask import Blueprint, jsonify
from flask_login import login_required
from app.models import Reservation
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/summary', methods=['GET'])
@login_required
def get_summary():
    # Group by status and count
    results = db.session.query(Reservation.status, func.count(Reservation.id)).group_by(Reservation.status).all()
    
    summary = {
        "PENDING": 0,
        "BOOKED": 0,
        "CHECKED_IN": 0,
        "CHECKED_OUT": 0,
        "CANCELLED": 0
    }
    
    for status, count in results:
        summary[status] = count
        
    return jsonify(summary), 200
