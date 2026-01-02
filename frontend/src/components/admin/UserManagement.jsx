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
    TextField,
    MenuItem,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControl,
    InputLabel,
    Select,
    Alert,
    Snackbar,
    Tooltip,
    CircularProgress
} from '@mui/material';
import {
    Edit,
    Block,
    CheckCircle,
    Refresh
} from '@mui/icons-material';
import { adminAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

function UserManagement() {
    const { user: currentUser } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalUsers, setTotalUsers] = useState(0);
    const [roleFilter, setRoleFilter] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    
    // Edit user dialog
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [editForm, setEditForm] = useState({ role: '', phone: '' });
    
    // Snackbar
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

    useEffect(() => {
        fetchUsers();
    }, [page, rowsPerPage, roleFilter]);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const params = {
                page: page + 1,
                per_page: rowsPerPage,
            };
            if (roleFilter) params.role = roleFilter;
            
            const response = await adminAPI.getUsers(params);
            setUsers(response.data.users);
            setTotalUsers(response.data.total);
        } catch (error) {
            showSnackbar('Failed to fetch users: ' + (error.response?.data?.error || error.message), 'error');
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

    const handleEditClick = (user) => {
        setEditingUser(user);
        setEditForm({
            role: user.role,
            phone: user.phone || ''
        });
        setEditDialogOpen(true);
    };

    const handleEditSubmit = async () => {
        try {
            await adminAPI.updateUser(editingUser.id, editForm);
            showSnackbar('User updated successfully', 'success');
            setEditDialogOpen(false);
            fetchUsers();
        } catch (error) {
            showSnackbar('Failed to update user: ' + (error.response?.data?.error || error.message), 'error');
        }
    };

    const handleToggleActive = async (user) => {
        // Prevent deactivating own account
        if (user.id === currentUser.id) {
            showSnackbar('You cannot deactivate your own account', 'warning');
            return;
        }

        try {
            if (user.is_active) {
                await adminAPI.deactivateUser(user.id);
                showSnackbar('User deactivated successfully', 'success');
            } else {
                await adminAPI.activateUser(user.id);
                showSnackbar('User activated successfully', 'success');
            }
            fetchUsers();
        } catch (error) {
            showSnackbar('Failed to toggle user status: ' + (error.response?.data?.error || error.message), 'error');
        }
    };

    const showSnackbar = (message, severity = 'info') => {
        setSnackbar({ open: true, message, severity });
    };

    const handleCloseSnackbar = () => {
        setSnackbar({ ...snackbar, open: false });
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

    const filteredUsers = users.filter(user =>
        searchTerm === '' ||
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <Box>
            {/* Filters */}
            <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
                <TextField
                    label="Search users"
                    variant="outlined"
                    size="small"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    sx={{ flexGrow: 1 }}
                />
                <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel>Role Filter</InputLabel>
                    <Select
                        value={roleFilter}
                        label="Role Filter"
                        onChange={(e) => setRoleFilter(e.target.value)}
                    >
                        <MenuItem value="">All Roles</MenuItem>
                        <MenuItem value="super_admin">Super Admin</MenuItem>
                        <MenuItem value="admin">Admin</MenuItem>
                        <MenuItem value="operator">Operator</MenuItem>
                        <MenuItem value="viewer">Viewer</MenuItem>
                    </Select>
                </FormControl>
                <Tooltip title="Refresh">
                    <IconButton onClick={fetchUsers} color="primary">
                        <Refresh />
                    </IconButton>
                </Tooltip>
            </Box>

            {/* Users Table */}
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
                                    <TableCell>Username</TableCell>
                                    <TableCell>Email</TableCell>
                                    <TableCell>Role</TableCell>
                                    <TableCell>Phone</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Created</TableCell>
                                    <TableCell align="right">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {filteredUsers.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell>{user.username}</TableCell>
                                        <TableCell>{user.email}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={user.role.replace('_', ' ').toUpperCase()}
                                                size="small"
                                                color={getRoleColor(user.role)}
                                            />
                                        </TableCell>
                                        <TableCell>{user.phone || '-'}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={user.is_active ? 'Active' : 'Inactive'}
                                                size="small"
                                                color={user.is_active ? 'success' : 'default'}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell align="right">
                                            <Tooltip title="Edit User">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleEditClick(user)}
                                                    color="primary"
                                                >
                                                    <Edit />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title={user.is_active ? 'Deactivate' : 'Activate'}>
                                                <span>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleToggleActive(user)}
                                                        color={user.is_active ? 'error' : 'success'}
                                                        disabled={user.id === currentUser.id}
                                                    >
                                                        {user.is_active ? <Block /> : <CheckCircle />}
                                                    </IconButton>
                                                </span>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {filteredUsers.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center">
                                            No users found
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>

                    <TablePagination
                        component="div"
                        count={totalUsers}
                        page={page}
                        onPageChange={handleChangePage}
                        rowsPerPage={rowsPerPage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                        rowsPerPageOptions={[5, 10, 25, 50]}
                    />
                </>
            )}

            {/* Edit User Dialog */}
            <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Edit User</DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <TextField
                            label="Username"
                            value={editingUser?.username || ''}
                            disabled
                            fullWidth
                        />
                        <TextField
                            label="Email"
                            value={editingUser?.email || ''}
                            disabled
                            fullWidth
                        />
                        <FormControl fullWidth>
                            <InputLabel>Role</InputLabel>
                            <Select
                                value={editForm.role}
                                label="Role"
                                onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                            >
                                <MenuItem value="super_admin">Super Admin</MenuItem>
                                <MenuItem value="admin">Admin</MenuItem>
                                <MenuItem value="operator">Operator</MenuItem>
                                <MenuItem value="viewer">Viewer</MenuItem>
                            </Select>
                        </FormControl>
                        <TextField
                            label="Phone"
                            value={editForm.phone}
                            onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                            fullWidth
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleEditSubmit} variant="contained">
                        Save Changes
                    </Button>
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

export default UserManagement;
