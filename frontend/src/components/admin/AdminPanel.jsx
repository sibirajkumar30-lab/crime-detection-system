import React, { useState } from 'react';
import {
    Box,
    Container,
    Paper,
    Tabs,
    Tab,
    Typography,
    Alert
} from '@mui/material';
import { People, Email } from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import UserManagement from './UserManagement';
import InvitationManagement from './InvitationManagement';

function TabPanel({ children, value, index, ...other }) {
    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`admin-tabpanel-${index}`}
            aria-labelledby={`admin-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

function AdminPanel() {
    const [currentTab, setCurrentTab] = useState(0);
    const { user } = useAuth();

    const handleTabChange = (event, newValue) => {
        setCurrentTab(newValue);
    };

    // Check if user is admin
    if (!user || (user.role !== 'admin' && user.role !== 'super_admin')) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Alert severity="error">
                    Access Denied. You must be an administrator to access this page.
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
                Admin Panel
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Manage users and invitations for the system
            </Typography>

            <Paper sx={{ width: '100%' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={currentTab} onChange={handleTabChange} aria-label="admin tabs">
                        <Tab 
                            icon={<People />} 
                            label="User Management" 
                            iconPosition="start"
                            id="admin-tab-0"
                            aria-controls="admin-tabpanel-0"
                        />
                        <Tab 
                            icon={<Email />} 
                            label="Invitations" 
                            iconPosition="start"
                            id="admin-tab-1"
                            aria-controls="admin-tabpanel-1"
                        />
                    </Tabs>
                </Box>

                <TabPanel value={currentTab} index={0}>
                    <UserManagement />
                </TabPanel>

                <TabPanel value={currentTab} index={1}>
                    <InvitationManagement />
                </TabPanel>
            </Paper>
        </Container>
    );
}

export default AdminPanel;
