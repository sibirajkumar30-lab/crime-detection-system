import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { authAPI } from '../../services/api';
import {
    Container,
    Paper,
    Typography,
    Box,
    Grid,
    TextField,
    Button,
    Avatar,
    Divider,
    Alert
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import BadgeIcon from '@mui/icons-material/Badge';
import LockIcon from '@mui/icons-material/Lock';

const Profile = () => {
    const { user } = useAuth();
    const [showPasswordChange, setShowPasswordChange] = useState(false);
    const [passwords, setPasswords] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const handlePasswordChange = (e) => {
        setPasswords({
            ...passwords,
            [e.target.name]: e.target.value
        });
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });
        
        if (passwords.newPassword !== passwords.confirmPassword) {
            setMessage({ type: 'error', text: 'New passwords do not match' });
            return;
        }

        if (passwords.newPassword.length < 6) {
            setMessage({ type: 'error', text: 'Password must be at least 6 characters' });
            return;
        }

        setLoading(true);
        
        try {
            const response = await authAPI.changePassword({
                currentPassword: passwords.currentPassword,
                newPassword: passwords.newPassword
            });
            
            setMessage({ type: 'success', text: response.data.message || 'Password changed successfully' });
            
            // Reset form
            setPasswords({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            });
            
            // Hide form after 2 seconds
            setTimeout(() => {
                setShowPasswordChange(false);
                setMessage({ type: '', text: '' });
            }, 2000);
            
        } catch (error) {
            const errorMessage = error.response?.data?.message || 'Failed to change password';
            setMessage({ type: 'error', text: errorMessage });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
                User Profile
            </Typography>

            {/* Profile Information */}
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar
                        sx={{
                            width: 80,
                            height: 80,
                            bgcolor: 'primary.main',
                            fontSize: '2rem',
                            mr: 3
                        }}
                    >
                        {user?.username?.charAt(0).toUpperCase()}
                    </Avatar>
                    <Box>
                        <Typography variant="h5" gutterBottom>
                            {user?.username}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {user?.role?.toUpperCase()}
                        </Typography>
                    </Box>
                </Box>

                <Divider sx={{ my: 3 }} />

                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <PersonIcon sx={{ mr: 2, color: 'text.secondary' }} />
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Username
                                </Typography>
                                <Typography variant="body1">
                                    {user?.username}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <EmailIcon sx={{ mr: 2, color: 'text.secondary' }} />
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Email
                                </Typography>
                                <Typography variant="body1">
                                    {user?.email}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <BadgeIcon sx={{ mr: 2, color: 'text.secondary' }} />
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    User ID
                                </Typography>
                                <Typography variant="body1">
                                    #{user?.id}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <BadgeIcon sx={{ mr: 2, color: 'text.secondary' }} />
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Role
                                </Typography>
                                <Typography variant="body1">
                                    {user?.role?.toUpperCase()}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                </Grid>
            </Paper>

            {/* Change Password Section */}
            <Paper elevation={3} sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <LockIcon sx={{ mr: 2 }} />
                    <Typography variant="h6">
                        Change Password
                    </Typography>
                </Box>

                {!showPasswordChange ? (
                    <Button
                        variant="outlined"
                        onClick={() => setShowPasswordChange(true)}
                    >
                        Change Password
                    </Button>
                ) : (
                    <Box component="form" onSubmit={handlePasswordSubmit}>
                        {message.text && (
                            <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage({ type: '', text: '' })}>
                                {message.text}
                            </Alert>
                        )}

                        <TextField
                            fullWidth
                            type="password"
                            label="Current Password"
                            name="currentPassword"
                            value={passwords.currentPassword}
                            onChange={handlePasswordChange}
                            required
                            sx={{ mb: 2 }}
                        />

                        <TextField
                            fullWidth
                            type="password"
                            label="New Password"
                            name="newPassword"
                            value={passwords.newPassword}
                            onChange={handlePasswordChange}
                            required
                            sx={{ mb: 2 }}
                            helperText="Minimum 6 characters"
                        />

                        <TextField
                            fullWidth
                            type="password"
                            label="Confirm New Password"
                            name="confirmPassword"
                            value={passwords.confirmPassword}
                            onChange={handlePasswordChange}
                            required
                            sx={{ mb: 2 }}
                        />

                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <Button
                                type="submit"
                                variant="contained"
                                disabled={loading}
                            >
                                {loading ? 'Updating...' : 'Update Password'}
                            </Button>
                            <Button
                                variant="outlined"
                                disabled={loading}
                                onClick={() => {
                                    setShowPasswordChange(false);
                                    setPasswords({
                                        currentPassword: '',
                                        newPassword: '',
                                        confirmPassword: ''
                                    });
                                    setMessage({ type: '', text: '' });
                                }}
                            >
                                Cancel
                            </Button>
                        </Box>
                    </Box>
                )}
            </Paper>
        </Container>
    );
};

export default Profile;
