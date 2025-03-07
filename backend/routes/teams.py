from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging
from models.user import User, db
from models.employee import Employee
from models.team import Team
from models.team_member import TeamMember

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/', methods=['GET'])
@jwt_required()
def get_teams():
    try:
        # Log request details
        logger.info('GET /api/teams - Fetching teams list')
        logger.info(f'Request args: {request.args}')
        
        # Check if user is admin
        current_user_id = get_jwt_identity()
        logger.info(f'User ID: {current_user_id} attempting to access teams list')
        
        current_user = User.query.get(current_user_id)
        if not current_user:
            logger.error(f'User not found for ID: {current_user_id}')
            return jsonify({'message': 'No autorizado', 'error': 'Usuario no encontrado'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        department = request.args.get('department')
        status = request.args.get('status')
        search = request.args.get('search')
        
        logger.info(f'Query params - page: {page}, per_page: {per_page}, department: {department}, status: {status}, search: {search}')
        
        # Build query
        query = Team.query
        
        if department:
            query = query.filter(Team.department == department)
            logger.debug(f'Filtering by department: {department}')
        
        if status:
            query = query.filter(Team.status == status)
            logger.debug(f'Filtering by status: {status}')
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(Team.name.ilike(search_term))
            logger.debug(f'Filtering by search term: {search}')
        
        # Execute query with pagination
        teams = query.order_by(Team.name).paginate(page=page, per_page=per_page)
        logger.info(f'Query executed, found {teams.total} total teams')
        
        # Format response
        result = {
            'teams': [team.to_dict() for team in teams.items],
            'total': teams.total,
            'pages': teams.pages,
            'current_page': teams.page
        }
        
        logger.info(f'Successfully fetched {len(teams.items)} teams for page {page}')
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Error fetching teams: {str(e)}')
        logger.exception('Full traceback:')
        return jsonify({'message': 'Error al obtener equipos', 'error': str(e)}), 500

@teams_bp.route('/', methods=['POST'])
@jwt_required()
def create_team():
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Datos incompletos', 'error': 'Se requiere al menos el nombre del equipo'}), 400
    
    # Check if team name already exists
    if Team.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Error de creación', 'error': 'El nombre del equipo ya existe'}), 409
    
    try:
        # Create team
        team = Team(
            name=data['name'],
            description=data.get('description'),
            department=data.get('department')
        )
        db.session.add(team)
        db.session.commit()
        
        # Add members if provided
        if 'members' in data and isinstance(data['members'], list):
            for member_data in data['members']:
                employee_id = member_data.get('employee_id')
                role = member_data.get('role', 'member')
                
                if employee_id and Employee.query.get(employee_id):
                    team_member = TeamMember(
                        team_id=team.id,
                        employee_id=employee_id,
                        role=role
                    )
                    db.session.add(team_member)
            
            db.session.commit()
        
        return jsonify({
            'message': 'Equipo creado exitosamente',
            'team': team.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear equipo', 'error': str(e)}), 500

@teams_bp.route('/<int:team_id>', methods=['GET'])
@jwt_required()
def get_team(team_id):
    # Get current user
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'message': 'Equipo no encontrado', 'error': 'El equipo no existe'}), 404
    
    # Get team members
    team_members = TeamMember.query.filter_by(team_id=team.id).all()
    members_data = []
    
    for member in team_members:
        employee = Employee.query.get(member.employee_id)
        if employee:
            member_data = member.to_dict()
            member_data['employee'] = {
                'id': employee.id,
                'name': employee.full_name,
                'position': employee.position,
                'department': employee.department
            }
            members_data.append(member_data)
    
    # Combine team data with members
    team_data = team.to_dict()
    team_data['members'] = members_data
    
    return jsonify(team_data), 200

@teams_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'message': 'Equipo no encontrado', 'error': 'El equipo no existe'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Datos incompletos', 'error': 'No se proporcionaron datos para actualizar'}), 400
    
    try:
        # Update team fields
        if 'name' in data and data['name'] != team.name:
            # Check if name already exists
            existing_name = Team.query.filter(Team.name == data['name'], Team.id != team.id).first()
            if existing_name:
                return jsonify({'message': 'Error de actualización', 'error': 'El nombre del equipo ya existe'}), 409
            team.name = data['name']
        if 'description' in data:
            team.description = data['description']
        if 'department' in data:
            team.department = data['department']
        if 'status' in data:
            team.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Equipo actualizado exitosamente',
            'team': team.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar equipo', 'error': str(e)}), 500

@teams_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'message': 'Equipo no encontrado', 'error': 'El equipo no existe'}), 404
    
    try:
        # Instead of deleting, mark as inactive
        team.status = 'inactive'
        db.session.commit()
        
        return jsonify({
            'message': 'Equipo desactivado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al desactivar equipo', 'error': str(e)}), 500

