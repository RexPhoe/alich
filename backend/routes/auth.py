from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models.user import User, db
from models.employee import Employee
from utils.db_logger import log_database_query, log_query_details, log_error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Datos incompletos', 'error': 'Se requiere nombre de usuario y contraseña'}), 400
    
    try:
        # Log the query details
        log_query_details("User.query.filter_by(username=?).first()", {"username": data['username']})
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Credenciales inválidas', 'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        log_error(e, "Login attempt failed")
        return jsonify({'message': 'Error en el inicio de sesión', 'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    # Only admins can register new users
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    data = request.get_json()
    
    required_fields = ['username', 'password', 'role', 'first_name', 'last_name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': 'Datos incompletos', 'error': f'Se requiere el campo {field}'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Error de registro', 'error': 'El nombre de usuario ya existe'}), 409
    
    # Check if email already exists
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Error de registro', 'error': 'El correo electrónico ya está registrado'}), 409
    
    try:
        # Start a transaction
        db.session.begin()
        
        # Create user
        user = User(username=data['username'], password=data['password'], role=data['role'])
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID
        
        # Create employee
        employee = Employee(
            user_id=user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            hire_date=datetime.strptime(data.get('hire_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        )
        db.session.add(employee)
        
        # Commit the transaction
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al registrar usuario', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado', 'error': 'El usuario no existe'}), 404
    
    # Get employee data if exists
    employee_data = None
    if user.employee:
        employee_data = user.employee.to_dict()
    
    return jsonify({
        'user': user.to_dict(),
        'employee': employee_data
    }), 200

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado', 'error': 'El usuario no existe'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Datos incompletos', 'error': 'Se requiere la contraseña actual y la nueva'}), 400
    
    if not user.check_password(data['current_password']):
        return jsonify({'message': 'Contraseña incorrecta', 'error': 'La contraseña actual es incorrecta'}), 401
    
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar contraseña', 'error': str(e)}), 500