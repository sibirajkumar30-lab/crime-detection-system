import React, { useState, useEffect } from 'react';
import API from '../../services/api';
import {
    Container,
    Paper,
    Typography,
    Box,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    CircularProgress,
    Alert,
    IconButton,
    Collapse,
    TextField,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    Grid
} from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

const AlertsList = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedAlert, setExpandedAlert] = useState(null);
    const [filterSeverity, setFilterSeverity] = useState('all');
    const [filterCategory, setFilterCategory] = useState('all');
    const [stats, setStats] = useState({
        total: 0,
        sent: 0,
        failed: 0
    });

    useEffect(() => {
        fetchAlerts();
    }, [filterSeverity, filterCategory]);

    const fetchAlerts = async () => {
        try {
            setLoading(true);
            // Fetch all alerts (email and in-app)
            const response = await API.get('/notifications', {
                params: {
                    limit: 100,
                    ...(filterSeverity !== 'all' && { severity: filterSeverity }),
                    ...(filterCategory !== 'all' && { category: filterCategory })
                }
            });

            const allAlerts = response.data.notifications || [];
            setAlerts(allAlerts);

            // Calculate stats
            const sent = allAlerts.filter(a => a.status === 'sent').length;
            const failed = allAlerts.filter(a => a.status === 'failed').length;
            
            setStats({
                total: allAlerts.length,
                sent: sent,
                failed: failed
            });

            setError('');
        } catch (err) {
            console.error('Failed to fetch alerts:', err);
            setError('Failed to load alerts');
        } finally {
            setLoading(false);
        }
    };

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'critical':
                return <ErrorIcon sx={{ color: '#d32f2f' }} />;
            case 'warning':
                return <WarningIcon sx={{ color: '#ed6c02' }} />;
            case 'info':
                return <InfoIcon sx={{ color: '#0288d1' }} />;
            default:
                return <InfoIcon sx={{ color: '#757575' }} />;
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical':
                return 'error';
            case 'warning':
                return 'warning';
            case 'info':
                return 'info';
            default:
                return 'default';
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'sent':
            case 'delivered':
            case 'read':
                return 'success';
            case 'failed':
                return 'error';
            case 'pending':
                return 'warning';
            default:
                return 'default';
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const utcDate = new Date(dateString);
        const istDate = new Date(utcDate.getTime() + (5.5 * 60 * 60 * 1000));
        return istDate.toLocaleString('en-IN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        }) + ' IST';
    };

    const toggleExpand = (alertId) => {
        setExpandedAlert(expandedAlert === alertId ? null : alertId);
    };

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress />
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
                Alert History
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
                View all email alerts sent by the system
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 3, mt: 2 }}>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <EmailIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                        <Typography variant="h4">{stats.total}</Typography>
                        <Typography variant="body2" color="text.secondary">
                            Total Alerts
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                        <Typography variant="h4">{stats.sent}</Typography>
                        <Typography variant="body2" color="text.secondary">
                            Successfully Sent
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <ErrorIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                        <Typography variant="h4">{stats.failed}</Typography>
                        <Typography variant="body2" color="text.secondary">
                            Failed
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>

            {/* Filters */}
            <Paper sx={{ p: 2, mb: 3 }}>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                            <InputLabel>Severity</InputLabel>
                            <Select
                                value={filterSeverity}
                                label="Severity"
                                onChange={(e) => setFilterSeverity(e.target.value)}
                            >
                                <MenuItem value="all">All Severities</MenuItem>
                                <MenuItem value="critical">Critical</MenuItem>
                                <MenuItem value="warning">Warning</MenuItem>
                                <MenuItem value="info">Info</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                            <InputLabel>Category</InputLabel>
                            <Select
                                value={filterCategory}
                                label="Category"
                                onChange={(e) => setFilterCategory(e.target.value)}
                            >
                                <MenuItem value="all">All Categories</MenuItem>
                                <MenuItem value="detection">Detection</MenuItem>
                                <MenuItem value="criminal_mgmt">Criminal Management</MenuItem>
                                <MenuItem value="system">System</MenuItem>
                                <MenuItem value="operational">Operational</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                </Grid>
            </Paper>

            {/* Alerts Table */}
            <Paper elevation={3}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell width="50px"></TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Subject</TableCell>
                                <TableCell>Recipient</TableCell>
                                <TableCell>Severity</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Sent At</TableCell>
                                <TableCell>Action</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {alerts.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={8} align="center">
                                        <Typography color="text.secondary" sx={{ py: 4 }}>
                                            No alerts found
                                        </Typography>
                                    </TableCell>
                                </TableRow>
                            ) : (
                                alerts.map((alert) => (
                                    <React.Fragment key={alert.id}>
                                        <TableRow hover>
                                            <TableCell>
                                                {getSeverityIcon(alert.severity)}
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={alert.alert_type?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
                                                    size="small"
                                                    color="primary"
                                                    variant="outlined"
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2">
                                                    {alert.subject || alert.title || 'No subject'}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    <EmailIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                                    <Typography variant="body2">
                                                        {alert.recipient_email || 'N/A'}
                                                    </Typography>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={alert.severity?.toUpperCase() || 'N/A'}
                                                    size="small"
                                                    color={getSeverityColor(alert.severity)}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={alert.status?.toUpperCase() || 'N/A'}
                                                    size="small"
                                                    color={getStatusColor(alert.status)}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2">
                                                    {formatDate(alert.sent_at)}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <IconButton
                                                    size="small"
                                                    onClick={() => toggleExpand(alert.id)}
                                                >
                                                    {expandedAlert === alert.id ? (
                                                        <ExpandLessIcon />
                                                    ) : (
                                                        <ExpandMoreIcon />
                                                    )}
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell colSpan={8} sx={{ py: 0 }}>
                                                <Collapse in={expandedAlert === alert.id} timeout="auto" unmountOnExit>
                                                    <Box sx={{ p: 2, bgcolor: 'background.default' }}>
                                                        <Typography variant="subtitle2" gutterBottom>
                                                            Alert Details:
                                                        </Typography>
                                                        <Grid container spacing={2}>
                                                            <Grid item xs={12} md={6}>
                                                                <Typography variant="body2" color="text.secondary">
                                                                    <strong>Alert ID:</strong> #{alert.id}
                                                                </Typography>
                                                                <Typography variant="body2" color="text.secondary">
                                                                    <strong>Category:</strong> {alert.category || 'N/A'}
                                                                </Typography>
                                                                <Typography variant="body2" color="text.secondary">
                                                                    <strong>Priority:</strong> {alert.priority || 'N/A'}
                                                                </Typography>
                                                                <Typography variant="body2" color="text.secondary">
                                                                    <strong>Delivery Method:</strong> {alert.delivery_method || 'N/A'}
                                                                </Typography>
                                                            </Grid>
                                                            <Grid item xs={12} md={6}>
                                                                {alert.detection_log_id && (
                                                                    <Typography variant="body2" color="text.secondary">
                                                                        <strong>Detection Log ID:</strong> {alert.detection_log_id}
                                                                    </Typography>
                                                                )}
                                                                {alert.video_detection_id && (
                                                                    <Typography variant="body2" color="text.secondary">
                                                                        <strong>Video Detection ID:</strong> {alert.video_detection_id}
                                                                    </Typography>
                                                                )}
                                                                {alert.criminal_id && (
                                                                    <Typography variant="body2" color="text.secondary">
                                                                        <strong>Criminal ID:</strong> {alert.criminal_id}
                                                                    </Typography>
                                                                )}
                                                                <Typography variant="body2" color="text.secondary">
                                                                    <strong>Created At:</strong> {formatDate(alert.created_at)}
                                                                </Typography>
                                                            </Grid>
                                                        </Grid>
                                                    </Box>
                                                </Collapse>
                                            </TableCell>
                                        </TableRow>
                                    </React.Fragment>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Container>
    );
};

export default AlertsList;
