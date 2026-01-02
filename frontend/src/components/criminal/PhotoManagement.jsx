import React, { useState } from 'react';
import {
    Box,
    Card,
    CardMedia,
    CardContent,
    CardActions,
    Typography,
    IconButton,
    Button,
    Grid,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    CircularProgress,
    Tooltip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import AddPhotoAlternateIcon from '@mui/icons-material/AddPhotoAlternate';
import API from '../../services/api';

/**
 * PhotoManagement Component
 * Phase 2/3 Enhancement: Manage multiple photos per criminal
 * - Display all photos with quality scores
 * - Mark photos as primary
 * - Delete photos
 * - Upload additional photos
 */
const PhotoManagement = ({ criminalId, encodings, onUpdate }) => {
    const [uploading, setUploading] = useState(false);
    const [deleteDialog, setDeleteDialog] = useState({ open: false, encoding: null });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const getQualityColor = (score) => {
        if (score >= 0.8) return 'success';
        if (score >= 0.6) return 'primary';
        if (score >= 0.4) return 'warning';
        return 'error';
    };

    const getQualityLabel = (score) => {
        if (score >= 0.8) return 'Excellent';
        if (score >= 0.6) return 'Good';
        if (score >= 0.4) return 'Fair';
        return 'Poor';
    };

    const getPoseIcon = (poseType) => {
        const icons = {
            'frontal': '😊',
            'three_quarter': '🙂',
            'profile': '🙃',
            'unknown': '😐'
        };
        return icons[poseType] || '😐';
    };

    const handleUploadPhotos = async (event) => {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        setUploading(true);
        setError('');
        setSuccess('');

        try {
            const formData = new FormData();
            files.forEach((file) => {
                formData.append('photos[]', file);
            });

            const response = await API.post(`/criminals/${criminalId}/photos`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setSuccess(`Uploaded ${response.data.results.filter(r => r.success).length}/${files.length} photos`);
            
            // Refresh encodings
            if (onUpdate) {
                setTimeout(() => onUpdate(), 1000);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to upload photos');
        } finally {
            setUploading(false);
        }
    };

    const handleSetPrimary = async (encodingId) => {
        try {
            await API.put(`/criminals/encodings/${encodingId}/set-primary`);
            setSuccess('Primary photo updated');
            
            if (onUpdate) {
                setTimeout(() => onUpdate(), 500);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to set primary photo');
        }
    };

    const handleDeletePhoto = async () => {
        if (!deleteDialog.encoding) return;

        try {
            await API.delete(`/criminals/encodings/${deleteDialog.encoding.id}`);
            setSuccess('Photo deleted successfully');
            setDeleteDialog({ open: false, encoding: null });
            
            if (onUpdate) {
                setTimeout(() => onUpdate(), 500);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to delete photo');
        }
    };

    return (
        <Box>
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">
                    Photos ({encodings.length})
                </Typography>
                <Button
                    variant="contained"
                    component="label"
                    startIcon={uploading ? <CircularProgress size={20} /> : <AddPhotoAlternateIcon />}
                    disabled={uploading}
                >
                    Add Photos
                    <input
                        type="file"
                        hidden
                        accept="image/*"
                        multiple
                        onChange={handleUploadPhotos}
                    />
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            {success && (
                <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
                    {success}
                </Alert>
            )}

            <Grid container spacing={2}>
                {encodings.map((encoding) => (
                    <Grid item xs={12} sm={6} md={4} key={encoding.id}>
                        <Card elevation={encoding.is_primary ? 6 : 2}>
                            <CardMedia
                                component="img"
                                height="200"
                                image={`http://127.0.0.1:5000/${encoding.image_path}`}
                                alt={`Photo ${encoding.id}`}
                                sx={{ objectFit: 'cover' }}
                            />
                            <CardContent>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                                    {encoding.is_primary && (
                                        <Chip
                                            icon={<StarIcon />}
                                            label="Primary"
                                            color="primary"
                                            size="small"
                                        />
                                    )}
                                    {encoding.quality_score && (
                                        <Chip
                                            label={`Quality: ${getQualityLabel(encoding.quality_score)} (${Math.round(encoding.quality_score * 100)}%)`}
                                            color={getQualityColor(encoding.quality_score)}
                                            size="small"
                                        />
                                    )}
                                </Box>
                                {encoding.pose_type && (
                                    <Typography variant="caption" display="block" color="text.secondary">
                                        {getPoseIcon(encoding.pose_type)} {encoding.pose_type.replace('_', ' ')}
                                    </Typography>
                                )}
                                <Typography variant="caption" display="block" color="text.secondary">
                                    Added: {new Date(encoding.created_at).toLocaleDateString()}
                                </Typography>
                            </CardContent>
                            <CardActions sx={{ justifyContent: 'space-between' }}>
                                <Tooltip title={encoding.is_primary ? "Already primary" : "Set as primary"}>
                                    <span>
                                        <IconButton
                                            size="small"
                                            onClick={() => handleSetPrimary(encoding.id)}
                                            disabled={encoding.is_primary}
                                            color="primary"
                                        >
                                            {encoding.is_primary ? <StarIcon /> : <StarBorderIcon />}
                                        </IconButton>
                                    </span>
                                </Tooltip>
                                <Tooltip title="Delete photo">
                                    <IconButton
                                        size="small"
                                        onClick={() => setDeleteDialog({ open: true, encoding })}
                                        color="error"
                                        disabled={encodings.length === 1}
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </Tooltip>
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {encodings.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                        No photos uploaded yet
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        Upload 2-3 photos (frontal + different angles) for best results
                    </Typography>
                </Box>
            )}

            {/* Delete Confirmation Dialog */}
            <Dialog
                open={deleteDialog.open}
                onClose={() => setDeleteDialog({ open: false, encoding: null })}
            >
                <DialogTitle>Delete Photo?</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete this photo? This action cannot be undone.
                    </Typography>
                    {deleteDialog.encoding?.is_primary && (
                        <Alert severity="warning" sx={{ mt: 2 }}>
                            This is the primary photo. Another photo will be automatically selected as primary.
                        </Alert>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialog({ open: false, encoding: null })}>
                        Cancel
                    </Button>
                    <Button onClick={handleDeletePhoto} color="error" variant="contained">
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default PhotoManagement;
