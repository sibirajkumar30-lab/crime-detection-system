import React, { useState, useEffect } from 'react';
import {
    Box,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    Paper,
    IconButton,
    Chip,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Alert,
    Snackbar,
    Tooltip,
    CircularProgress,
    Typography,
    InputAdornment
} from '@mui/material';
import {
    Add,
    Delete,
    ContentCopy,
    Refresh,
    Email
} from '@mui/icons-material';
import { adminAPI } from '../../services/api';

function InvitationManagement() {
    const [invitations, setInvitations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalInvitations, setTotalInvitations] = useState(0);
    const [statusFilter, setStatusFilter] = useState('pending');
    
    // Create invitation dialog
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [createForm, setCreateForm] = useState({
        email: '',
        role: 'operator',
        department: ''
    });
    const [createdInvitation, setCreatedInvitation] = useState(null);
    
    // Snackbar
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

    useEffect(() => {
        fetchInvitations();
    }, [page, rowsPerPage, statusFilter]);

    const fetchInvitations = async () => {
        try {
            setLoading(true);
            const params = {
                page: page + 1,
                per_page: rowsPerPage,
                status: statusFilter
            };
            
            const response = await adminAPI.getInvitations(params);
            setInvitations(response.data.invitations);
            setTotalInvitations(response.data.total);
        } catch (error) {
            showSnackbar('Failed to fetch invitations: ' + (error.response?.data?.error || error.message), 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleCreateInvitation = async () => {
        try {
            const response = await adminAPI.createInvitation(createForm);
            setCreatedInvitation(response.data);
            showSnackbar('Invitation created successfully', 'success');
            fetchInvitations();
            // Keep dialog open to show the invitation link
        } catch (error) {
            showSnackbar('Failed to create invitation: ' + (error.response?.data?.error || error.message), 'error');
        }
    };

    const handleRevokeInvitation = async (id) => {
        if (!window.confirm('Are you sure you want to revoke this invitation?')) {
            return;
        }

        try {
            await adminAPI.revokeInvitation(id);
            showSnackbar('Invitation revoked successfully', 'success');
            fetchInvitations();
        } catch (error) {
            showSnackbar('Failed to revoke invitation: ' + (error.response?.data?.error || error.message), 'error');
        }
    };

    const handleResendInvitation = async (id) => {
        try {
            await adminAPI.resendInvitation(id);
            showSnackbar('Invitation email sent successfully', 'success');
        } catch (error) {
            showSnackbar('Failed to resend invitation: ' + (error.response?.data?.error || error.message), 'error');
        }
    };

    const handleCopyLink = (link) => {
        navigator.clipboard.writeText(link);
        showSnackbar('Invitation link copied to clipboard', 'success');
    };

    const handleCloseCreateDialog = () => {
        setCreateDialogOpen(false);
        setCreatedInvitation(null);
        setCreateForm({
            email: '',
            role: 'operator',
            department: ''
        });
    };

    const showSnackbar = (message, severity = 'info') => {
        setSnackbar({ open: true, message, severity });
    };

    const handleCloseSnackbar = () => {
        setSnackbar({ ...snackbar, open: false });
    };

    const getStatusColor = (invitation) => {
        if (!invitation.is_active) return 'error';
        if (invitation.used_at) return 'success';
        if (new Date(invitation.expires_at) < new Date()) return 'warning';
        return 'primary';
    };

    const getStatusLabel = (invitation) => {
        if (!invitation.is_active) return 'Revoked';
        if (invitation.used_at) return 'Used';
        if (new Date(invitation.expires_at) < new Date()) return 'Expired';
        return 'Pending';
    };

    const getRoleColor = (role) => {
        const colors = {
            super_admin: 'error',
            admin: 'warning',
            operator: 'info',
            viewer: 'default'
        };
        return colors[role] || 'default';
    };

    return (
        <Box>
            {/* Header with Create Button */}
            <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel>Status Filter</InputLabel>
                    <Select
                        value={statusFilter}
                        label="Status Filter"
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <MenuItem value="all">All</MenuItem>
                        <MenuItem value="pending">Pending</MenuItem>
                        <MenuItem value="used">Used</MenuItem>
                        <MenuItem value="expired">Expired</MenuItem>
                    </Select>
                </FormControl>
                <Box sx={{ flexGrow: 1 }} />
                <Tooltip title="Refresh">
                    <IconButton onClick={fetchInvitations} color="primary">
                        <Refresh />
                    </IconButton>
                </Tooltip>
                <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setCreateDialogOpen(true)}
                >
                    Create Invitation
                </Button>
            </Box>

            {/* Invitations Table */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    <TableContainer component={Paper} variant="outlined">
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Email</TableCell>
                                    <TableCell>Role</TableCell>
                                    <TableCell>Department</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Created</TableCell>
                                    <TableCell>Expires</TableCell>
                                    <TableCell align="right">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {invitations.map((invitation) => (
                                    <TableRow key={invitation.id}>
                                        <TableCell>{invitation.email}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={invitation.role.replace('_', ' ').toUpperCase()}
                                                size="small"
                                                color={getRoleColor(invitation.role)}
                                            />
                                        </TableCell>
                                        <TableCell>{invitation.department || '-'}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={getStatusLabel(invitation)}
                                                size="small"
                                                color={getStatusColor(invitation)}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            {new Date(invitation.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>
                                            {new Date(invitation.expires_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell align="right">
                                            {invitation.is_active && !invitation.used_at && (
                                                <>
                                                    <Tooltip title="Copy Invitation Link">
                                                        <IconButton
                                                            size="small"
                                                            onClick={() => handleCopyLink(invitation.invitation_link)}
                                                            color="primary"
                                                        >
                                                            <ContentCopy />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Resend Email">
                                                        <IconButton
                                                            size="small"
                                                            onClick={() => handleResendInvitation(invitation.id)}
                                                            color="info"
                                                        >
                                                            <Email />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Revoke">
                                                        <IconButton
                                                            size="small"
                                                            onClick={() => handleRevokeInvitation(invitation.id)}
                                                            color="error"
                                                        >
                                                            <Delete />
                                                        </IconButton>
                                                    </Tooltip>
                                                </>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {invitations.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center">
                                            No invitations found
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>

                    <TablePagination
                        component="div"
                        count={totalInvitations}
                        page={page}
                        onPageChange={handleChangePage}
                        rowsPerPage={rowsPerPage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                        rowsPerPageOptions={[5, 10, 25, 50]}
                    />
                </>
            )}

            {/* Create Invitation Dialog */}
            <Dialog open={createDialogOpen} onClose={handleCloseCreateDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {createdInvitation ? 'Invitation Created' : 'Create New Invitation'}
                </DialogTitle>
                <DialogContent>
                    {createdInvitation ? (
                        <Box sx={{ pt: 2 }}>
                            <Alert severity="success" sx={{ mb: 2 }}>
                                Invitation created successfully! Share the link below with the user.
                            </Alert>
                            <TextField
                                label="Invitation Link"
                                value={createdInvitation.invitation_link}
                                fullWidth
                                multiline
                                rows={3}
                                InputProps={{
                                    readOnly: true,
                                    endAdornment: (
                                        <InputAdornment position="end">
                                            <Tooltip title="Copy Link">
                                                <IconButton
                                                    onClick={() => handleCopyLink(createdInvitation.invitation_link)}
                                                    edge="end"
                                                >
                                                    <ContentCopy />
                                                </IconButton>
                                            </Tooltip>
                                        </InputAdornment>
                                    ),
                                }}
                            />
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                Expires: {new Date(createdInvitation.expires_at).toLocaleString()}
                            </Typography>
                        </Box>
                    ) : (
                        <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <TextField
                                label="Email"
                                type="email"
                                value={createForm.email}
                                onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                                fullWidth
                                required
                            />
                            <FormControl fullWidth required>
                                <InputLabel>Role</InputLabel>
                                <Select
                                    value={createForm.role}
                                    label="Role"
                                    onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                                >
                                    <MenuItem value="admin">Admin</MenuItem>
                                    <MenuItem value="operator">Operator</MenuItem>
                                    <MenuItem value="viewer">Viewer</MenuItem>
                                </Select>
                            </FormControl>
                            <TextField
                                label="Department (Optional)"
                                value={createForm.department}
                                onChange={(e) => setCreateForm({ ...createForm, department: e.target.value })}
                                fullWidth
                            />
                            <Alert severity="info">
                                An invitation link will be generated. The user must use this link to register within 48 hours.
                            </Alert>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    {createdInvitation ? (
                        <Button onClick={handleCloseCreateDialog} variant="contained">
                            Close
                        </Button>
                    ) : (
                        <>
                            <Button onClick={handleCloseCreateDialog}>Cancel</Button>
                            <Button 
                                onClick={handleCreateInvitation} 
                                variant="contained"
                                disabled={!createForm.email || !createForm.role}
                            >
                                Create Invitation
                            </Button>
                        </>
                    )}
                </DialogActions>
            </Dialog>

            {/* Snackbar for notifications */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
}

export default InvitationManagement;
