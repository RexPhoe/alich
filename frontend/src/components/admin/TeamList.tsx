import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import { Add, Edit, Delete, Group } from '@mui/icons-material';
import { useLanguage } from '../../contexts/LanguageContext';
import teamService, { Team, TeamWithMembers } from '../../services/teamService';
import TeamForm from './TeamForm';
import TeamMembersDialog from './TeamMembersDialog';

const TeamList = () => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isMembersDialogOpen, setIsMembersDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [teamToDelete, setTeamToDelete] = useState<Team | null>(null);
  const [teamWithMembers, setTeamWithMembers] = useState<TeamWithMembers | null>(null);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const teamsData = await teamService.getAllTeams();
      setTeams(teamsData);
      setError('');
    } catch (err: any) {
      console.error('Error fetching teams:', err);
      setError(err.response?.data?.message || 'Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTeam = () => {
    setSelectedTeam(null);
    setIsFormOpen(true);
  };

  const handleEditTeam = (team: Team) => {
    setSelectedTeam(team);
    setIsFormOpen(true);
  };

  const handleDeleteTeam = (team: Team) => {
    setTeamToDelete(team);
    setIsDeleteDialogOpen(true);
  };

  const confirmDeleteTeam = async () => {
    if (!teamToDelete) return;
    
    try {
      await teamService.deleteTeam(teamToDelete.id!);
      fetchTeams();
      setIsDeleteDialogOpen(false);
      setTeamToDelete(null);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete team');
    }
  };

  const handleViewMembers = async (team: Team) => {
    try {
      const teamData = await teamService.getTeamById(team.id!);
      setTeamWithMembers(teamData);
      setIsMembersDialogOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load team members');
    }
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
  };

  const handleFormSuccess = () => {
    fetchTeams();
  };

  const handleMembersDialogClose = () => {
    setIsMembersDialogOpen(false);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: t('admin.teams.name'), width: 200 },
    { field: 'department', headerName: t('admin.teams.department'), width: 150 },
    { field: 'description', headerName: t('admin.teams.description'), width: 300 },
    { field: 'status', headerName: t('admin.teams.status'), width: 100 },
    {
      field: 'actions',
      headerName: t('common.actions'),
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => {
        const team = params.row as Team;
        return (
          <Box>
            <Tooltip title={t('admin.teams.viewMembers')}>
              <IconButton onClick={() => handleViewMembers(team)} size="small">
                <Group />
              </IconButton>
            </Tooltip>
            <Tooltip title={t('common.edit')}>
              <IconButton onClick={() => handleEditTeam(team)} size="small">
                <Edit />
              </IconButton>
            </Tooltip>
            <Tooltip title={t('common.delete')}>
              <IconButton onClick={() => handleDeleteTeam(team)} size="small">
                <Delete />
              </IconButton>
            </Tooltip>
          </Box>
        );
      },
    },
  ];

  if (loading && teams.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">{t('admin.teams.title')}</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Add />}
          onClick={handleAddTeam}
        >
          {t('admin.teams.add')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <div style={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={teams}
          columns={columns}
          pageSize={5}
          rowsPerPageOptions={[5]}
          disableSelectionOnClick
        />
      </div>

      <TeamForm
        open={isFormOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        team={selectedTeam || undefined}
      />

      {teamWithMembers && (
        <TeamMembersDialog
          open={isMembersDialogOpen}
          onClose={handleMembersDialogClose}
          team={teamWithMembers}
          onMemberUpdate={fetchTeams}
        />
      )}

      <Dialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
      >
        <DialogTitle>{t('admin.teams.deleteConfirmTitle')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('admin.teams.deleteConfirmMessage', { name: teamToDelete?.name })}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>
            {t('common.cancel')}
          </Button>
          <Button onClick={confirmDeleteTeam} color="error" autoFocus>
            {t('common.delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default TeamList;