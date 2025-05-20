import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';

const Sessions = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success',
  });
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);

  // Colonnes pour le tableau DataGrid
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'session_id', headerName: 'Session ID', width: 200 },
    { field: 'phone_number', headerName: 'Numéro de téléphone', width: 150 },
    { field: 'current_menu', headerName: 'Menu actuel', width: 150 },
    {
      field: 'started_at',
      headerName: 'Début',
      width: 180,
      valueFormatter: (params) => new Date(params.value).toLocaleString(),
    },
    {
      field: 'last_activity',
      headerName: 'Dernière activité',
      width: 180,
      valueFormatter: (params) => new Date(params.value).toLocaleString(),
    },
    {
      field: 'is_active',
      headerName: 'Statut',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Terminée'}
          color={params.value ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <IconButton color="primary" onClick={() => handleViewSession(params.row)}>
            <VisibilityIcon />
          </IconButton>
          {params.row.is_active && (
            <IconButton color="error" onClick={() => handleEndSession(params.row.id)}>
              <CloseIcon />
            </IconButton>
          )}
        </Box>
      ),
    },
  ];

  // Récupérer la liste des sessions
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      // Dans un environnement réel, vous feriez un appel API ici
      const response = await axios.get('/api/ussd/sessions', {
        headers: {
          'X-API-Key': localStorage.getItem('apiKey') || 'your_secure_api_key_change_me',
        },
      });
      setSessions(response.data?.sessions || []);
      setLoading(false);
    } catch (err) {
      console.error('Erreur lors de la récupération des sessions:', err);
      // Pour l'exemple, nous allons utiliser des données fictives
      const mockSessions = [
        {
          id: 1,
          session_id: 'sess_123456789',
          user_id: 1,
          phone_number: '+123456789',
          current_menu: 'main',
          started_at: '2023-01-01T10:00:00Z',
          last_activity: '2023-01-01T10:05:00Z',
          is_active: true,
        },
        {
          id: 2,
          session_id: 'sess_987654321',
          user_id: 2,
          phone_number: '+987654321',
          current_menu: 'services',
          started_at: '2023-01-01T09:30:00Z',
          last_activity: '2023-01-01T09:35:00Z',
          is_active: false,
          ended_at: '2023-01-01T09:35:00Z',
        },
      ];
      setSessions(mockSessions);
      setError('Impossible de charger les sessions. Utilisation de données de démonstration.');
      setLoading(false);
    }
  };

  // Gérer l'affichage des détails d'une session
  const handleViewSession = (session) => {
    setSelectedSession(session);
    setOpenDialog(true);
  };

  // Gérer la fermeture du dialogue
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  // Gérer la terminaison d'une session
  const handleEndSession = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir terminer cette session ?')) {
      try {
        // Dans un environnement réel, vous feriez un appel API ici
        // Simulation pour l'exemple
        const updatedSessions = sessions.map((session) =>
          session.id === id
            ? {
                ...session,
                is_active: false,
                ended_at: new Date().toISOString(),
              }
            : session
        );
        setSessions(updatedSessions);
        setSnackbar({
          open: true,
          message: 'Session terminée avec succès',
          severity: 'success',
        });
      } catch (err) {
        console.error('Erreur lors de la terminaison de la session:', err);
        setSnackbar({
          open: true,
          message: 'Une erreur est survenue lors de la terminaison de la session.',
          severity: 'error',
        });
      }
    }
  };

  // Fermer la notification
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false,
    });
  };

  // Formater les données de session pour l'affichage
  const formatSessionData = (data) => {
    if (!data) return '';
    try {
      return JSON.stringify(data, null, 2);
    } catch (err) {
      return String(data);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Sessions USSD
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={fetchSessions}
        >
          Rafraîchir
        </Button>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height={400}>
            <CircularProgress />
          </Box>
        ) : (
          <DataGrid
            rows={sessions}
            columns={columns}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            autoHeight
            disableSelectionOnClick
          />
        )}
      </Paper>

      {/* Dialogue de détails de session */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>Détails de la session</DialogTitle>
        <DialogContent>
          {selectedSession && (
            <Box>
              <TextField
                label="ID de session"
                value={selectedSession.session_id}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
              <TextField
                label="Numéro de téléphone"
                value={selectedSession.phone_number}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
              <TextField
                label="Menu actuel"
                value={selectedSession.current_menu}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
              <TextField
                label="Début de session"
                value={new Date(selectedSession.started_at).toLocaleString()}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
              <TextField
                label="Dernière activité"
                value={new Date(selectedSession.last_activity).toLocaleString()}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
              {selectedSession.ended_at && (
                <TextField
                  label="Fin de session"
                  value={new Date(selectedSession.ended_at).toLocaleString()}
                  fullWidth
                  margin="normal"
                  InputProps={{ readOnly: true }}
                />
              )}
              <TextField
                label="Statut"
                value={selectedSession.is_active ? 'Active' : 'Terminée'}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
              <TextField
                label="Données de session"
                value={formatSessionData(selectedSession.session_data)}
                fullWidth
                margin="normal"
                multiline
                rows={10}
                InputProps={{ readOnly: true }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Fermer
          </Button>
          {selectedSession && selectedSession.is_active && (
            <Button
              onClick={() => {
                handleEndSession(selectedSession.id);
                handleCloseDialog();
              }}
              color="error"
              variant="contained"
            >
              Terminer la session
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Notification */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Sessions;
