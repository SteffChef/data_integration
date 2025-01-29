from flask import Blueprint, jsonify, request
from ..models import User
from ..extensions import db

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])

@users_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    # Standard Location: Germany
    latitude = data.get('latitude', 51.961563)
    longitude = data.get('longitude', 7.628202)
    new_user = User(name=data['name'], email=data['email'], latitude=latitude, longitude=longitude)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201
