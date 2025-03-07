import axios from 'axios';
import teamService from '../teamService';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Team Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch all teams', async () => {
    const teams = [
      { id: 1, name: 'Development Team', department: 'IT' },
      { id: 2, name: 'Marketing Team', department: 'Marketing' }
    ];
    
    mockedAxios.get.mockResolvedValueOnce({ data: { teams } });
    
    const result = await teamService.getAllTeams();
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/teams/');
    expect(result).toEqual(teams);
  });

  it('should fetch a team by ID with members', async () => {
    const team = {
      id: 1,
      name: 'Development Team',
      department: 'IT',
      members: [
        {
          id: 1,
          team_id: 1,
          employee_id: 101,
          role: 'leader',
          employee: {
            id: 101,
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com'
          }
        }
      ]
    };
    
    mockedAxios.get.mockResolvedValueOnce({ data: { team } });
    
    const result = await teamService.getTeamById(1);
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/teams/1');
    expect(result).toEqual(team);
  });

  it('should create a new team', async () => {
    const newTeam = {
      name: 'New Team',
      description: 'A new team',
      department: 'HR'
    };
    
    const members = [
      { employee_id: 101, role: 'leader' },
      { employee_id: 102, role: 'member' }
    ];
    
    const createdTeam = {
      id: 3,
      ...newTeam
    };
    
    mockedAxios.post.mockResolvedValueOnce({ data: { team: createdTeam } });
    
    const result = await teamService.createTeam(newTeam, members);
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/teams/', {
      ...newTeam,
      members
    });
    expect(result).toEqual(createdTeam);
  });

  it('should update a team', async () => {
    const teamId = 1;
    const updateData = {
      name: 'Updated Team Name',
      department: 'Updated Department'
    };
    
    const updatedTeam = {
      id: teamId,
      ...updateData,
      description: 'Original description'
    };
    
    mockedAxios.put.mockResolvedValueOnce({ data: { team: updatedTeam } });
    
    const result = await teamService.updateTeam(teamId, updateData);
    
    expect(mockedAxios.put).toHaveBeenCalledWith(`/teams/${teamId}`, updateData);
    expect(result).toEqual(updatedTeam);
  });

  it('should delete a team', async () => {
    const teamId = 1;
    
    mockedAxios.delete.mockResolvedValueOnce({});
    
    await teamService.deleteTeam(teamId);
    
    expect(mockedAxios.delete).toHaveBeenCalledWith(`/teams/${teamId}`);
  });

  it('should add a member to a team', async () => {
    const teamId = 1;
    const employeeId = 101;
    const role = 'leader';
    
    const newMember = {
      id: 5,
      team_id: teamId,
      employee_id: employeeId,
      role
    };
    
    mockedAxios.post.mockResolvedValueOnce({ data: { team_member: newMember } });
    
    const result = await teamService.addTeamMember(teamId, employeeId, role);
    
    expect(mockedAxios.post).toHaveBeenCalledWith(`/teams/${teamId}/members`, {
      employee_id: employeeId,
      role
    });
    expect(result).toEqual(newMember);
  });

  it('should remove a member from a team', async () => {
    const teamId = 1;
    const memberId = 5;
    
    mockedAxios.delete.mockResolvedValueOnce({});
    
    await teamService.removeTeamMember(teamId, memberId);
    
    expect(mockedAxios.delete).toHaveBeenCalledWith(`/teams/${teamId}/members/${memberId}`);
  });

  it('should update a team member role', async () => {
    const teamId = 1;
    const memberId = 5;
    const newRole = 'member';
    
    const updatedMember = {
      id: memberId,
      team_id: teamId,
      employee_id: 101,
      role: newRole
    };
    
    mockedAxios.put.mockResolvedValueOnce({ data: { team_member: updatedMember } });
    
    const result = await teamService.updateTeamMemberRole(teamId, memberId, newRole);
    
    expect(mockedAxios.put).toHaveBeenCalledWith(`/teams/${teamId}/members/${memberId}`, {
      role: newRole
    });
    expect(result).toEqual(updatedMember);
  });
});