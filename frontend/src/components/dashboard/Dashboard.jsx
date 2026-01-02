import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import API from '../../services/api';
import {
    Container,
    Grid,
    Paper,
    Typography,
    Box,
    Card,
    CardContent,
    Alert
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import NotificationsIcon from '@mui/icons-material/Notifications';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        total_criminals: 0,
        total_detections: 0,
        pending_detections: 0,
        total_alerts: 0
    });
    const [recentDetections, setRecentDetections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [statsResponse, detectionsResponse] = await Promise.all([
                API.get('/dashboard/stats'),
                API.get('/dashboard/recent-detections')
            ]);

            setStats(statsResponse.data);
            setRecentDetections(detectionsResponse.data.detections || []);
            setLoading(false);
        } catch (err) {
            setError('Failed to load dashboard data');
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, icon: Icon, color }) => (
        <Card elevation={3}>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                        <Typography color="text.secondary" variant="body2">
                            {title}
                        </Typography>
                        <Typography variant="h4" sx={{ mt: 1, fontWeight: 'bold' }}>
                            {value}
                        </Typography>
                    </Box>
                    <Box
                        sx={{
                            backgroundColor: color,
                            borderRadius: '50%',
                            p: 2,
                            display: 'flex',
                            alignItems: 'center'
                        }}
                    >
                        <Icon sx={{ fontSize: 40, color: 'white' }} />
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );

    if (loading) {
        return (
            <Container>
                <Typography>Loading...</Typography>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Welcome Section */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" gutterBottom>
                    Welcome back, {user?.username}!
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Role: {user?.role?.toUpperCase()}
                </Typography>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Criminals"
                        value={stats.total_criminals}
                        icon={PeopleIcon}
                        color="error.main"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Detections"
                        value={stats.total_detections}
                        icon={CheckCircleIcon}
                        color="success.main"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Pending Reviews"
                        value={stats.pending_detections}
                        icon={WarningIcon}
                        color="warning.main"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Alerts"
                        value={stats.total_alerts}
                        icon={NotificationsIcon}
                        color="info.main"
                    />
                </Grid>
            </Grid>

            {/* Recent Detections */}
            <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Recent Detections
                </Typography>
                {recentDetections.length === 0 ? (
                    <Typography color="text.secondary" sx={{ mt: 2 }}>
                        No recent detections
                    </Typography>
                ) : (
                    <Box sx={{ mt: 2 }}>
                        {recentDetections.map((detection) => (
                            <Box
                                key={detection.id}
                                sx={{
                                    p: 2,
                                    mb: 2,
                                    border: '1px solid',
                                    borderColor: 'divider',
                                    borderRadius: 1
                                }}
                            >
                                <Typography variant="subtitle1">
                                    <strong>Criminal:</strong> {detection.criminal_name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Confidence: {(detection.confidence_score * 100).toFixed(2)}%
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Time: {new Date(detection.detected_at).toLocaleString()}
                                </Typography>
                            </Box>
                        ))}
                    </Box>
                )}
            </Paper>
        </Container>
    );
};

export default Dashboard;