@teams_bp.route('/<int:team_id>/members', methods=['GET'])
@jwt_required()
def get_team_members(team_id):
    # Get current user
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'message': 'Equipo no encontrado', 'error': 'El equipo no existe'}), 404
    
    # Get team members with employee details
    team_members = TeamMember.query.filter_by(team_id=team.id).all()
    members_data = []
    
    for member in team_members:
        employee = Employee.query.get(member.employee_id)
        if employee:
            member_data = member.to_dict()
            member_data['employee'] = {
                'id': employee.id,
                'name': employee.full_name,
                'position': employee.position,
                'department': employee.department,
                'email': employee.email
            }
            members_data.append(member_data)
    
    return jsonify({
        'team_id': team.id,
        'team_name': team.name,
        'members': members_data
    }), 200

@teams_bp.route('/<int:team_id>/members', methods=['POST'])
@jwt_required()
def add_team_member(team_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'message': 'Equipo no encontrado', 'error': 'El equipo no existe'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('employee_id'):
        return jsonify({'message': 'Datos incompletos', 'error': 'Se requiere el ID del empleado'}), 400
    
    employee_id = data['employee_id']
    role = data.get('role', 'member')
    
    # Check if employee exists
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    # Check if employee is already a member
    existing_member = TeamMember.query.filter_by(team_id=team.id, employee_id=employee_id).first()
    if existing_member:
        return jsonify({'message': 'Error de adición', 'error': 'El empleado ya es miembro del equipo'}), 409
    
    try:
        # Add employee to team
        team_member = TeamMember(
            team_id=team.id,
            employee_id=employee_id,
            role=role
        )
        db.session.add(team_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Miembro agregado exitosamente',
            'team_member': team_member.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al agregar miembro', 'error': str(e)}), 500

@teams_bp.route('/<int:team_id>/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_team_member(team_id, member_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    team_member = TeamMember.query.get(member_id)
    
    if not team_member or team_member.team_id != team_id:
        return jsonify({'message': 'Miembro no encontrado', 'error': 'El miembro no existe en este equipo'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Datos incompletos', 'error': 'No se proporcionaron datos para actualizar'}), 400
    
    try:
        # Update team member fields
        if 'role' in data:
            team_member.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Miembro actualizado exitosamente',
            'team_member': team_member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar miembro', 'error': str(e)}), 500

@teams_bp.route('/<int:team_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_team_member(team_id, member_id):
    # Check if user is admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin():
        return jsonify({'message': 'No autorizado', 'error': 'Se requieren privilegios de administrador'}), 403
    
    team_member = TeamMember.query.get(member_id)
    
    if not team_member or team_member.team_id != team_id:
        return jsonify({'message': 'Miembro no encontrado', 'error': 'El miembro no existe en este equipo'}), 404
    
    try:
        # Remove member from team
        db.session.delete(team_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Miembro eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar miembro', 'error': str(e)}), 500

@teams_bp.route('/employee/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee_teams(employee_id):
    # Check if user is admin or the employee themselves
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'message': 'No autorizado', 'error': 'Usuario no válido'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'message': 'Empleado no encontrado', 'error': 'El empleado no existe'}), 404
    
    # Only admins or the employee themselves can view teams
    if not current_user.is_admin() and current_user.id != employee.user_id:
        return jsonify({'message': 'No autorizado', 'error': 'No tiene permisos para ver estos equipos'}), 403
    
    # Get teams the employee is a member of
    team_memberships = TeamMember.query.filter_by(employee_id=employee.id).all()
    teams_data = []
    
    for membership in team_memberships:
        team = Team.query.get(membership.team_id)
        if team and team.is_active():
            team_data = team.to_dict()
            team_data['role'] = membership.role
            teams_data.append(team_data)
    
    return jsonify({
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'teams': teams_data
    }), 200