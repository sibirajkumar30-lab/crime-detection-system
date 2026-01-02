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
    Alert,
    Tabs,
    Tab,
    CircularProgress,
    Chip,
    Divider,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import NotificationsIcon from '@mui/icons-material/Notifications';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import BarChart from './BarChart';
import LineChart from './LineChart';
import PieChart from './PieChart';

const AnalyticsDashboard = () => {
    const { user } = useAuth();
    const [tabValue, setTabValue] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // State for all dashboard data
    const [stats, setStats] = useState({});
    const [recentDetections, setRecentDetections] = useState([]);
    const [topCriminals, setTopCriminals] = useState([]);
    const [detectionTimeline, setDetectionTimeline] = useState([]);
    const [statusBreakdown, setStatusBreakdown] = useState([]);
    const [confidenceDistribution, setConfidenceDistribution] = useState([]);
    const [locationStats, setLocationStats] = useState([]);
    const [videoAnalytics, setVideoAnalytics] = useState({});
    const [performanceMetrics, setPerformanceMetrics] = useState({});
    const [timePatterns, setTimePatterns] = useState({ hourly_pattern: [], daily_pattern: [] });
    const [criminalActivity, setCriminalActivity] = useState([]);

    useEffect(() => {
        fetchAllData();
    }, []);

    const fetchAllData = async () => {
        setLoading(true);
        setError('');

        try {
            const [
                statsRes,
                detectionsRes,
                criminalsRes,
                timelineRes,
                statusRes,
                confidenceRes,
                locationRes,
                videoRes,
                performanceRes,
                patternsRes,
                activityRes
            ] = await Promise.all([
                API.get('/dashboard/stats').catch(err => ({ data: {} })),
                API.get('/dashboard/recent-detections').catch(err => ({ data: { detections: [] } })),
                API.get('/dashboard/top-criminals?limit=10').catch(err => ({ data: { criminals: [] } })),
                API.get('/dashboard/detections-timeline?days=7').catch(err => ({ data: { timeline: [] } })),
                API.get('/dashboard/detection-status-breakdown').catch(err => ({ data: { breakdown: [] } })),
                API.get('/dashboard/confidence-distribution').catch(err => ({ data: { distribution: [] } })),
                API.get('/dashboard/location-stats?limit=10').catch(err => ({ data: { locations: [] } })),
                API.get('/dashboard/video-analytics').catch(err => ({ data: {} })),
                API.get('/dashboard/analytics/performance').catch(err => ({ data: {} })),
                API.get('/dashboard/analytics/patterns').catch(err => ({ data: { hourly_pattern: [], daily_pattern: [] } })),
                API.get('/dashboard/analytics/activity').catch(err => ({ data: { criminals: [] } }))
            ]);

            setStats(statsRes.data || {});
            setRecentDetections(detectionsRes.data.detections || []);
            setTopCriminals(criminalsRes.data.criminals || []);
            setDetectionTimeline(timelineRes.data.timeline || []);
            setStatusBreakdown(statusRes.data.breakdown || []);
            setConfidenceDistribution(confidenceRes.data.distribution || []);
            setLocationStats(locationRes.data.locations || []);
            setVideoAnalytics(videoRes.data || {});
            setPerformanceMetrics(performanceRes.data || {});
            setTimePatterns(patternsRes.data || { hourly_pattern: [], daily_pattern: [] });
            setCriminalActivity(activityRes.data.criminals || []);

            setLoading(false);
        } catch (err) {
            console.error('Dashboard error:', err);
            setError('Failed to load dashboard data');
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, subtitle, icon: Icon, color }) => (
        <Card elevation={3} sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                        <Typography color="text.secondary" variant="body2">
                            {title}
                        </Typography>
                        <Typography variant="h4" sx={{ mt: 1, fontWeight: 'bold' }}>
                            {value}
                        </Typography>
                        {subtitle && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                                {subtitle}
                            </Typography>
                        )}
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

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress />
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            {/* Welcome Section */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" gutterBottom>
                    Analytics Dashboard
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Welcome back, {user?.username}! - Role: {user?.role?.toUpperCase()}
                </Typography>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            {/* Key Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={4}>
                    <StatCard
                        title="Total Criminals"
                        value={stats.total_criminals || 0}
                        subtitle={`${stats.wanted_criminals || 0} wanted`}
                        icon={PeopleIcon}
                        color="error.main"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <StatCard
                        title="Total Detections"
                        value={stats.total_detections || 0}
                        subtitle={`${stats.accuracy_rate || 0}% accuracy`}
                        icon={CheckCircleIcon}
                        color="success.main"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <StatCard
                        title="Total Alerts"
                        value={stats.total_alerts || 0}
                        subtitle={`${stats.total_videos || 0} videos processed`}
                        icon={NotificationsIcon}
                        color="info.main"
                    />
                </Grid>
            </Grid>

            {/* Tabs for Different Views */}
            <Paper elevation={3} sx={{ mb: 3 }}>
                <Tabs
                    value={tabValue}
                    onChange={handleTabChange}
                    variant="scrollable"
                    scrollButtons="auto"
                >
                    <Tab label="Overview" />
                    <Tab label="Detection Analysis" />
                    <Tab label="Criminal Activity" />
                    <Tab label="Location & Time" />
                    <Tab label="Video Analytics" />
                    <Tab label="Performance" />
                </Tabs>
            </Paper>

            {/* Tab Content */}
            {tabValue === 0 && (
                <Grid container spacing={3}>
                    {/* Detection Timeline */}
                    <Grid item xs={12} md={8}>
                        <LineChart
                            data={detectionTimeline.map(d => ({ ...d, date: new Date(d.date).toLocaleDateString() }))}
                            title="Detections Timeline (Last 7 Days)"
                            xKey="date"
                            yKey="count"
                            color="#1976d2"
                        />
                    </Grid>

                    {/* Detection Status */}
                    <Grid item xs={12} md={4}>
                        <PieChart
                            data={statusBreakdown}
                            title="Detection Status"
                            labelKey="status"
                            valueKey="count"
                        />
                    </Grid>

                    {/* Top Criminals */}
                    <Grid item xs={12} md={6}>
                        <BarChart
                            data={topCriminals.slice(0, 5)}
                            title="Most Detected Criminals"
                            dataKey="name"
                            valueKey="detection_count"
                            color="#d32f2f"
                        />
                    </Grid>

                    {/* Top Locations */}
                    <Grid item xs={12} md={6}>
                        <BarChart
                            data={locationStats.slice(0, 5)}
                            title="Top Detection Locations"
                            dataKey="location"
                            valueKey="count"
                            color="#2e7d32"
                        />
                    </Grid>

                    {/* Recent Detections Table */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Recent Detections
                            </Typography>
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Criminal</TableCell>
                                            <TableCell>Confidence</TableCell>
                                            <TableCell>Location</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Date & Time</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {recentDetections.slice(0, 10).map((detection) => (
                                            <TableRow key={detection.id}>
                                                <TableCell>
                                                    {detection.criminal?.name || 'Unknown'}
                                                </TableCell>
                                                <TableCell>
                                                    {(detection.confidence_score * 100).toFixed(2)}%
                                                </TableCell>
                                                <TableCell>{detection.location || 'N/A'}</TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={detection.status}
                                                        size="small"
                                                        color={
                                                            detection.status === 'verified' ? 'success' :
                                                            detection.status === 'pending' ? 'warning' : 'error'
                                                        }
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    {new Date(detection.detected_at).toLocaleString()}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Paper>
                    </Grid>
                </Grid>
            )}

            {tabValue === 1 && (
                <Grid container spacing={3}>
                    {/* Confidence Distribution */}
                    <Grid item xs={12} md={6}>
                        <BarChart
                            data={confidenceDistribution}
                            title="Confidence Score Distribution"
                            dataKey="range"
                            valueKey="count"
                            color="#1976d2"
                        />
                    </Grid>

                    {/* Status Breakdown */}
                    <Grid item xs={12} md={6}>
                        <PieChart
                            data={statusBreakdown}
                            title="Detection Status Distribution"
                            labelKey="status"
                            valueKey="count"
                        />
                    </Grid>

                    {/* Detection Statistics */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Detection Statistics
                            </Typography>
                            <Grid container spacing={2} sx={{ mt: 1 }}>
                                <Grid item xs={6} md={3}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h4" color="primary">
                                            {stats.total_detections || 0}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Total Detections
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={6} md={3}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h4" color="success.main">
                                            {stats.verified_detections || 0}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Verified
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={6} md={3}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h4" color="warning.main">
                                            {stats.pending_verifications || 0}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Pending
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={6} md={3}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h4" color="error.main">
                                            {stats.false_positives || 0}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            False Positives
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>
                </Grid>
            )}

            {tabValue === 2 && (
                <Grid container spacing={3}>
                    {/* Top Criminals */}
                    <Grid item xs={12}>
                        <BarChart
                            data={topCriminals}
                            title="Most Detected Criminals (Top 10)"
                            dataKey="name"
                            valueKey="detection_count"
                            color="#d32f2f"
                        />
                    </Grid>

                    {/* Criminal Activity Table */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Detailed Criminal Activity Report
                            </Typography>
                            <TableContainer>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Name</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Detections</TableCell>
                                            <TableCell>Avg Confidence</TableCell>
                                            <TableCell>Last Detected</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {criminalActivity.map((criminal) => (
                                            <TableRow key={criminal.id}>
                                                <TableCell>
                                                    <Typography variant="body2" fontWeight="bold">
                                                        {criminal.name}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={criminal.status}
                                                        size="small"
                                                        color={criminal.status === 'wanted' ? 'error' : 'success'}
                                                    />
                                                </TableCell>
                                                <TableCell>{criminal.detection_count}</TableCell>
                                                <TableCell>
                                                    {(criminal.avg_confidence * 100).toFixed(1)}%
                                                </TableCell>
                                                <TableCell>
                                                    {criminal.last_detected 
                                                        ? new Date(criminal.last_detected).toLocaleString()
                                                        : 'N/A'
                                                    }
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Paper>
                    </Grid>
                </Grid>
            )}

            {tabValue === 3 && (
                <Grid container spacing={3}>
                    {/* Location Stats */}
                    <Grid item xs={12} md={6}>
                        <BarChart
                            data={locationStats}
                            title="Detections by Location"
                            dataKey="location"
                            valueKey="count"
                            color="#2e7d32"
                        />
                    </Grid>

                    {/* Hourly Pattern */}
                    <Grid item xs={12} md={6}>
                        <LineChart
                            data={timePatterns.hourly_pattern || []}
                            title="Detections by Hour of Day"
                            xKey="hour"
                            yKey="count"
                            color="#ed6c02"
                        />
                    </Grid>

                    {/* Daily Pattern */}
                    <Grid item xs={12}>
                        <BarChart
                            data={timePatterns.daily_pattern || []}
                            title="Detections by Day of Week"
                            dataKey="day"
                            valueKey="count"
                            color="#9c27b0"
                        />
                    </Grid>
                </Grid>
            )}

            {tabValue === 4 && (
                <Grid container spacing={3}>
                    {/* Video Statistics Cards */}
                    <Grid item xs={12} md={3}>
                        <Card>
                            <CardContent>
                                <VideoLibraryIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                                <Typography variant="h5" sx={{ mt: 1 }}>
                                    {stats.total_videos || 0}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Total Videos
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={3}>
                        <Card>
                            <CardContent>
                                <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main' }} />
                                <Typography variant="h5" sx={{ mt: 1 }}>
                                    {stats.videos_completed || 0}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Completed
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={3}>
                        <Card>
                            <CardContent>
                                <PeopleIcon sx={{ fontSize: 40, color: 'info.main' }} />
                                <Typography variant="h5" sx={{ mt: 1 }}>
                                    {videoAnalytics.total_faces_detected || 0}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Total Faces
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={3}>
                        <Card>
                            <CardContent>
                                <WarningIcon sx={{ fontSize: 40, color: 'error.main' }} />
                                <Typography variant="h5" sx={{ mt: 1 }}>
                                    {videoAnalytics.total_criminals_matched || 0}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Criminals Matched
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Video Processing Stats */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Video Processing Performance
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Box>
                                        <Typography variant="body2" color="text.secondary">
                                            Average Processing Time
                                        </Typography>
                                        <Typography variant="h4">
                                            {videoAnalytics.avg_processing_time_seconds
                                                ? `${Math.round(videoAnalytics.avg_processing_time_seconds)}s`
                                                : 'N/A'
                                            }
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Box>
                                        <Typography variant="body2" color="text.secondary">
                                            Total Processing Time
                                        </Typography>
                                        <Typography variant="h4">
                                            {videoAnalytics.total_processing_time_seconds
                                                ? `${Math.round(videoAnalytics.total_processing_time_seconds / 60)}m`
                                                : 'N/A'
                                            }
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>

                    {/* Video Status Breakdown */}
                    <Grid item xs={12} md={6}>
                        <PieChart
                            data={videoAnalytics.status_breakdown || []}
                            title="Video Processing Status"
                            labelKey="status"
                            valueKey="count"
                        />
                    </Grid>
                </Grid>
            )}

            {tabValue === 5 && (
                <Grid container spacing={3}>
                    {/* Performance Metrics */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                System Performance Metrics
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h3" color="success.main">
                                            {performanceMetrics.accuracy_rate || 0}%
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Detection Accuracy
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h3" color="error.main">
                                            {performanceMetrics.false_positive_rate || 0}%
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            False Positive Rate
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="h3" color="info.main">
                                            {performanceMetrics.avg_response_time_seconds || 0}s
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Avg Alert Response Time
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>

                    {/* Confidence Scores */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Average Confidence Scores
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        All Detections
                                    </Typography>
                                    <Typography variant="h5">
                                        {performanceMetrics.avg_confidence_all 
                                            ? (performanceMetrics.avg_confidence_all * 100).toFixed(1) 
                                            : 0}%
                                    </Typography>
                                </Box>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        Verified Detections
                                    </Typography>
                                    <Typography variant="h5" color="success.main">
                                        {performanceMetrics.avg_confidence_verified 
                                            ? (performanceMetrics.avg_confidence_verified * 100).toFixed(1) 
                                            : 0}%
                                    </Typography>
                                </Box>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        False Positives
                                    </Typography>
                                    <Typography variant="h5" color="error.main">
                                        {performanceMetrics.avg_confidence_false_positive 
                                            ? (performanceMetrics.avg_confidence_false_positive * 100).toFixed(1) 
                                            : 0}%
                                    </Typography>
                                </Box>
                            </Box>
                        </Paper>
                    </Grid>

                    {/* Review Statistics */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Review Statistics
                            </Typography>
                            <Divider sx={{ my: 2 }} />
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        Total Reviewed
                                    </Typography>
                                    <Typography variant="h5">
                                        {performanceMetrics.total_reviewed || 0}
                                    </Typography>
                                </Box>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        Verified Detections
                                    </Typography>
                                    <Typography variant="h5" color="success.main">
                                        {performanceMetrics.verified_detections || 0}
                                    </Typography>
                                </Box>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        False Positives
                                    </Typography>
                                    <Typography variant="h5" color="error.main">
                                        {performanceMetrics.false_positives || 0}
                                    </Typography>
                                </Box>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>
            )}
        </Container>
    );
};

export default AnalyticsDashboard;
