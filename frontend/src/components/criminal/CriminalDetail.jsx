import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../../services/api';
import PhotoManagement from './PhotoManagement';  // Phase 2/3 enhancement
import {
    Container,
    Paper,
    Typography,
    Box,
    Grid,
    Chip,
    Button,
    Alert,
    CircularProgress,
    Divider
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';

const CriminalDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [criminal, setCriminal] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCriminal();
    }, [id]);

    const fetchCriminal = async () => {
        try {
            const response = await API.get(`/criminals/${id}`);
            // Backend returns {criminal: {...}}
            setCriminal(response.data.criminal || response.data);
            setLoading(false);
        } catch (err) {
            setError('Failed to load criminal details');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <CircularProgress />
            </Box>
        );
    }

    if (error || !criminal) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <Alert severity="error">{error || 'Criminal not found'}</Alert>
                <Button onClick={() => navigate('/criminals')} sx={{ mt: 2 }}>
                    Back to List
                </Button>
            </Container>
        );
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'wanted': return 'error';
            case 'arrested': return 'warning';
            case 'released': return 'success';
            default: return 'default';
        }
    };

    const getDangerColor = (level) => {
        switch (level) {
            case 'critical': return 'error';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'success';
            default: return 'default';
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate('/criminals')}
                >
                    Back to List
                </Button>
                <Button
                    variant="contained"
                    startIcon={<EditIcon />}
                    onClick={() => navigate(`/criminals/edit/${id}`)}
                >
                    Edit
                </Button>
            </Box>

            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" gutterBottom>
                    {criminal.name}
                </Typography>
                {criminal.alias && (
                    <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                        Alias: {criminal.alias}
                    </Typography>
                )}

                <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                    <Chip
                        label={(criminal.status || 'unknown').toUpperCase()}
                        color={getStatusColor(criminal.status)}
                    />
                    <Chip
                        label={`Danger: ${criminal.danger_level || 'unknown'}`}
                        color={getDangerColor(criminal.danger_level)}
                    />
                </Box>

                <Divider sx={{ my: 3 }} />

                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                            Crime Type
                        </Typography>
                        <Typography variant="body1">{criminal.crime_type}</Typography>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                            Last Seen Date
                        </Typography>
                        <Typography variant="body1">
                            {criminal.last_seen_date
                                ? new Date(criminal.last_seen_date).toLocaleDateString()
                                : 'N/A'}
                        </Typography>
                    </Grid>

                    <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary">
                            Last Seen Location
                        </Typography>
                        <Typography variant="body1">
                            {criminal.last_seen_location || 'N/A'}
                        </Typography>
                    </Grid>

                    <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary">
                            Description
                        </Typography>
                        <Typography variant="body1">
                            {criminal.description || 'No description available'}
                        </Typography>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                            Added Date
                        </Typography>
                        <Typography variant="body1">
                            {new Date(criminal.added_date).toLocaleString()}
                        </Typography>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                            Last Updated
                        </Typography>
                        <Typography variant="body1">
                            {new Date(criminal.updated_at).toLocaleString()}
                        </Typography>
                    </Grid>
                </Grid>
            </Paper>

            {/* Phase 2/3 Enhancement: Photo Management */}
            <Paper elevation={3} sx={{ p: 4, mt: 3 }}>
                <PhotoManagement
                    criminalId={id}
                    encodings={criminal.encodings || []}
                    onUpdate={fetchCriminal}
                />
            </Paper>
        </Container>
    );
};

export default CriminalDetail;
