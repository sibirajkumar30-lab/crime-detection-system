import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../../services/api';
import {
    Container,
    Paper,
    Typography,
    Box,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Chip,
    Alert,
    CircularProgress,
    TextField,
    InputAdornment,
    Checkbox,
    Toolbar,
    Tooltip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';

const CriminalList = () => {
    const navigate = useNavigate();
    const [criminals, setCriminals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [selected, setSelected] = useState([]);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [bulkDeleteLoading, setBulkDeleteLoading] = useState(false);

    useEffect(() => {
        fetchCriminals();
    }, []);

    const fetchCriminals = async () => {
        try {
            const response = await API.get('/criminals');
            setCriminals(response.data.criminals || []);
            setLoading(false);
        } catch (err) {
            setError('Failed to load criminals');
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this criminal record?')) {
            try {
                await API.delete(`/criminals/${id}`);
                fetchCriminals();
            } catch (err) {
                setError('Failed to delete criminal');
            }
        }
    };

    const handleSelectAll = (event) => {
        if (event.target.checked) {
            const allIds = filteredCriminals.map(c => c.id);
            setSelected(allIds);
        } else {
            setSelected([]);
        }
    };

    const handleSelectOne = (id) => {
        const selectedIndex = selected.indexOf(id);
        let newSelected = [];

        if (selectedIndex === -1) {
            newSelected = [...selected, id];
        } else {
            newSelected = selected.filter(selectedId => selectedId !== id);
        }

        setSelected(newSelected);
    };

    const handleBulkDelete = async () => {
        setBulkDeleteLoading(true);
        try {
            await Promise.all(selected.map(id => API.delete(`/criminals/${id}`)));
            
            setDeleteDialogOpen(false);
            setSelected([]);
            fetchCriminals();
        } catch (err) {
            setError('Failed to delete some criminals. Please try again.');
        } finally {
            setBulkDeleteLoading(false);
        }
    };

    const isSelected = (id) => selected.indexOf(id) !== -1;

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

    const filteredCriminals = criminals.filter(criminal =>
        criminal.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        criminal.crime_type.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4">Criminal Records</Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/criminals/add')}
                >
                    Add Criminal
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            {selected.length > 0 && (
                <Paper 
                    elevation={3} 
                    sx={{ 
                        mb: 2, 
                        backgroundColor: 'primary.light',
                        color: 'primary.contrastText'
                    }}
                >
                    <Toolbar>
                        <Typography variant="subtitle1" sx={{ flex: '1 1 100%' }}>
                            {selected.length} selected
                        </Typography>
                        <Tooltip title="Delete selected">
                            <Button
                                variant="contained"
                                color="error"
                                startIcon={<DeleteSweepIcon />}
                                onClick={() => setDeleteDialogOpen(true)}
                            >
                                Delete ({selected.length})
                            </Button>
                        </Tooltip>
                    </Toolbar>
                </Paper>
            )}

            <Paper elevation={3} sx={{ p: 3 }}>
                <TextField
                    fullWidth
                    placeholder="Search by name or crime type..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    sx={{ mb: 3 }}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                />

                {filteredCriminals.length === 0 ? (
                    <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                        No criminals found. Add your first criminal record.
                    </Typography>
                ) : (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell padding="checkbox">
                                        <Checkbox
                                            indeterminate={selected.length > 0 && selected.length < filteredCriminals.length}
                                            checked={filteredCriminals.length > 0 && selected.length === filteredCriminals.length}
                                            onChange={handleSelectAll}
                                            color="primary"
                                        />
                                    </TableCell>
                                    <TableCell><strong>Name</strong></TableCell>
                                    <TableCell><strong>Crime Type</strong></TableCell>
                                    <TableCell><strong>Status</strong></TableCell>
                                    <TableCell><strong>Danger Level</strong></TableCell>
                                    <TableCell><strong>Last Seen</strong></TableCell>
                                    <TableCell align="right"><strong>Actions</strong></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {filteredCriminals.map((criminal) => {
                                    const isItemSelected = isSelected(criminal.id);
                                    return (
                                        <TableRow 
                                            key={criminal.id} 
                                            hover
                                            selected={isItemSelected}
                                            sx={{ 
                                                backgroundColor: isItemSelected ? 'action.selected' : 'inherit',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            <TableCell padding="checkbox">
                                                <Checkbox
                                                    checked={isItemSelected}
                                                    onChange={() => handleSelectOne(criminal.id)}
                                                    color="primary"
                                                />
                                            </TableCell>
                                            <TableCell>{criminal.name}</TableCell>
                                            <TableCell>{criminal.crime_type}</TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={criminal.status}
                                                    color={getStatusColor(criminal.status)}
                                                    size="small"
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={criminal.danger_level}
                                                    color={getDangerColor(criminal.danger_level)}
                                                    size="small"
                                                />
                                            </TableCell>
                                            <TableCell>
                                                {criminal.last_seen_date 
                                                    ? new Date(criminal.last_seen_date).toLocaleDateString()
                                                    : 'N/A'
                                                }
                                            </TableCell>
                                            <TableCell align="right">
                                                <IconButton
                                                    size="small"
                                                    color="primary"
                                                    onClick={() => navigate(`/criminals/${criminal.id}`)}
                                                >
                                                    <VisibilityIcon />
                                                </IconButton>
                                                <IconButton
                                                    size="small"
                                                    color="primary"
                                                    onClick={() => navigate(`/criminals/edit/${criminal.id}`)}
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                                <IconButton
                                                    size="small"
                                                    color="error"
                                                    onClick={() => handleDelete(criminal.id)}
                                                >
                                                    <DeleteIcon />
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
            </Paper>

            <Dialog
                open={deleteDialogOpen}
                onClose={() => !bulkDeleteLoading && setDeleteDialogOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>Confirm Bulk Delete</DialogTitle>
                <DialogContent>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                        You are about to delete {selected.length} criminal record(s). This action cannot be undone.
                    </Alert>
                    <Typography variant="body2" gutterBottom>
                        The following records will be deleted:
                    </Typography>
                    <List dense>
                        {selected.slice(0, 10).map(id => {
                            const criminal = criminals.find(c => c.id === id);
                            return criminal ? (
                                <ListItem key={id}>
                                    <ListItemText
                                        primary={criminal.name}
                                        secondary={`${criminal.crime_type} - ${criminal.status}`}
                                    />
                                </ListItem>
                            ) : null;
                        })}
                        {selected.length > 10 && (
                            <ListItem>
                                <ListItemText secondary={`... and ${selected.length - 10} more`} />
                            </ListItem>
                        )}
                    </List>
                </DialogContent>
                <DialogActions>
                    <Button 
                        onClick={() => setDeleteDialogOpen(false)}
                        disabled={bulkDeleteLoading}
                    >
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleBulkDelete}
                        color="error"
                        variant="contained"
                        disabled={bulkDeleteLoading}
                        startIcon={bulkDeleteLoading ? <CircularProgress size={20} /> : <DeleteSweepIcon />}
                    >
                        {bulkDeleteLoading ? 'Deleting...' : 'Delete All'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default CriminalList;
