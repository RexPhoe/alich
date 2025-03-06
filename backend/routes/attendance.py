from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from models.user import User, db
from models.employee import Employee
from models.attendance import Attendance
from models.work_schedule import WorkSchedule

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    # Get current user
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    # Get employee associated with user
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    
    if not employee or not employee.is_active():
        return jsonify({'message': 'No autorizado', 'error': 'Empleado no encontrado o inactivo'}), 403
    
    # Check if already checked in today
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    existing_attendance = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.check_in >= today_start,
        Attendance.check_in <= today_end
    ).first()
    
    if existing_attendance:
        return jsonify({
            'message': 'Ya has registrado entrada hoy',
            'attendance': existing_attendance.to_dict()
        }), 409
    
    # Get current time
    now = datetime.now()
    
    # Create attendance record
    attendance = Attendance(
        employee_id=employee.id,
        check_in=now,
        status='present'
    )
    
    # Check if late based on schedule
    today_weekday = now.weekday()  # 0=Monday, 6=Sunday
    schedule = WorkSchedule.query.filter_by(
        employee_id=employee.id,
        day_of_week=today_weekday
    ).first()
    
    if schedule:
        scheduled_start = datetime.combine(today, schedule.start_time)
        # If more than 10 minutes late, mark as late
        if now > scheduled_start + timedelta(minutes=10):
            attendance.status = 'late'
            attendance.notes = f'Llegada tardía. Hora programada: {schedule.start_time.strftime("%H:%M")}'
    
    try:
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'message': 'Entrada registrada exitosamente',
            'attendance': attendance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al registrar entrada', 'error': str(e)}), 500

@attendance_bp.route('/check-out', methods=['POST'])
@jwt_required()
def check_out():
    # Get current user
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    # Get employee associated with user
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    
    if not employee or not employee.is_active():
        return jsonify({'message': 'No autorizado', 'error': 'Empleado no encontrado o inactivo'}), 403
    
    # Find today's attendance record
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    attendance = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.check_in >= today_start,
        Attendance.check_in <= today_end
    ).first()
    
    if not attendance:
        return jsonify({'message': 'Error', 'error': 'No has registrado entrada hoy'}), 404
    
    if attendance.is_checked_out():
        return jsonify({'message': 'Ya has registrado salida hoy', 'attendance': attendance.to_dict()}), 409
    
    # Get current time
    now = datetime.now()
    
    # Update attendance record
    attendance.check_out = now
    
    # Check if early departure based on schedule
    today_weekday = now.weekday()  # 0=Monday, 6=Sunday
    schedule = WorkSchedule.query.filter_by(
        employee_id=employee.id,
        day_of_week=today_weekday
    ).first()
    
    if schedule:
        scheduled_end = datetime.combine(today, schedule.end_time)
        # If more than 10 minutes early, note early departure
        if now < scheduled_end - timedelta(minutes=10):
            attendance.notes = (attendance.notes or '') + '\nSalida temprana. '
            attendance.notes += f'Hora programada: {schedule.end_time.strftime("%H:%M")}'
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Salida registrada exitosamente',
            'attendance': attendance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al registrar salida', 'error': str(e)}), 500

@attendance_bp.route('/employee/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee_attendance(employee_id):
    # Check if user is admin or the employee themselves
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    # Only admins or the employee themselves can view attendance
    if not current_user.is_admin() and current_user.id != employee.user_id:
        return jsonify({'message': 'No autorizado', 'error': 'No tiene permisos para ver esta asistencia'}), 403
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = Attendance.query.filter_by(employee_id=employee.id)
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Attendance.check_in >= start)
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = datetime.combine(end, datetime.max.time())
        query = query.filter(Attendance.check_in <= end)
    
    # Execute query with pagination
    attendance_records = query.order_by(Attendance.check_in.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    result = {
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'attendance_records': [record.to_dict() for record in attendance_records.items],
        'total': attendance_records.total,
        'pages': attendance_records.pages,
        'current_page': attendance_records.page
    }
    
    return jsonify(result), 200

@attendance_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_attendance():
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    # Get today's date range
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Get all attendance records for today
    attendance_records = Attendance.query.filter(
        Attendance.check_in >= today_start,
        Attendance.check_in <= today_end
    ).all()
    
    # Get all active employees
    active_employees = Employee.query.filter_by(status='active').all()
    
    # Create a dictionary of employee_id -> attendance record
    attendance_dict = {record.employee_id: record for record in attendance_records}
    
    # Create result with attendance status for all employees
    result = []
    for employee in active_employees:
        attendance = attendance_dict.get(employee.id)
        result.append({
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'department': employee.department,
            'position': employee.position,
            'present': attendance is not None,
            'check_in': attendance.check_in.isoformat() if attendance and attendance.check_in else None,
            'check_out': attendance.check_out.isoformat() if attendance and attendance.check_out else None,
            'status': attendance.status if attendance else 'absent'
        })
    
    return jsonify({
        'date': today.isoformat(),
        'total_employees': len(active_employees),
        'present': len(attendance_records),
        'absent': len(active_employees) - len(attendance_records),
        'attendance': result
    }), 200

@attendance_bp.route('/my-status', methods=['GET'])
@jwt_required()
def get_my_attendance_status():
    # Get current user
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    # Get employee associated with user
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    
    if not employee or not employee.is_active():
        return jsonify({'message': 'No autorizado', 'error': 'Empleado no encontrado o inactivo'}), 403
    
    # Get today's date range
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Find today's attendance record
    attendance = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.check_in >= today_start,
        Attendance.check_in <= today_end
    ).first()
    
    # Get today's schedule
    today_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
    schedule = WorkSchedule.query.filter_by(
        employee_id=employee.id,
        day_of_week=today_weekday
    ).first()
    
    result = {
        'date': today.isoformat(),
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'checked_in': attendance is not None,
        'checked_out': attendance.is_checked_out() if attendance else False,
        'attendance': attendance.to_dict() if attendance else None,
        'scheduled_today': schedule is not None,
        'schedule': schedule.to_dict() if schedule else None
    }
    
    return jsonify(result), 200

@attendance_bp.route('/<int:attendance_id>', methods=['PUT'])
@jwt_required()
def update_attendance(attendance_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    attendance = Attendance.query.get(attendance_id)
    
    if not attendance:
        return jsonify({'message': 'Registro no encontrado', 'error': 'El registro de asistencia no existe'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Datos incompletos', 'error': 'No se proporcionaron datos para actualizar'}), 400
    
    try:
        # Update attendance fields
        if 'check_in' in data:
            attendance.check_in = datetime.fromisoformat(data['check_in'])
        if 'check_out' in data:
            attendance.check_out = datetime.fromisoformat(data['check_out']) if data['check_out'] else None
        if 'status' in data:
            attendance.status = data['status']
        if 'notes' in data:
            attendance.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Registro actualizado exitosamente',
            'attendance': attendance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar registro', 'error': str(e)}), 500