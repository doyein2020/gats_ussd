import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import axios from 'axios';

// Enregistrement des composants ChartJS nécessaires
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Composant de carte de statistique
const StatCard = ({ title, value, loading }) => {
  return (
    <Paper
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        height: 140,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Typography component="h2" variant="h6" color="primary" gutterBottom>
        {title}
      </Typography>
      {loading ? (
        <CircularProgress size={30} />
      ) : (
        <Typography component="p" variant="h4">
          {value}
        </Typography>
      )}
    </Paper>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        // Appel à l'API pour récupérer les statistiques
        const response = await axios.get('/api/ussd/stats', {
          headers: {
            'X-API-Key': localStorage.getItem('apiKey') || 'your_secure_api_key_change_me',
          },
        });
        setStats(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Erreur lors de la récupération des statistiques:', err);
        setError('Impossible de charger les statistiques. Veuillez réessayer plus tard.');
        setLoading(false);
      }
    };

    fetchStats();

    // Rafraîchir les statistiques toutes les 30 secondes
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // Données pour le graphique des sessions
  const sessionData = {
    labels: ['Sessions actives', 'Sessions terminées'],
    datasets: [
      {
        data: stats ? [stats.active_sessions, stats.total_sessions - stats.active_sessions] : [0, 0],
        backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)'],
        borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
        borderWidth: 1,
      },
    ],
  };

  // Données pour le graphique des interactions
  const interactionData = {
    labels: ['Réussies', 'Erreurs'],
    datasets: [
      {
        data: stats ? [stats.total_interactions - stats.error_count, stats.error_count] : [0, 0],
        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 159, 64, 0.6)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 159, 64, 1)'],
        borderWidth: 1,
      },
    ],
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom component="h1">
        Tableau de bord
      </Typography>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Grid container spacing={3}>
        {/* Statistiques principales */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Sessions totales"
            value={stats?.total_sessions || 0}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Sessions actives"
            value={stats?.active_sessions || 0}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Interactions totales"
            value={stats?.total_interactions || 0}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Temps de réponse moyen"
            value={stats ? `${stats.avg_response_time_ms.toFixed(2)} ms` : '0 ms'}
            loading={loading}
          />
        </Grid>

        {/* Graphiques */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 300,
            }}
          >
            <Typography variant="h6" gutterBottom>
              Sessions
            </Typography>
            {loading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                <CircularProgress />
              </Box>
            ) : (
              <Pie data={sessionData} options={{ maintainAspectRatio: false }} />
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 300,
            }}
          >
            <Typography variant="h6" gutterBottom>
              Interactions
            </Typography>
            {loading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                <CircularProgress />
              </Box>
            ) : (
              <Pie data={interactionData} options={{ maintainAspectRatio: false }} />
            )}
          </Paper>
        </Grid>

        {/* Taux d'erreur */}
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 300,
            }}
          >
            <Typography variant="h6" gutterBottom>
              Taux d'erreur
            </Typography>
            {loading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                <CircularProgress />
              </Box>
            ) : (
              <Bar
                data={{
                  labels: ['Taux d\'erreur'],
                  datasets: [
                    {
                      label: 'Pourcentage',
                      data: [stats ? stats.error_rate * 100 : 0],
                      backgroundColor: 'rgba(255, 99, 132, 0.6)',
                      borderColor: 'rgba(255, 99, 132, 1)',
                      borderWidth: 1,
                    },
                  ],
                }}
                options={{
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      title: {
                        display: true,
                        text: 'Pourcentage (%)',
                      },
                    },
                  },
                }}
              />
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
