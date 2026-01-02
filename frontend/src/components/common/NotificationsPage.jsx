import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
  Button,
  Alert as MuiAlert,
  Tooltip,
  Divider
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  DoneAll as DoneAllIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import api from '../../services/api';

const NotificationsPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchNotifications();
  }, [activeTab]);

  const fetchNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      
      // Filter by tab
      if (activeTab === 1) {
        params.unread_only = true;
      } else if (activeTab === 2) {
        params.severity = 'critical';
      } else if (activeTab === 3) {
        params.category = 'detection';
      } else if (activeTab === 4) {
        params.category = 'system';
      }

      const response = await api.get('/notifications', { params });
      setNotifications(response.data.notifications);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}/mark-read`);
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, acknowledged: true } : n
        )
      );
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to mark as read');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.put('/notifications/mark-all-read');
      setNotifications(prev =>
        prev.map(n => ({ ...n, acknowledged: true }))
      );
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to mark all as read');
    }
  };

  const handleDelete = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete notification');
    }
  };

  const handleClearOld = async () => {
    try {
      await api.delete('/notifications/clear-old');
      fetchNotifications();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to clear old notifications');
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <CheckCircleIcon color="success" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      return format(new Date(timestamp), 'MMM d, yyyy h:mm a');
    } catch {
      return 'Unknown';
    }
  };

  const unreadCount = notifications.filter(n => !n.acknowledged).length;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Notifications
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {unreadCount > 0 && (
            <Button
              startIcon={<DoneAllIcon />}
              variant="outlined"
              onClick={handleMarkAllAsRead}
            >
              Mark All Read
            </Button>
          )}
          <Button
            startIcon={<DeleteIcon />}
            variant="outlined"
            color="error"
            onClick={handleClearOld}
          >
            Clear Old
          </Button>
        </Box>
      </Box>

      {error && (
        <MuiAlert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </MuiAlert>
      )}

      <Paper>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="All" />
          <Tab label={`Unread (${unreadCount})`} />
          <Tab label="Critical" />
          <Tab label="Detections" />
          <Tab label="System" />
        </Tabs>

        <Divider />

        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">Loading notifications...</Typography>
          </Box>
        ) : notifications.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">No notifications found</Typography>
          </Box>
        ) : (
          <List>
            {notifications.map((notification) => (
              <React.Fragment key={notification.id}>
                <ListItem
                  sx={{
                    bgcolor: notification.acknowledged ? 'transparent' : 'action.hover',
                    borderLeft: notification.acknowledged ? 'none' : `4px solid ${
                      notification.severity === 'critical' ? 'error.main' :
                      notification.severity === 'warning' ? 'warning.main' :
                      'info.main'
                    }`,
                    py: 2
                  }}
                >
                  <ListItemIcon>
                    {getSeverityIcon(notification.severity)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: notification.acknowledged ? 400 : 600 }}>
                          {notification.message}
                        </Typography>
                        <Chip
                          label={notification.severity}
                          size="small"
                          color={getSeverityColor(notification.severity)}
                        />
                        <Chip
                          label={notification.category}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          {formatTimestamp(notification.created_at)}
                        </Typography>
                        {notification.data && notification.data.details && (
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                            {notification.data.details}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {!notification.acknowledged && (
                      <Tooltip title="Mark as read">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleMarkAsRead(notification.id)}
                        >
                          <CheckCircleIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(notification.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
};

export default NotificationsPage;
