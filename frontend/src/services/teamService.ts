import api from './api';

export interface Team {
  id?: number;
  name: string;
  description?: string;
  department?: string;
  status?: string;
  created_at?: string;
}

export interface TeamMember {
  id?: number;
  team_id: number;
  employee_id: number;
  role?: string;
  joined_at?: string;
  employee?: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    position?: string;
    department?: string;
  };
}

export interface TeamWithMembers extends Team {
  members?: TeamMember[];
}

const teamService = {
  // Get all teams
  getAllTeams: async (): Promise<Team[]> => {
    const response = await api.get('/teams/');
    return response.data.teams;
  },

  // Get team by ID
  getTeamById: async (id: number): Promise<TeamWithMembers> => {
    const response = await api.get(`/teams/${id}`);
    return response.data.team;
  },

  // Create new team
  createTeam: async (teamData: Team, members?: {employee_id: number, role?: string}[]): Promise<Team> => {
    const payload = {
      ...teamData,
      members: members || []
    };
    const response = await api.post('/teams/', payload);
    return response.data.team;
  },

  // Update team
  updateTeam: async (id: number, teamData: Partial<Team>): Promise<Team> => {
    const response = await api.put(`/teams/${id}`, teamData);
    return response.data.team;
  },

  // Delete team
  deleteTeam: async (id: number): Promise<void> => {
    await api.delete(`/teams/${id}`);
  },

  // Add member to team
  addTeamMember: async (teamId: number, employeeId: number, role: string = 'member'): Promise<TeamMember> => {
    const response = await api.post(`/teams/${teamId}/members`, { employee_id: employeeId, role });
    return response.data.team_member;
  },

  // Remove member from team
  removeTeamMember: async (teamId: number, memberId: number): Promise<void> => {
    await api.delete(`/teams/${teamId}/members/${memberId}`);
  },

  // Update team member role
  updateTeamMemberRole: async (teamId: number, memberId: number, role: string): Promise<TeamMember> => {
    const response = await api.put(`/teams/${teamId}/members/${memberId}`, { role });
    return response.data.team_member;
  }
};

export default teamService;