import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  CircularProgress,
  Snackbar,
  Alert,
  IconButton,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

const Services = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('add'); // 'add' ou 'edit'
  const [selectedService, setSelectedService] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    menu_structure: '',
    is_active: true,
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success',
  });

  // Colonnes pour le tableau DataGrid
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'code', headerName: 'Code', width: 120 },
    { field: 'name', headerName: 'Nom', width: 200 },
    { field: 'description', headerName: 'Description', width: 300 },
    {
      field: 'is_active',
      headerName: 'Actif',
      width: 100,
      renderCell: (params) => (
        <Switch
          checked={params.value}
          onChange={(e) => handleToggleActive(params.row.id, e.target.checked)}
          color="primary"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <IconButton color="primary" onClick={() => handleEditClick(params.row)}>
            <EditIcon />
          </IconButton>
          <IconButton color="error" onClick={() => handleDeleteClick(params.row.id)}>
            <DeleteIcon />
          </IconButton>
        </Box>
      ),
    },
  ];

  // Récupérer la liste des services
  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      setLoading(true);
      // Dans un environnement réel, vous feriez un appel API ici
      // Simulation de données pour l'exemple
      const response = await axios.get('/api/services', {
        headers: {
          'X-API-Key': localStorage.getItem('apiKey') || 'your_secure_api_key_change_me',
        },
      });
      setServices(response.data || []);
      setLoading(false);
    } catch (err) {
      console.error('Erreur lors de la récupération des services:', err);
      // Pour l'exemple, nous allons utiliser des données fictives
      setServices([
        {
          id: 1,
          code: '*123#',
          name: 'Service Principal',
          description: 'Service USSD principal de l\'entreprise',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
        {
          id: 2,
          code: 'SRV-A',
          name: 'Service A',
          description: 'Description du Service A',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      ]);
      setError('Impossible de charger les services. Utilisation de données de démonstration.');
      setLoading(false);
    }
  };

  // Gérer l'ouverture du dialogue d'ajout
  const handleAddClick = () => {
    setDialogMode('add');
    setFormData({
      code: '',
      name: '',
      description: '',
      menu_structure: JSON.stringify({
        main: {
          title: 'Menu Principal',
          options: [
            { code: '1', text: 'Option 1', next: 'option1' },
            { code: '2', text: 'Option 2', next: 'option2' },
          ],
        },
      }, null, 2),
      is_active: true,
    });
    setOpenDialog(true);
  };

  // Gérer l'ouverture du dialogue d'édition
  const handleEditClick = (service) => {
    setDialogMode('edit');
    setSelectedService(service);
    setFormData({
      code: service.code,
      name: service.name,
      description: service.description,
      menu_structure: JSON.stringify(service.menu_structure || {}, null, 2),
      is_active: service.is_active,
    });
    setOpenDialog(true);
  };

  // Gérer la fermeture du dialogue
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  // Gérer les changements dans le formulaire
  const handleFormChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'is_active' ? checked : value,
    });
  };

  // Gérer la soumission du formulaire
  const handleSubmit = async () => {
    try {
      // Valider le JSON de la structure de menu
      let menuStructure;
      try {
        menuStructure = JSON.parse(formData.menu_structure);
      } catch (err) {
        setSnackbar({
          open: true,
          message: 'Structure de menu invalide. Veuillez vérifier le format JSON.',
          severity: 'error',
        });
        return;
      }

      const serviceData = {
        ...formData,
        menu_structure: menuStructure,
      };

      if (dialogMode === 'add') {
        // Ajouter un nouveau service
        // Dans un environnement réel, vous feriez un appel API ici
        // Simulation pour l'exemple
        const newService = {
          id: services.length + 1,
          ...serviceData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setServices([...services, newService]);
        setSnackbar({
          open: true,
          message: 'Service ajouté avec succès',
          severity: 'success',
        });
      } else {
        // Mettre à jour un service existant
        // Dans un environnement réel, vous feriez un appel API ici
        // Simulation pour l'exemple
        const updatedServices = services.map((service) =>
          service.id === selectedService.id
            ? {
                ...service,
                ...serviceData,
                updated_at: new Date().toISOString(),
              }
            : service
        );
        setServices(updatedServices);
        setSnackbar({
          open: true,
          message: 'Service mis à jour avec succès',
          severity: 'success',
        });
      }

      handleCloseDialog();
    } catch (err) {
      console.error('Erreur lors de la soumission du formulaire:', err);
      setSnackbar({
        open: true,
        message: 'Une erreur est survenue. Veuillez réessayer.',
        severity: 'error',
      });
    }
  };

  // Gérer la suppression d'un service
  const handleDeleteClick = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce service ?')) {
      try {
        // Dans un environnement réel, vous feriez un appel API ici
        // Simulation pour l'exemple
        const updatedServices = services.filter((service) => service.id !== id);
        setServices(updatedServices);
        setSnackbar({
          open: true,
          message: 'Service supprimé avec succès',
          severity: 'success',
        });
      } catch (err) {
        console.error('Erreur lors de la suppression du service:', err);
        setSnackbar({
          open: true,
          message: 'Une erreur est survenue lors de la suppression.',
          severity: 'error',
        });
      }
    }
  };

  // Gérer l'activation/désactivation d'un service
  const handleToggleActive = async (id, isActive) => {
    try {
      // Dans un environnement réel, vous feriez un appel API ici
      // Simulation pour l'exemple
      const updatedServices = services.map((service) =>
        service.id === id ? { ...service, is_active: isActive } : service
      );
      setServices(updatedServices);
      setSnackbar({
        open: true,
        message: `Service ${isActive ? 'activé' : 'désactivé'} avec succès`,
        severity: 'success',
      });
    } catch (err) {
      console.error('Erreur lors de la modification du statut du service:', err);
      setSnackbar({
        open: true,
        message: 'Une erreur est survenue. Veuillez réessayer.',
        severity: 'error',
      });
    }
  };

  // Fermer la notification
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false,
    });
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Gestion des services USSD
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddClick}
        >
          Ajouter un service
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
            rows={services}
            columns={columns}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            autoHeight
            disableSelectionOnClick
          />
        )}
      </Paper>

      {/* Dialogue d'ajout/édition de service */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Ajouter un service' : 'Modifier le service'}
        </DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            name="code"
            label="Code du service"
            type="text"
            fullWidth
            value={formData.code}
            onChange={handleFormChange}
            disabled={dialogMode === 'edit'}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="name"
            label="Nom du service"
            type="text"
            fullWidth
            value={formData.name}
            onChange={handleFormChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            multiline
            rows={2}
            value={formData.description}
            onChange={handleFormChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="menu_structure"
            label="Structure du menu (JSON)"
            type="text"
            fullWidth
            multiline
            rows={10}
            value={formData.menu_structure}
            onChange={handleFormChange}
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={handleFormChange}
                name="is_active"
                color="primary"
              />
            }
            label="Service actif"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Annuler
          </Button>
          <Button onClick={handleSubmit} color="primary" variant="contained">
            {dialogMode === 'add' ? 'Ajouter' : 'Mettre à jour'}
          </Button>
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

export default Services;
