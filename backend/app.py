from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from config import Config
from models import db

# Import routes
from routes.auth import auth_bp
from routes.employees import employees_bp
from routes.attendance import attendance_bp
from routes.teams import teams_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize JWT Manager
jwt = JWTManager(app)

# Configure JWT settings
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Token inválido',
        'error': 'El token proporcionado no es válido'
    }), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'message': 'Token expirado',
        'error': 'El token ha expirado'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'message': 'Token no proporcionado',
        'error': 'Se requiere un token de acceso'
    }), 401

# Enable CORS with specific configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
    r"/api/*/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(employees_bp, url_prefix='/api/employees')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(teams_bp, url_prefix='/api/teams')

# Root route
@app.route('/')
def index():
    return jsonify({
        'message': 'Bienvenido a la API de ALICH - Sistema de Control de Asistencia',
        'status': 'online'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'message': 'Recurso no encontrado',
        'error': str(error)
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'message': 'Error interno del servidor',
        'error': str(error)
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Changed default from 5000 to 5001
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
