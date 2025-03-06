import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Grid,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Save, Cancel } from '@mui/icons-material';
import axios from 'axios';
import { useLanguage } from '../../contexts/LanguageContext';

interface EmployeeFormProps {
  open: boolean;
  onClose: () => void;
  employeeId?: number; // Optional for edit mode
  onSave: () => void;
}

const EmployeeForm: React.FC<EmployeeFormProps> = ({ open, onClose, employeeId, onSave }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'employee',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
  });

  const isEditMode = !!employeeId;

  useEffect(() => {
    // If in edit mode, fetch employee data
    if (isEditMode && open) {
      fetchEmployeeData();
    } else {
      // Reset form for new employee
      setFormData({
        username: '',
        password: '',
        role: 'employee',
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        department: '',
        position: '',
      });
    }
  }, [employeeId, open]);

  const fetchEmployeeData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5001/api/employees/${employeeId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Map API response to form data
      const employee = response.data;
      setFormData({
        username: employee.username || '',
        password: '', // Don't populate password for security reasons
        role: employee.role || 'employee',
        first_name: employee.first_name || '',
        last_name: employee.last_name || '',
        email: employee.email || '',
        phone: employee.phone || '',
        department: employee.department || '',
        position: employee.position || '',
      });
      setError('');
    } catch (err: any) {
      console.error('Error fetching employee:', err);
      setError(err.response?.data?.message || 'Failed to load employee data');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name as string]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      if (isEditMode) {
        // Update existing employee
        await axios.put(
          `http://localhost:5001/api/employees/${employeeId}`,
          formData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        // Create new employee
        await axios.post(
          'http://localhost:5001/api/auth/register',
          formData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }
      
      onSave(); // Notify parent component
      onClose(); // Close dialog
    } catch (err: any) {
      console.error('Error saving employee:', err);
      setError(err.response?.data?.message || 'Failed to save employee data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {isEditMode ? t('admin.employees.edit') : t('admin.employees.add')}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="first_name"
                label={t('admin.employees.name')}
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="last_name"
                label={t('admin.employees.name')}
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label={t('auth.username')}
                name="username"
                value={formData.username}
                onChange={handleChange}
                disabled={loading || isEditMode} // Username can't be changed in edit mode
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required={!isEditMode} // Password is required only for new employees
                fullWidth
                id="password"
                label={t('auth.password')}
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                helperText={isEditMode ? 'Leave blank to keep current password' : ''}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label={t('admin.employees.email')}
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                fullWidth
                id="phone"
                label={t('employee.info.phone')}
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                fullWidth
                id="department"
                label={t('admin.employees.department')}
                name="department"
                value={formData.department}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                fullWidth
                id="position"
                label={t('admin.employees.position')}
                name="position"
                value={formData.position}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel id="role-label">{t('admin.employees.role')}</InputLabel>
                <Select
                  labelId="role-label"
                  id="role"
                  name="role"
                  value={formData.role}
                  label={t('admin.employees.role')}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <MenuItem value="employee">Employee</MenuItem>
                  <MenuItem value="admin">Administrator</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button 
          onClick={onClose} 
          startIcon={<Cancel />}
          disabled={loading}
        >
          {t('common.cancel')}
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          color="primary" 
          startIcon={<Save />}
          disabled={loading}
        >
          {loading ? t('common.saving') : t('common.save')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EmployeeForm;