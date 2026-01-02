import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    ListItemButton,
    Box,
    Divider,
    Typography
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import NotificationsIcon from '@mui/icons-material/Notifications';
import BarChartIcon from '@mui/icons-material/BarChart';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { useAuth } from '../../context/AuthContext';

const drawerWidth = 240;

const Sidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user } = useAuth();

    const menuItems = [
        { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
        { text: 'Analytics', icon: <BarChartIcon />, path: '/analytics' },
        { text: 'Criminals', icon: <PeopleIcon />, path: '/criminals' },
        { text: 'Image Detection', icon: <CameraAltIcon />, path: '/detection' },
        { text: 'Video Detection', icon: <VideoLibraryIcon />, path: '/videos' },
        { text: 'Alerts', icon: <NotificationsIcon />, path: '/alerts' }
    ];

    // Add admin menu item if user is admin
    const adminMenuItem = { text: 'Admin Panel', icon: <AdminPanelSettingsIcon />, path: '/admin' };
    const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: drawerWidth,
                    boxSizing: 'border-box',
                    top: 64, // Height of navbar
                    height: 'calc(100% - 64px)'
                },
            }}
        >
            <Box sx={{ overflow: 'auto' }}>
                <List>
                    {menuItems.map((item) => (
                        <ListItem key={item.text} disablePadding>
                            <ListItemButton
                                selected={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
                                onClick={() => navigate(item.path)}
                            >
                                <ListItemIcon>{item.icon}</ListItemIcon>
                                <ListItemText primary={item.text} />
                            </ListItemButton>
                        </ListItem>
                    ))}
                    
                    {isAdmin && (
                        <>
                            <Divider sx={{ my: 1 }} />
                            <ListItem disablePadding>
                                <ListItemButton
                                    selected={location.pathname === adminMenuItem.path}
                                    onClick={() => navigate(adminMenuItem.path)}
                                >
                                    <ListItemIcon>{adminMenuItem.icon}</ListItemIcon>
                                    <ListItemText primary={adminMenuItem.text} />
                                </ListItemButton>
                            </ListItem>
                        </>
                    )}
                </List>
            </Box>
        </Drawer>
    );
};

export default Sidebar;
