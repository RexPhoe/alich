import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Grid,
  Tab,
  Tabs,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { ExitToApp, Add } from '@mui/icons-material';
import axios from 'axios';
import { useLanguage } from '../../contexts/LanguageContext';
import UserForm from './UserForm';
import TeamList from './TeamList';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [employees, setEmployees] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [isUserFormOpen, setIsUserFormOpen] = useState(false);
  const [teamsLoaded, setTeamsLoaded] = useState(false);

  useEffect(() => {
    // Check if user is logged in and is admin
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    
    if (!storedUser || !token) {
      navigate('/login');
      return;
    }

    const user = JSON.parse(storedUser);
    if (user.role !== 'admin') {
      navigate('/employee/dashboard');
      return;
    }

    fetchEmployees(token);
  }, [navigate]);

  const fetchEmployees = async (token: string) => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5001/api/employees/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmployees(response.data.employees);
      setError('');
    } catch (err: any) {
      console.error('Error fetching employees:', err);
      setError(err.response?.data?.message || 'Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const employeeColumns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'first_name', headerName: t('admin.employees.name'), width: 130 },
    { field: 'last_name', headerName: t('admin.employees.name'), width: 130 },
    { field: 'email', headerName: t('admin.employees.email'), width: 200 },
    { field: 'department', headerName: t('admin.employees.department'), width: 130 },
    { field: 'position', headerName: t('admin.employees.position'), width: 130 },
    { field: 'status', headerName: t('admin.employees.status'), width: 100 }
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const handleAddUser = () => {
    setIsUserFormOpen(true);
  };

  const handleUserFormClose = () => {
    setIsUserFormOpen(false);
  };

  const handleUserFormSuccess = () => {
    fetchEmployees(localStorage.getItem('token') || '');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('admin.dashboard.title')}
        </Typography>
        <Button
          variant="outlined"
          color="secondary"
          startIcon={<ExitToApp />}
          onClick={handleLogout}
        >
          {t('common.logout')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="admin tabs">
          <Tab label={t('admin.dashboard.employees')} />
          <Tab label={t('admin.dashboard.schedules')} />
          <Tab label={t('admin.dashboard.teams')} />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">{t('admin.employees.title')}</Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<Add />}
              onClick={handleAddUser}
            >
              {t('admin.employees.add')}
            </Button>
          </Box>
          <div style={{ height: 400, width: '100%' }}>
            <DataGrid
              rows={employees}
              columns={employeeColumns}
              pageSize={5}
              rowsPerPageOptions={[5]}
              checkboxSelection
              disableSelectionOnClick
            />
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">{t('admin.schedules.title')}</Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<Add />}
              onClick={() => {}}
            >
              {t('admin.schedules.add')}
            </Button>
          </Box>
          {/* Schedule management will be implemented in the next phase */}
          <Typography variant="body1">
            Work schedule management coming soon...
          </Typography>
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <TeamList />
        </TabPanel>
      </Paper>

      <UserForm
        open={isUserFormOpen}
        onClose={handleUserFormClose}
        onSuccess={handleUserFormSuccess}
      />
    </Container>
  );
};

export default AdminDashboard;