import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import { AccessTime, EventNote, ExitToApp } from '@mui/icons-material';
import axios from 'axios';

const EmployeeDashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [employee, setEmployee] = useState<any>(null);
  const [attendance, setAttendance] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [checkInLoading, setCheckInLoading] = useState(false);
  const [checkOutLoading, setCheckOutLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    
    if (!storedUser || !token) {
      navigate('/login');
      return;
    }

    setUser(JSON.parse(storedUser));
    fetchEmployeeData(token);
  }, [navigate]);

  const fetchEmployeeData = async (token: string) => {
    try {
      setLoading(true);
      // Get employee data
      const employeeResponse = await axios.get('http://localhost:5001/api/employees/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmployee(employeeResponse.data);

      // Get today's attendance
      const attendanceResponse = await axios.get(
        `http://localhost:5001/api/attendance/today/${employeeResponse.data.id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAttendance(attendanceResponse.data);
      setError('');
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError('Failed to load employee data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    const token = localStorage.getItem('token');
    if (!token || !employee) return;

    try {
      setCheckInLoading(true);
      setMessage('');
      
      const response = await axios.post(
        'http://localhost:5001/api/attendance/check-in',
        { employee_id: employee.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setAttendance(response.data);
      setMessage('Successfully checked in!');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to check in. Please try again.');
    } finally {
      setCheckInLoading(false);
    }
  };

  const handleCheckOut = async () => {
    const token = localStorage.getItem('token');
    if (!token || !employee || !attendance) return;

    try {
      setCheckOutLoading(true);
      setMessage('');
      
      const response = await axios.post(
        `http://localhost:5001/api/attendance/check-out/${attendance.id}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setAttendance(response.data);
      setMessage('Successfully checked out!');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to check out. Please try again.');
    } finally {
      setCheckOutLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Employee Dashboard
        </Typography>
        <Button
          variant="outlined"
          color="secondary"
          startIcon={<ExitToApp />}
          onClick={handleLogout}
        >
          Logout
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Employee Info Card */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Employee Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {employee && (
              <Box>
                <Typography variant="body1">
                  <strong>Name:</strong> {employee.first_name} {employee.last_name}
                </Typography>
                <Typography variant="body1">
                  <strong>Email:</strong> {employee.email}
                </Typography>
                <Typography variant="body1">
                  <strong>Department:</strong> {employee.department || 'Not assigned'}
                </Typography>
                <Typography variant="body1">
                  <strong>Position:</strong> {employee.position || 'Not assigned'}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Attendance Card */}
        <Grid item xs={12} md={8}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Today's Attendance
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Date:</strong> {new Date().toLocaleDateString()}
                  </Typography>
                  {attendance && (
                    <>
                      <Typography variant="body1">
                        <strong>Check-in:</strong> {attendance.check_in ? new Date(attendance.check_in).toLocaleTimeString() : 'Not checked in'}
                      </Typography>
                      <Typography variant="body1">
                        <strong>Check-out:</strong> {attendance.check_out ? new Date(attendance.check_out).toLocaleTimeString() : 'Not checked out'}
                      </Typography>
                      {attendance.check_in && attendance.check_out && (
                        <Typography variant="body1">
                          <strong>Duration:</strong> {attendance.duration || 'N/A'}
                        </Typography>
                      )}
                    </>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'center' }}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      {!attendance ? 'You have not checked in today.' : 
                       !attendance.check_out ? 'You are currently checked in.' : 
                       'You have completed your shift for today.'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
            <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AccessTime />}
                onClick={handleCheckIn}
                disabled={checkInLoading || (attendance && attendance.check_in) || checkOutLoading}
              >
                {checkInLoading ? 'Checking in...' : 'Check In'}
              </Button>
              <Button
                variant="contained"
                color="secondary"
                startIcon={<EventNote />}
                onClick={handleCheckOut}
                disabled={checkOutLoading || !attendance || !attendance.check_in || attendance.check_out}
                sx={{ ml: 2 }}
              >
                {checkOutLoading ? 'Checking out...' : 'Check Out'}
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EmployeeDashboard;