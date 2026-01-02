import React, { useState } from 'react';
import API from '../../services/api';
import {
    Container,
    Paper,
    Typography,
    Box,
    Button,
    TextField,
    Grid,
    Alert,
    CircularProgress,
    Card,
    CardContent,
    Chip,
    Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImageIcon from '@mui/icons-material/Image';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

const UploadDetection = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [location, setLocation] = useState('');
    const [cameraId, setCameraId] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setResult(null);
            setError('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedFile) {
            setError('Please select an image');
            return;
        }

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('image', selectedFile);
            formData.append('location', location);
            formData.append('camera_id', cameraId);

            // Debug: Log what we're sending
            console.log('Uploading file:', selectedFile);
            console.log('FormData entries:', Array.from(formData.entries()));

            // Don't set Content-Type manually - let Axios handle it for FormData
            // This ensures Authorization header is preserved
            const response = await API.post('/detection/upload', formData);

            setResult(response.data);
        } catch (err) {
            console.error('Upload error:', err);
            setError(err.response?.data?.message || 'Detection failed');
        } finally {
            setLoading(false);
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
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
                Face Detection
            </Typography>

            <Grid container spacing={3}>
                {/* Upload Section */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Upload Image
                        </Typography>

                        {error && (
                            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                                {error}
                            </Alert>
                        )}

                        <Box component="form" onSubmit={handleSubmit}>
                            <Button
                                variant="outlined"
                                component="label"
                                fullWidth
                                startIcon={<CloudUploadIcon />}
                                sx={{ mb: 2 }}
                            >
                                Select Image
                                <input
                                    type="file"
                                    hidden
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                />
                            </Button>

                            {preview && (
                                <Box sx={{ mb: 2, textAlign: 'center' }}>
                                    <img
                                        src={preview}
                                        alt="Preview"
                                        style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }}
                                    />
                                </Box>
                            )}

                            <TextField
                                fullWidth
                                label="Location (Optional)"
                                value={location}
                                onChange={(e) => setLocation(e.target.value)}
                                sx={{ mb: 2 }}
                                placeholder="e.g., Main Entrance, Building A"
                            />

                            <TextField
                                fullWidth
                                label="Camera ID (Optional)"
                                value={cameraId}
                                onChange={(e) => setCameraId(e.target.value)}
                                sx={{ mb: 2 }}
                                placeholder="e.g., CAM-001"
                            />

                            <Button
                                type="submit"
                                variant="contained"
                                fullWidth
                                disabled={!selectedFile || loading}
                                startIcon={loading ? <CircularProgress size={20} /> : <ImageIcon />}
                            >
                                {loading ? 'Processing...' : 'Detect Faces'}
                            </Button>
                        </Box>
                    </Paper>
                </Grid>

                {/* Results Section */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Detection Results
                        </Typography>

                        {!result && !loading && (
                            <Box sx={{ textAlign: 'center', py: 6 }}>
                                <ImageIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                                <Typography color="text.secondary">
                                    Upload an image to start detection
                                </Typography>
                            </Box>
                        )}

                        {loading && (
                            <Box sx={{ textAlign: 'center', py: 6 }}>
                                <CircularProgress size={60} />
                                <Typography color="text.secondary" sx={{ mt: 2 }}>
                                    Analyzing image...
                                </Typography>
                            </Box>
                        )}

                        {result && (
                            <Box>
                                <Box sx={{ mb: 3 }}>
                                    <Typography variant="body1" gutterBottom>
                                        <strong>Faces Detected:</strong> {result.faces_detected}
                                    </Typography>
                                    {result.matched_faces !== undefined && (
                                        <Typography variant="body1" gutterBottom>
                                            <strong>Matched Faces:</strong> {result.matched_faces}
                                        </Typography>
                                    )}
                                    <Typography variant="body1" gutterBottom>
                                        <strong>Total Matches:</strong> {result.matches?.length || 0}
                                    </Typography>
                                    {result.faces_detected > 1 && (
                                        <Chip 
                                            label="Multi-Face Detection" 
                                            color="primary" 
                                            size="small"
                                            sx={{ mt: 1 }}
                                        />
                                    )}
                                </Box>

                                {result.matches && result.matches.length > 0 ? (
                                    <>
                                        <Alert severity="error" sx={{ mb: 2 }} icon={<WarningIcon />}>
                                            <strong>CRIMINAL DETECTED!</strong> {result.matches.length} match(es) found. Immediate action required.
                                        </Alert>

                                        <Divider sx={{ my: 2 }} />

                                        {result.matches.map((match, index) => (
                                            <Card key={index} sx={{ mb: 2, border: '2px solid #f44336' }}>
                                                <CardContent>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                                        <Box>
                                                            <Typography variant="h6">
                                                                {match.criminal_name}
                                                            </Typography>
                                                            {match.face_index !== undefined && (
                                                                <Typography variant="caption" color="text.secondary">
                                                                    Face #{match.face_index + 1} in image
                                                                </Typography>
                                                            )}
                                                        </Box>
                                                        <Chip
                                                            label={`${(match.confidence * 100).toFixed(1)}% Match`}
                                                            color="error"
                                                            size="small"
                                                        />
                                                    </Box>

                                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                                        <strong>Crime Type:</strong> {match.crime_type}
                                                    </Typography>

                                                    <Box sx={{ mt: 1 }}>
                                                        <Chip
                                                            label={`Danger: ${match.danger_level}`}
                                                            color={getDangerColor(match.danger_level)}
                                                            size="small"
                                                            sx={{ mr: 1 }}
                                                        />
                                                        <Chip
                                                            label={match.status.toUpperCase()}
                                                            color={match.status === 'wanted' ? 'error' : 'warning'}
                                                            size="small"
                                                        />
                                                    </Box>
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </>
                                ) : result.faces_detected > 0 ? (
                                    <Alert severity="success" icon={<CheckCircleIcon />}>
                                        {result.faces_detected > 1 
                                            ? `Detected ${result.faces_detected} faces. No criminal matches found. All clear!`
                                            : 'No criminal matches found. All clear!'
                                        }
                                    </Alert>
                                ) : (
                                    <Alert severity="info">
                                        No faces detected in the image.
                                    </Alert>
                                )}

                                {result.message && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                                        {result.message}
                                    </Typography>
                                )}
                            </Box>
                        )}
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default UploadDetection;
