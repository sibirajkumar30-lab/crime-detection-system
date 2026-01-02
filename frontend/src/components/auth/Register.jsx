import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
    Container,
    Box,
    Paper,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
    Chip
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import Avatar from '@mui/material/Avatar';
import { authAPI } from '../../services/api';

const Register = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [searchParams] = useSearchParams();
    const invitationToken = searchParams.get('token');
    
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [invitationDetails, setInvitationDetails] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [verifyingToken, setVerifyingToken] = useState(false);

    useEffect(() => {
        // If no invitation token, redirect to login
        if (!invitationToken) {
            navigate('/login', { 
                state: { message: 'Registration requires an invitation. Please contact an administrator.' } 
            });
            return;
        }

        // Verify invitation token
        const verifyToken = async () => {
            setVerifyingToken(true);
            try {
                const response = await authAPI.verifyToken(invitationToken);
                setInvitationDetails(response.data);
                setFormData(prev => ({ ...prev, email: response.data.email }));
            } catch (error) {
                setError(error.response?.data?.error || 'Invalid or expired invitation token');
            } finally {
                setVerifyingToken(false);
            }
        };

        verifyToken();
    }, [invitationToken, navigate]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 4) {
            setError('Password must be at least 4 characters');
            return;
        }

        setLoading(true);

        try {
            // Register with invitation token
            const response = await authAPI.register({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                token: invitationToken
            });

            navigate('/login', { 
                state: { message: 'Registration successful! Please login with your credentials.' } 
            });
        } catch (error) {
            setError(error.response?.data?.error || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
                            <PersonAddIcon />
                        </Avatar>
                        <Typography component="h1" variant="h5">
                            Register
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Complete your registration with invitation
                        </Typography>
                    </Box>

                    {verifyingToken && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                            <CircularProgress />
                        </Box>
                    )}

                    {invitationDetails && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                <strong>Invitation Details:</strong>
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                <Chip label={`Role: ${invitationDetails.role.replace('_', ' ').toUpperCase()}`} size="small" color="primary" />
                                {invitationDetails.department && (
                                    <Chip label={`Department: ${invitationDetails.department}`} size="small" />
                                )}
                                <Chip 
                                    label={`Expires: ${new Date(invitationDetails.expires_at).toLocaleDateString()}`} 
                                    size="small" 
                                />
                            </Box>
                        </Alert>
                    )}

                    {error && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                            {error}
                        </Alert>
                    )}

                    {!verifyingToken && invitationDetails && (
                        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                id="username"
                                label="Username"
                                name="username"
                                autoComplete="username"
                                autoFocus
                                value={formData.username}
                                onChange={handleChange}
                                disabled={loading}
                            />
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                id="email"
                                label="Email Address"
                                name="email"
                                autoComplete="email"
                                value={formData.email}
                                onChange={handleChange}
                                disabled={true}
                                helperText="Email from invitation (cannot be changed)"
                            />
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                name="password"
                                label="Password"
                                type="password"
                                id="password"
                                autoComplete="new-password"
                                value={formData.password}
                                onChange={handleChange}
                                disabled={loading}
                            />
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                name="confirmPassword"
                                label="Confirm Password"
                                type="password"
                                id="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                disabled={loading}
                            />
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                sx={{ mt: 3, mb: 2 }}
                                disabled={loading}
                            >
                                {loading ? <CircularProgress size={24} /> : 'Complete Registration'}
                            </Button>
                            <Box sx={{ textAlign: 'center' }}>
                                <Link to="/login" style={{ textDecoration: 'none' }}>
                                    <Typography variant="body2" color="primary">
                                        Already have an account? Sign in
                                    </Typography>
                                </Link>
                            </Box>
                        </Box>
                    )}
                </Paper>
            </Box>
        </Container>
    );
};

export default Register;
