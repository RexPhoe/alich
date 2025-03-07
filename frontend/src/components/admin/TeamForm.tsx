import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  Chip,
  Autocomplete,
} from '@mui/material';
import { useLanguage } from '../../contexts/LanguageContext';
import teamService, { Team } from '../../services/teamService';
import axios from 'axios';

interface TeamFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  team?: Team;
}

interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  department?: string;
  position?: string;
}

interface TeamMemberInput {
  employee_id: number;
  role: string;
  employee?: Employee;
}

const TeamForm = ({ open, onClose, onSuccess, team }: TeamFormProps) => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedMembers, setSelectedMembers] = useState<TeamMemberInput[]>([]);
  const [formData, setFormData] = useState<Team>({
    name: '',
    description: '',
    department: '',
  });

  useEffect(() => {
    // If team is provided, we're in edit mode
    if (team) {
      setFormData({
        name: team.name,
        description: team.description || '',
        department: team.department || '',
      });
    } else {
      // Reset form for create mode
      setFormData({
        name: '',
        description: '',
        department: '',
      });
    }
    
    // Reset selected members
    setSelectedMembers([]);
    
    // Fetch employees for member selection
    fetchEmployees();
  }, [team, open]);

  const fetchEmployees = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5001/api/employees/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmployees(response.data.employees);
    } catch (err: any) {
      console.error('Error fetching employees:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name as string]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (team?.id) {
        // Update existing team
        await teamService.updateTeam(team.id, formData);
        
        // Handle team members updates if needed
        // This would require additional API calls to add/remove members
      } else {
        // Create new team with members
        await teamService.createTeam(formData, selectedMembers);
      }
      
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save team');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = (employee: Employee | null, role: string = 'member') => {
    if (!employee) return;
    
    // Check if employee is already added
    if (selectedMembers.some(member => member.employee_id === employee.id)) {
      return;
    }
    
    setSelectedMembers(prev => [
      ...prev,
      {
        employee_id: employee.id,
        role,
        employee
      }
    ]);
  };

  const handleRemoveMember = (employeeId: number) => {
    setSelectedMembers(prev => prev.filter(member => member.employee_id !== employeeId));
  };

  const handleMemberRoleChange = (employeeId: number, role: string) => {
    setSelectedMembers(prev => prev.map(member => 
      member.employee_id === employeeId ? { ...member, role } : member
    ));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{team ? t('admin.teams.edit') : t('admin.teams.add')}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                name="name"
                label={t('admin.teams.name')}
                value={formData.name}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="description"
                label={t('admin.teams.description')}
                value={formData.description}
                onChange={handleChange}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="department"
                label={t('admin.teams.department')}
                value={formData.department}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ mt: 2, mb: 1 }}>
                <InputLabel>{t('admin.teams.members')}</InputLabel>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={8}>
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
                    onChange={(_, value) => handleAddMember(value)}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={() => {
                      const autocompleteInput = document.querySelector('input[id^="mui-"]') as HTMLInputElement;
                      if (autocompleteInput) {
                        autocompleteInput.value = '';
                      }
                    }}
                  >
                    {t('admin.teams.clearSelection')}
                  </Button>
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 2 }}>
                {selectedMembers.map((member) => (
                  <Box key={member.employee_id} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Chip 
                      label={`${member.employee?.first_name} ${member.employee?.last_name}`}
                      onDelete={() => handleRemoveMember(member.employee_id)}
                      sx={{ mr: 1 }}
                    />
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                      <Select
                        value={member.role}
                        onChange={(e) => handleMemberRoleChange(member.employee_id, e.target.value as string)}
                      >
                        <MenuItem value="member">{t('admin.teams.roleMember')}</MenuItem>
                        <MenuItem value="leader">{t('admin.teams.roleLeader')}</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                ))}
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>{t('common.cancel')}</Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? t('common.saving') : t('common.save')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default TeamForm;