import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Box } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import PrivateRoute from './components/common/PrivateRoute';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Dashboard from './components/dashboard/Dashboard';
import AnalyticsDashboard from './components/dashboard/AnalyticsDashboard';
import CriminalList from './components/criminal/CriminalList';
import CriminalForm from './components/criminal/CriminalForm';
import CriminalDetail from './components/criminal/CriminalDetail';
import UploadDetection from './components/detection/UploadDetection';
import VideoUpload from './components/detection/VideoUpload';
import VideoList from './components/detection/VideoList';
import VideoDetails from './components/detection/VideoDetails';
import AdminPanel from './components/admin/AdminPanel';
import Profile from './components/user/Profile';
import AlertsList from './components/alerts/AlertsList';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    error: {
      main: '#d32f2f',
    },
  },
});

const AppContent = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const showSidebar = isAuthenticated && !['/login', '/register'].includes(location.pathname);

  return (
    <>
      <Navbar />
      <Box sx={{ display: 'flex' }}>
        {showSidebar && <Sidebar />}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            bgcolor: 'background.default',
            p: 0,
            marginLeft: showSidebar ? '240px' : 0,
            minHeight: 'calc(100vh - 64px)'
          }}
        >
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <PrivateRoute>
                  <AnalyticsDashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/criminals"
              element={
                <PrivateRoute>
                  <CriminalList />
                </PrivateRoute>
              }
            />
            <Route
              path="/criminals/add"
              element={
                <PrivateRoute>
                  <CriminalForm />
                </PrivateRoute>
              }
            />
            <Route
              path="/criminals/edit/:id"
              element={
                <PrivateRoute>
                  <CriminalForm />
                </PrivateRoute>
              }
            />
            <Route
              path="/criminals/:id"
              element={
                <PrivateRoute>
                  <CriminalDetail />
                </PrivateRoute>
              }
            />
            <Route
              path="/detection"
              element={
                <PrivateRoute>
                  <UploadDetection />
                </PrivateRoute>
              }
            />
            <Route
              path="/video/upload"
              element={
                <PrivateRoute>
                  <VideoUpload />
                </PrivateRoute>
              }
            />
            <Route
              path="/videos"
              element={
                <PrivateRoute>
                  <VideoList />
                </PrivateRoute>
              }
            />
            <Route
              path="/videos/:id"
              element={
                <PrivateRoute>
                  <VideoDetails />
                </PrivateRoute>
              }
            />
            <Route
              path="/alerts"
              element={
                <PrivateRoute>
                  <AlertsList />
                </PrivateRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <PrivateRoute>
                  <Profile />
                </PrivateRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <PrivateRoute>
                  <AdminPanel />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Box>
      </Box>
    </>
  );
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
