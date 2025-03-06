from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging
from models.user import User, db
from models.employee import Employee
from models.work_schedule import WorkSchedule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/', methods=['GET'])
@jwt_required()
def get_employees():
    try:
        # Log request details
        logger.info('GET /api/employees - Fetching employees list')
        logger.info(f'Request args: {request.args}')
        
        # Check if user is admin
        current_user_id = get_jwt_identity()
        logger.info(f'User ID: {current_user_id} attempting to access employees list')
        
        current_user = User.query.get(current_user_id)
        if not current_user:
            logger.error(f'User not found for ID: {current_user_id}')
            return jsonify({'message': 'No autorizado', 'error': 'Usuario no encontrado'}), 403
        
        logger.info(f'User role: {current_user.role}')
        if not current_user.is_admin():
            logger.warning(f'Non-admin user {current_user_id} attempted to access employees list')
            return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        department = request.args.get('department')
        status = request.args.get('status')
        search = request.args.get('search')
        
        logger.info(f'Query params - page: {page}, per_page: {per_page}, department: {department}, status: {status}, search: {search}')
        
        # Build query
        query = Employee.query
        
        if department:
            query = query.filter(Employee.department == department)
            logger.debug(f'Filtering by department: {department}')
        
        if status:
            query = query.filter(Employee.status == status)
            logger.debug(f'Filtering by status: {status}')
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                (Employee.first_name.ilike(search_term)) |
                (Employee.last_name.ilike(search_term)) |
                (Employee.email.ilike(search_term))
            )
            logger.debug(f'Filtering by search term: {search}')
        
        # Execute query with pagination
        employees = query.order_by(Employee.last_name).paginate(page=page, per_page=per_page)
        logger.info(f'Query executed, found {employees.total} total employees')
        
        # Format response
        result = {
            'employees': [employee.to_dict() for employee in employees.items],
            'total': employees.total,
            'pages': employees.pages,
            'current_page': employees.page
        }
        
        logger.info(f'Successfully fetched {len(employees.items)} employees for page {page}')
        logger.debug(f'Response data: {result}')
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Error fetching employees: {str(e)}')
        logger.exception('Full traceback:')
        return jsonify({'message': 'Error al obtener empleados', 'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    # Check if user is admin or the employee themselves
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    # Only admins or the employee themselves can view details
    if not current_user.is_admin() and current_user.id != employee.user_id:
        return jsonify({'message': 'No autorizado', 'error': 'No tiene permisos para ver este empleado'}), 403
    
    # Get work schedules
    schedules = WorkSchedule.query.filter_by(employee_id=employee.id).all()
    schedules_data = [schedule.to_dict() for schedule in schedules]
    
    # Combine employee data with schedules
    employee_data = employee.to_dict()
    employee_data['work_schedules'] = schedules_data
    
    return jsonify(employee_data), 200

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Datos incompletos', 'error': 'No se proporcionaron datos para actualizar'}), 400
    
    try:
        # Update employee fields
        if 'first_name' in data:
            employee.first_name = data['first_name']
        if 'last_name' in data:
            employee.last_name = data['last_name']
        if 'email' in data and data['email'] != employee.email:
            # Check if email already exists
            existing_email = Employee.query.filter(Employee.email == data['email'], Employee.id != employee.id).first()
            if existing_email:
                return jsonify({'message': 'Error de actualización', 'error': 'El correo electrónico ya está registrado'}), 409
            employee.email = data['email']
        if 'phone' in data:
            employee.phone = data['phone']
        if 'department' in data:
            employee.department = data['department']
        if 'position' in data:
            employee.position = data['position']
        if 'status' in data:
            employee.status = data['status']
        if 'hire_date' in data:
            employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Empleado actualizado exitosamente',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar empleado', 'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    try:
        # Instead of deleting, mark as inactive
        employee.status = 'inactive'
        db.session.commit()
        
        return jsonify({
            'message': 'Empleado desactivado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al desactivar empleado', 'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/schedules', methods=['GET'])
@jwt_required()
def get_employee_schedules(employee_id):
    # Check if user is admin or the employee themselves
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    # Only admins or the employee themselves can view schedules
    if not current_user.is_admin() and current_user.id != employee.user_id:
        return jsonify({'message': 'No autorizado', 'error': 'No tiene permisos para ver este horario'}), 403
    
    schedules = WorkSchedule.query.filter_by(employee_id=employee.id).all()
    schedules_data = [schedule.to_dict() for schedule in schedules]
    
    return jsonify({
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'schedules': schedules_data
    }), 200

@employees_bp.route('/<int:employee_id>/schedules', methods=['POST'])
@jwt_required()
def add_employee_schedule(employee_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    data = request.get_json()
    
    if not data or 'day_of_week' not in data or 'start_time' not in data or 'end_time' not in data:
        return jsonify({'message': 'Datos incompletos', 'error': 'Se requieren día de la semana, hora de inicio y hora de fin'}), 400
    
    try:
        # Parse times
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        # Create schedule
        schedule = WorkSchedule(
            employee_id=employee.id,
            day_of_week=data['day_of_week'],
            start_time=start_time,
            end_time=end_time
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Horario agregado exitosamente',
            'schedule': schedule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al agregar horario', 'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_employee_schedule(employee_id, schedule_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    schedule = WorkSchedule.query.get(schedule_id)
    
    if not schedule or schedule.employee_id != employee_id:
        return jsonify({'message': 'Horario no encontrado', 'error': 'El horario no existe para este empleado'}), 404
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Horario eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar horario', 'error': str(e)}), 500