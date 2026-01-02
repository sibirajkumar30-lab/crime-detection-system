import React, { useState, useEffect } from 'react';
import API from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const VideoList = () => {
  const navigate = useNavigate();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [message, setMessage] = useState('');

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchVideos();
  }, [statusFilter]);

  const fetchVideos = async () => {
    setLoading(true);
    try {
      const url = statusFilter === 'all' 
        ? '/video/list'
        : `/video/list?status=${statusFilter}`;
      
      const response = await API.get(url);
      
      setVideos(response.data.videos || []);
    } catch (error) {
      setMessage(error.response?.data?.message || 'Failed to fetch videos');
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async (videoId) => {
    setMessage('');
    try {
      await API.post(
        `/video/process/${videoId}`,
        { frame_skip: 5, confidence_threshold: 0.75 }
      );
      
      setMessage('Video processing started! Refresh to see updates.');
      fetchVideos();
    } catch (error) {
      setMessage(error.response?.data?.message || 'Failed to process video');
    }
  };

  const handleDelete = async (videoId) => {
    if (!window.confirm('Are you sure you want to delete this video?')) return;
    
    try {
      await API.delete(`/video/${videoId}`);
      
      setMessage('Video deleted successfully');
      fetchVideos();
    } catch (error) {
      setMessage(error.response?.data?.message || 'Failed to delete video');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: '#ffc107',
      processing: '#17a2b8',
      completed: '#28a745',
      failed: '#dc3545'
    };
    
    // Handle undefined or null status
    const statusText = (status || 'unknown').toUpperCase();
    const statusColor = colors[status] || '#6c757d';
    
    return (
      <span style={{
        padding: '4px 12px',
        borderRadius: '12px',
        backgroundColor: statusColor,
        color: 'white',
        fontSize: '12px',
        fontWeight: 'bold'
      }}>
        {statusText}
      </span>
    );
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading videos...</div>;
  }

  return (
    <div className="video-list-container" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Video Detections</h2>
        <button
          onClick={() => navigate('/video/upload')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          + Upload New Video
        </button>
      </div>

      <div className="filters" style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '10px', fontWeight: 'bold' }}>Filter by Status:</label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ddd'
          }}
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
        
        <button
          onClick={fetchVideos}
          style={{
            marginLeft: '10px',
            padding: '8px 15px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Refresh
        </button>
      </div>

      {message && (
        <div style={{
          padding: '10px',
          marginBottom: '20px',
          borderRadius: '4px',
          backgroundColor: message.includes('Failed') ? '#f8d7da' : '#d4edda',
          color: message.includes('Failed') ? '#721c24' : '#155724'
        }}>
          {message}
        </div>
      )}

      {videos.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px'
        }}>
          <p style={{ fontSize: '18px', color: '#666' }}>No videos found</p>
          <button
            onClick={() => navigate('/video/upload')}
            style={{
              marginTop: '15px',
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Upload Your First Video
          </button>
        </div>
      ) : (
        <div className="video-cards" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
          {videos.map((video) => (
            <div
              key={video.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: 'white',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
            >
              <div style={{ marginBottom: '10px' }}>
                <strong style={{ fontSize: '16px' }}>{video.video_filename}</strong>
                <div style={{ marginTop: '5px' }}>{getStatusBadge(video.processing_status)}</div>
              </div>

              <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                <p><strong>Location:</strong> {video.location || 'N/A'}</p>
                <p><strong>Camera:</strong> {video.camera_id || 'N/A'}</p>
                <p><strong>Duration:</strong> {video.duration_seconds?.toFixed(2)}s</p>
                <p><strong>FPS:</strong> {video.fps?.toFixed(0)}</p>
                <p><strong>Uploaded:</strong> {new Date(video.upload_date).toLocaleString()}</p>
              </div>

              {video.processing_status === 'completed' && (
                <div style={{
                  padding: '10px',
                  backgroundColor: '#e7f3ff',
                  borderRadius: '4px',
                  marginBottom: '10px',
                  fontSize: '14px'
                }}>
                  <p><strong>Faces Detected:</strong> {video.total_faces_detected || 0}</p>
                  <p><strong>Criminals Matched:</strong> {video.unique_criminals_matched || 0}</p>
                  {video.matched_criminals && video.matched_criminals.length > 0 && (
                    <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #ccc' }}>
                      <strong style={{ color: '#dc3545' }}>Matched:</strong>
                      <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                        {video.matched_criminals.map((criminal, idx) => (
                          <li key={idx} style={{ color: '#dc3545', fontWeight: 'bold' }}>
                            {criminal.name} ({criminal.crime_type})
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', gap: '8px', marginTop: '15px' }}>
                <button
                  onClick={() => navigate(`/videos/${video.id}`)}
                  style={{
                    flex: 1,
                    padding: '8px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  View Details
                </button>

                {video.processing_status === 'pending' && (
                  <button
                    onClick={() => handleProcess(video.id)}
                    style={{
                      flex: 1,
                      padding: '8px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    Process
                  </button>
                )}

                <button
                  onClick={() => handleDelete(video.id)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VideoList;
