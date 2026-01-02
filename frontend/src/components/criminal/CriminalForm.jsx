import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import API from '../../services/api';
import {
    Container,
    Paper,
    Typography,
    Box,
    TextField,
    Button,
    MenuItem,
    Grid,
    Alert,
    CircularProgress
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';

const CriminalForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEdit = Boolean(id);

    const [formData, setFormData] = useState({
        name: '',
        alias: '',
        crime_type: '',
        description: '',
        status: 'wanted',
        danger_level: 'medium',
        last_seen_location: '',
        last_seen_date: ''
    });
    const [images, setImages] = useState([]);  // Changed to support multiple images
    const [existingImages, setExistingImages] = useState([]);  // Existing images for edit mode
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (isEdit) {
            fetchCriminal();
        }
    }, [id]);

    const fetchCriminal = async () => {
        try {
            const response = await API.get(`/criminals/${id}`);
            // Backend returns {criminal: {...}}
            const criminal = response.data.criminal || response.data;
            setFormData({
                name: criminal.name || '',
                alias: criminal.alias || '',
                crime_type: criminal.crime_type || '',
                description: criminal.description || '',
                status: criminal.status || 'wanted',
                danger_level: criminal.danger_level || 'medium',
                last_seen_location: criminal.last_seen_location || '',
                last_seen_date: criminal.last_seen_date || ''
            });
            // Set existing images if available
            if (criminal.encodings && criminal.encodings.length > 0) {
                setExistingImages(criminal.encodings);
            }
        } catch (err) {
            setError('Failed to load criminal data');
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleImageChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            // Support multiple images (Phase 2 enhancement)
            const filesArray = Array.from(e.target.files);
            setImages(filesArray);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            if (isEdit) {
                await API.put(`/criminals/${id}`, formData);
                
                // Upload new images if provided in edit mode
                if (images.length > 0) {
                    const formDataImg = new FormData();
                    images.forEach((image) => {
                        formDataImg.append('photos[]', image);
                    });
                    
                    await API.post(`/criminals/${id}/photos`, formDataImg, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    setSuccess(`Criminal updated successfully with ${images.length} new photo(s)`);
                } else {
                    setSuccess('Criminal updated successfully');
                }
            } else {
                const response = await API.post('/criminals', formData);
                setSuccess('Criminal added successfully');
                
                // Upload multiple images if provided (Phase 2 enhancement)
                if (images.length > 0 && response.data.criminal) {
                    const formDataImg = new FormData();
                    
                    // Append all images
                    images.forEach((image) => {
                        formDataImg.append('photos[]', image);
                    });
                    
                    await API.post(`/criminals/${response.data.criminal.id}/photos`, formDataImg, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    
                    setSuccess(`Criminal added successfully with ${images.length} photo(s)`);
                }
            }
            
            setTimeout(() => navigate('/criminals'), 1500);
        } catch (err) {
            console.error('Error saving criminal:', err.response);
            setError(err.response?.data?.message || err.response?.data?.error || 'Failed to save criminal');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h5" gutterBottom>
                    {isEdit ? 'Edit Criminal' : 'Add New Criminal'}
                </Typography>

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                        {error}
                    </Alert>
                )}

                {success && (
                    <Alert severity="success" sx={{ mb: 3 }}>
                        {success}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                label="Full Name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                            />
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Alias"
                                name="alias"
                                value={formData.alias}
                                onChange={handleChange}
                            />
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                label="Crime Type"
                                name="crime_type"
                                value={formData.crime_type}
                                onChange={handleChange}
                                placeholder="e.g., Theft, Assault, Fraud"
                            />
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                select
                                label="Status"
                                name="status"
                                value={formData.status}
                                onChange={handleChange}
                            >
                                <MenuItem value="wanted">Wanted</MenuItem>
                                <MenuItem value="arrested">Arrested</MenuItem>
                                <MenuItem value="released">Released</MenuItem>
                            </TextField>
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                select
                                label="Danger Level"
                                name="danger_level"
                                value={formData.danger_level}
                                onChange={handleChange}
                            >
                                <MenuItem value="low">Low</MenuItem>
                                <MenuItem value="medium">Medium</MenuItem>
                                <MenuItem value="high">High</MenuItem>
                                <MenuItem value="critical">Critical</MenuItem>
                            </TextField>
                        </Grid>

                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                type="date"
                                label="Last Seen Date"
                                name="last_seen_date"
                                value={formData.last_seen_date}
                                onChange={handleChange}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>

                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Last Seen Location"
                                name="last_seen_location"
                                value={formData.last_seen_location}
                                onChange={handleChange}
                            />
                        </Grid>

                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                multiline
                                rows={4}
                                label="Description"
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                placeholder="Enter detailed description of criminal activities..."
                            />
                        </Grid>

                        {!isEdit && (
                            <Grid item xs={12}>
                                <Button
                                    variant="outlined"
                                    component="label"
                                    fullWidth
                                >
                                    Upload Photos (Multiple Supported)
                                    <input
                                        type="file"
                                        hidden
                                        accept="image/*"
                                        multiple
                                        onChange={handleImageChange}
                                    />
                                </Button>
                                {images.length > 0 && (
                                    <Box sx={{ mt: 1 }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Selected {images.length} photo(s):
                                        </Typography>
                                        {images.map((img, index) => (
                                            <Typography key={index} variant="caption" display="block" color="text.secondary">
                                                • {img.name}
                                            </Typography>
                                        ))}
                                        <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block' }}>
                                            💡 Tip: Upload 2-3 photos (frontal + different angles) for better matching
                                        </Typography>
                                    </Box>
                                )}
                            </Grid>
                        )}

                        {isEdit && (
                            <Grid item xs={12}>
                                {/* Show existing images */}
                                {existingImages.length > 0 && (
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="body2" color="text.secondary" gutterBottom>
                                            Existing Photos ({existingImages.length}):
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
                                            {existingImages.map((encoding, index) => (
                                                <Box
                                                    key={encoding.id || index}
                                                    sx={{
                                                        width: 100,
                                                        height: 100,
                                                        border: '2px solid #ddd',
                                                        borderRadius: 1,
                                                        overflow: 'hidden',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        bgcolor: 'grey.100'
                                                    }}
                                                >
                                                    {encoding.image_path ? (
                                                        <img
                                                            src={`http://127.0.0.1:5000/${encoding.image_path}`}
                                                            alt={`Criminal photo ${index + 1}`}
                                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                            onError={(e) => {
                                                                e.target.style.display = 'none';
                                                                e.target.parentElement.innerHTML = '<Typography variant="caption">No Image</Typography>';
                                                            }}
                                                        />
                                                    ) : (
                                                        <Typography variant="caption" color="text.secondary">Photo {index + 1}</Typography>
                                                    )}
                                                </Box>
                                            ))}
                                        </Box>
                                    </Box>
                                )}
                                
                                {/* Upload new images */}
                                <Button
                                    variant="outlined"
                                    component="label"
                                    fullWidth
                                >
                                    Upload Additional Photos
                                    <input
                                        type="file"
                                        hidden
                                        accept="image/*"
                                        multiple
                                        onChange={handleImageChange}
                                    />
                                </Button>
                                {images.length > 0 && (
                                    <Box sx={{ mt: 1 }}>
                                        <Typography variant="body2" color="success.main">
                                            {images.length} new photo(s) selected:
                                        </Typography>
                                        {images.map((img, index) => (
                                            <Typography key={index} variant="caption" display="block" color="text.secondary">
                                                • {img.name}
                                            </Typography>
                                        ))}
                                    </Box>
                                )}
                            </Grid>
                        )}

                        <Grid item xs={12}>
                            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                                <Button
                                    variant="outlined"
                                    startIcon={<CancelIcon />}
                                    onClick={() => navigate('/criminals')}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    variant="contained"
                                    startIcon={<SaveIcon />}
                                    disabled={loading}
                                >
                                    {loading ? <CircularProgress size={24} /> : 'Save'}
                                </Button>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </Paper>
        </Container>
    );
};

export default CriminalForm;
