import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@mui/material';
import { Save, Cancel } from '@mui/icons-material';
import axios from 'axios';
import { useLanguage } from '../../contexts/LanguageContext';

interface ScheduleFormProps {
  open: boolean;
  onClose: () => void;
  employeeId: number;
  scheduleId?: number; // Optional for edit mode
  onSave: () => void;
}

const daysOfWeek = [
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' },
  { value: 0, label: 'Sunday' },
];

const ScheduleForm: React.FC<ScheduleFormProps> = ({ open, onClose, employeeId, scheduleId, onSave }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    day_of_week: 1,
    start_time: '09:00',
    end_time: '17:00',
  });

  const isEditMode = !!scheduleId;

  useEffect(() => {
    // If in edit mode, fetch schedule data
    if (isEditMode && open) {
      fetchScheduleData();
    } else {
      // Reset form for new schedule
      setFormData({
        day_of_week: 1,
        start_time: '09:00',
        end_time: '17:00',
      });
    }
  }, [scheduleId, open]);

  const fetchScheduleData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5001/api/employees/${employeeId}/schedules/${scheduleId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Map API response to form data
      const schedule = response.data;
      setFormData({
        day_of_week: schedule.day_of_week,
        start_time: schedule.start_time,
        end_time: schedule.end_time,
      });
      setError('');
    } catch (err: any) {
      console.error('Error fetching schedule:', err);
      setError(err.response?.data?.message || 'Failed to load schedule data');
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
        // Update existing schedule
        await axios.put(
          `http://localhost:5001/api/employees/${employeeId}/schedules/${scheduleId}`,
          formData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        // Create new schedule
        await axios.post(
          `http://localhost:5001/api/employees/${employeeId}/schedules`,
          formData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }
      
      onSave(); // Notify parent component
      onClose(); // Close dialog
    } catch (err: any) {
      console.error('Error saving schedule:', err);
      setError(err.response?.data?.message || 'Failed to save schedule data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {isEditMode ? t('admin.schedules.edit') : t('admin.schedules.add')}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth margin="normal">
                <InputLabel id="day-of-week-label">{t('admin.schedules.dayOfWeek')}</InputLabel>
                <Select
                  labelId="day-of-week-label"
                  id="day_of_week"
                  name="day_of_week"
                  value={formData.day_of_week}
                  label={t('admin.schedules.dayOfWeek')}
                  onChange={handleChange}
                  disabled={loading}
                >
                  {daysOfWeek.map((day) => (
                    <MenuItem key={day.value} value={day.value}>
                      {t(`days.${day.label.toLowerCase()}`)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="start_time"
                label={t('admin.schedules.startTime')}
                name="start_time"
                type="time"
                value={formData.start_time}
                onChange={handleChange}
                disabled={loading}
                InputLabelProps={{ shrink: true }}
                inputProps={{ step: 300 }} // 5 min steps
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="end_time"
                label={t('admin.schedules.endTime')}
                name="end_time"
                type="time"
                value={formData.end_time}
                onChange={handleChange}
                disabled={loading}
                InputLabelProps={{ shrink: true }}
                inputProps={{ step: 300 }} // 5 min steps
              />
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

export default ScheduleForm;