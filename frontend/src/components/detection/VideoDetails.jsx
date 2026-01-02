import React, { useState, useEffect } from 'react';
import API from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useParams, useNavigate } from 'react-router-dom';

const VideoDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [video, setVideo] = useState(null);
  const [frames, setFrames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showMatchedOnly, setShowMatchedOnly] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState('');

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchVideoDetails();
    fetchFrames();
  }, [id, showMatchedOnly]);

  const fetchVideoDetails = async () => {
    try {
      const response = await API.get(`/video/${id}`);
      setVideo(response.data.video);
    } catch (error) {
      setMessage('Failed to fetch video details');
    } finally {
      setLoading(false);
    }
  };

  const fetchFrames = async () => {
    try {
      const url = showMatchedOnly
        ? `/video/${id}/frames?matched_only=true`
        : `/video/${id}/frames`;
      
      const response = await API.get(url);
      
      setFrames(response.data.frames || []);
    } catch (error) {
      console.error('Failed to fetch frames');
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    setMessage('');
    
    try {
      await API.post(
        `/video/process/${id}`,
        { frame_skip: 5, confidence_threshold: 0.75 }
      );
      
      setMessage('Video processing completed! Refreshing data...');
      setTimeout(() => {
        fetchVideoDetails();
        fetchFrames();
      }, 1000);
    } catch (error) {
      setMessage(error.response?.data?.message || 'Processing failed');
    } finally {
      setProcessing(false);
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
        padding: '6px 15px',
        borderRadius: '15px',
        backgroundColor: statusColor,
        color: 'white',
        fontSize: '14px',
        fontWeight: 'bold'
      }}>
        {statusText}
      </span>
    );
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading video details...</div>;
  }

  if (!video) {
    return <div style={{ padding: '20px' }}>Video not found</div>;
  }

  return (
    <div className="video-details-container" style={{ padding: '20px', maxWidth: '1200px' }}>
      <button
        onClick={() => navigate('/videos')}
        style={{
          padding: '8px 15px',
          marginBottom: '20px',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        ← Back to List
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Video Details</h2>
        {video.processing_status === 'pending' && (
          <button
            onClick={handleProcess}
            disabled={processing}
            style={{
              padding: '10px 20px',
              backgroundColor: processing ? '#ccc' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: processing ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            {processing ? 'Processing...' : 'Process Video Now'}
          </button>
        )}
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

      {/* Video Info Card */}
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ marginBottom: '15px' }}>
          <h3 style={{ marginBottom: '10px' }}>{video.video_filename}</h3>
          {getStatusBadge(video.processing_status)}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', fontSize: '14px' }}>
          <div>
            <p><strong>Video ID:</strong> {video.id}</p>
            <p><strong>Location:</strong> {video.location || 'N/A'}</p>
            <p><strong>Camera ID:</strong> {video.camera_id || 'N/A'}</p>
            <p><strong>Uploaded:</strong> {(() => {
              const utcDate = new Date(video.upload_date);
              const istDate = new Date(utcDate.getTime() + (5.5 * 60 * 60 * 1000));
              return istDate.toLocaleString('en-IN', { 
                timeZone: 'Asia/Kolkata',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
              }) + ' IST';
            })()}</p>
          </div>
          
          <div>
            <p><strong>Duration:</strong> {video.duration_seconds?.toFixed(2)} seconds</p>
            <p><strong>FPS:</strong> {video.fps?.toFixed(0)}</p>
            <p><strong>Resolution:</strong> {video.resolution}</p>
            <p><strong>Total Frames:</strong> {video.total_frames}</p>
          </div>
        </div>

        {video.processing_status === 'completed' && (
          <div style={{
            marginTop: '20px',
            padding: '15px',
            backgroundColor: '#e7f3ff',
            borderRadius: '4px'
          }}>
            <h4 style={{ marginBottom: '10px' }}>Detection Results</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
              <div>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
                  {video.total_faces_detected || 0}
                </p>
                <p style={{ fontSize: '12px', color: '#666' }}>Total Faces Detected</p>
              </div>
              <div>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                  {video.unique_criminals_matched || 0}
                </p>
                <p style={{ fontSize: '12px', color: '#666' }}>Criminals Matched</p>
              </div>
              <div>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                  {frames.length}
                </p>
                <p style={{ fontSize: '12px', color: '#666' }}>Frames with Detections</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Frame Detections */}
      {video.processing_status === 'completed' && (
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3>Frame Detections ({frames.length})</h3>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={showMatchedOnly}
                onChange={(e) => setShowMatchedOnly(e.target.checked)}
              />
              <span style={{ fontSize: '14px' }}>Show only criminal matches</span>
            </label>
          </div>

          {frames.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
              {showMatchedOnly ? 'No criminal matches found' : 'No faces detected in this video'}
            </p>
          ) : (
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead style={{ backgroundColor: '#f8f9fa', position: 'sticky', top: 0 }}>
                  <tr>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Frame</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Time</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Criminal</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Confidence</th>
                    <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Location</th>
                  </tr>
                </thead>
                <tbody>
                  {frames.map((frame, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '10px' }}>#{frame.frame_number}</td>
                      <td style={{ padding: '10px' }}>{frame.timestamp_seconds?.toFixed(2)}s</td>
                      <td style={{ padding: '10px' }}>
                        {frame.criminal?.name ? (
                          <span style={{ color: '#dc3545', fontWeight: 'bold' }}>
                            {frame.criminal.name}
                          </span>
                        ) : frame.criminal_id ? (
                          <span style={{ color: '#dc3545', fontWeight: 'bold' }}>
                            Criminal #{frame.criminal_id}
                          </span>
                        ) : (
                          <span style={{ color: '#6c757d' }}>Unknown</span>
                        )}
                      </td>
                      <td style={{ padding: '10px' }}>
                        {frame.confidence_score ? (
                          <span style={{
                            padding: '2px 8px',
                            borderRadius: '10px',
                            backgroundColor: frame.confidence_score > 0.85 ? '#28a745' : '#ffc107',
                            color: 'white',
                            fontSize: '12px'
                          }}>
                            {(frame.confidence_score * 100).toFixed(1)}%
                          </span>
                        ) : 'N/A'}
                      </td>
                      <td style={{ padding: '10px', fontSize: '12px', color: '#666' }}>
                        {frame.face_coordinates ? 
                          frame.face_coordinates : 
                          'N/A'
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {video.processing_status === 'failed' && (
        <div style={{
          padding: '20px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          marginTop: '20px'
        }}>
          <strong>Processing Failed</strong>
          <p>This video could not be processed. Please try uploading again or contact support.</p>
        </div>
      )}
    </div>
  );
};

export default VideoDetails;
