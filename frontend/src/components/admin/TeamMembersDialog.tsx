import { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Autocomplete,
  TextField,
  Grid,
} from '@mui/material';
import { Delete, Edit, Save, Cancel } from '@mui/icons-material';
import { useLanguage } from '../../contexts/LanguageContext';
import teamService, { TeamWithMembers, TeamMember } from '../../services/teamService';
import axios from 'axios';

interface TeamMembersDialogProps {
  open: boolean;
  onClose: () => void;
  team: TeamWithMembers;
  onMemberUpdate: () => void;
}

interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  department?: string;
  position?: string;
}

const TeamMembersDialog = ({ open, onClose, team, onMemberUpdate }: TeamMembersDialogProps) => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [selectedRole, setSelectedRole] = useState('member');
  const [editingMember, setEditingMember] = useState<TeamMember | null>(null);
  const [editRole, setEditRole] = useState('');

  // Fetch employees when dialog opens
  useState(() => {
    if (open) {
      fetchEmployees();
    }
  });

  const fetchEmployees = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5001/api/employees/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Filter out employees who are already team members
      const teamMemberIds = team.members?.map(member => member.employee_id) || [];
      const availableEmployees = response.data.employees.filter(
        (emp: Employee) => !teamMemberIds.includes(emp.id)
      );
      
      setEmployees(availableEmployees);
    } catch (err: any) {
      console.error('Error fetching employees:', err);
      setError(err.response?.data?.message || 'Failed to load employees');
    }
  };

  const handleAddMember = async () => {
    if (!selectedEmployee) return;
    
    setLoading(true);
    setError('');
    
    try {
      await teamService.addTeamMember(team.id!, selectedEmployee.id, selectedRole);
      setSelectedEmployee(null);
      setSelectedRole('member');
      onMemberUpdate();
      
      // Clear the autocomplete input
      const autocompleteInput = document.querySelector('input[id^="mui-"]') as HTMLInputElement;
      if (autocompleteInput) {
        autocompleteInput.value = '';
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to add team member');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: number) => {
    setLoading(true);
    setError('');
    
    try {
      await teamService.removeTeamMember(team.id!, memberId);
      onMemberUpdate();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to remove team member');
    } finally {
      setLoading(false);
    }
  };

  const startEditRole = (member: TeamMember) => {
    setEditingMember(member);
    setEditRole(member.role || 'member');
  };

  const cancelEditRole = () => {
    setEditingMember(null);
  };

  const saveEditRole = async () => {
    if (!editingMember) return;
    
    setLoading(true);
    setError('');
    
    try {
      await teamService.updateTeamMemberRole(team.id!, editingMember.id!, editRole);
      setEditingMember(null);
      onMemberUpdate();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update role');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {t('admin.teams.membersDialogTitle', { name: team.name })}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Typography variant="h6" sx={{ mb: 2 }}>
          {t('admin.teams.addMember')}
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6}>
            <Autocomplete
              options={employees}
              getOptionLabel={(option) => `${option.first_name} ${option.last_name}`}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={t('admin.teams.selectEmployee')}
                  variant="outlined"
                />
              )}
              onChange={(_, value) => setSelectedEmployee(value)}
              value={selectedEmployee}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel>{t('admin.teams.role')}</InputLabel>
              <Select
                value={selectedRole}
                label={t('admin.teams.role')}
                onChange={(e) => setSelectedRole(e.target.value as string)}
              >
                <MenuItem value="member">{t('admin.teams.roleMember')}</MenuItem>
                <MenuItem value="leader">{t('admin.teams.roleLeader')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              disabled={!selectedEmployee || loading}
              onClick={handleAddMember}
            >
              {t('admin.teams.addButton')}
            </Button>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="h6" sx={{ mb: 2 }}>
          {t('admin.teams.currentMembers')}
        </Typography>
        
        {team.members && team.members.length > 0 ? (
          <List>
            {team.members.map((member) => (
              <ListItem key={member.id}>
                <ListItemText
                  primary={`${member.employee?.first_name} ${member.employee?.last_name}`}
                  secondary={member.employee?.email}
                />
                
                <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
                  {editingMember?.id === member.id ? (
                    <>
                      <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
                        <Select
                          value={editRole}
                          onChange={(e) => setEditRole(e.target.value as string)}
                          size="small"
                        >
                          <MenuItem value="member">{t('admin.teams.roleMember')}</MenuItem>
                          <MenuItem value="leader">{t('admin.teams.roleLeader')}</MenuItem>
                        </Select>
                      </FormControl>
                      <IconButton onClick={saveEditRole} size="small" color="primary">
                        <Save fontSize="small" />
                      </IconButton>
                      <IconButton onClick={cancelEditRole} size="small">
                        <Cancel fontSize="small" />
                      </IconButton>
                    </>
                  ) : (
                    <>
                      <Typography variant="body2" sx={{ mr: 2 }}>
                        {member.role === 'leader' ? t('admin.teams.roleLeader') : t('admin.teams.roleMember')}
                      </Typography>
                      <IconButton onClick={() => startEditRole(member)} size="small">
                        <Edit fontSize="small" />
                      </IconButton>
                    </>
                  )}
                  <IconButton 
                    onClick={() => handleRemoveMember(member.id!)}
                    size="small"
                    color="error"
                    disabled={loading}
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </Box>
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1">
            {t('admin.teams.noMembers')}
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>
          {t('common.close')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TeamMembersDialog;