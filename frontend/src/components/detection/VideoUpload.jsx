import React, { useState } from 'react';
import API from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const VideoUpload = () => {
  const { token, isAuthenticated } = useAuth();
  const [videoFile, setVideoFile] = useState(null);
  const [location, setLocation] = useState('');
  const [cameraId, setCameraId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadedVideoId, setUploadedVideoId] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('');
  const [metadata, setMetadata] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file type
      const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv'];
      if (!validTypes.includes(file.type)) {
        setUploadMessage('Please select a valid video file (MP4, AVI, MOV, MKV)');
        return;
      }
      
      // Check file size (max 100MB)
      if (file.size > 100 * 1024 * 1024) {
        setUploadMessage('Video file size must be less than 100MB');
        return;
      }
      
      setVideoFile(file);
      setUploadMessage('');
    }
  };

  const handleUpload = async () => {
    if (!videoFile) {
      setUploadMessage('Please select a video file');
      return;
    }

    if (!isAuthenticated) {
      setUploadMessage('Authentication required. Please login first.');
      return;
    }

    setUploading(true);
    setUploadMessage('');
    setUploadedVideoId(null);

    const formData = new FormData();
    formData.append('video', videoFile);
    if (location) formData.append('location', location);
    if (cameraId) formData.append('camera_id', cameraId);

    try {
      const response = await API.post('/video/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setUploadedVideoId(response.data.video_id);
      setMetadata(response.data.metadata);
      setUploadMessage('Video uploaded successfully!');
      
      // Clear form
      setVideoFile(null);
      setLocation('');
      setCameraId('');
      document.getElementById('video-input').value = '';
      
    } catch (error) {
      setUploadMessage(
        error.response?.data?.message || 'Failed to upload video'
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="video-upload-container" style={{ padding: '20px', maxWidth: '800px' }}>
      <h2>Upload Video for Detection</h2>
      
      <div className="upload-form" style={{ marginTop: '20px' }}>
        <div className="form-group" style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Video File *
          </label>
          <input
            id="video-input"
            type="file"
            accept="video/mp4,video/avi,video/mov,video/mkv"
            onChange={handleFileChange}
            disabled={uploading}
            style={{
              padding: '10px',
              width: '100%',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
          />
          <small style={{ color: '#666', fontSize: '12px' }}>
            Supported: MP4, AVI, MOV, MKV (Max 100MB)
          </small>
        </div>

        <div className="form-group" style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Location (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g., Main Entrance, Gate 2, Mall"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            disabled={uploading}
            style={{
              padding: '10px',
              width: '100%',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
          />
        </div>

        <div className="form-group" style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Camera ID (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g., CAM-001, CCTV-A2"
            value={cameraId}
            onChange={(e) => setCameraId(e.target.value)}
            disabled={uploading}
            style={{
              padding: '10px',
              width: '100%',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={uploading || !videoFile}
          style={{
            padding: '12px 30px',
            backgroundColor: uploading || !videoFile ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: uploading || !videoFile ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {uploading ? 'Uploading...' : 'Upload Video'}
        </button>
      </div>

      {uploadMessage && (
        <div
          className="message"
          style={{
            marginTop: '20px',
            padding: '15px',
            borderRadius: '4px',
            backgroundColor: uploadedVideoId ? '#d4edda' : '#f8d7da',
            color: uploadedVideoId ? '#155724' : '#721c24',
            border: `1px solid ${uploadedVideoId ? '#c3e6cb' : '#f5c6cb'}`
          }}
        >
          {uploadMessage}
        </div>
      )}

      {uploadedVideoId && metadata && (
        <div className="upload-result" style={{ marginTop: '20px' }}>
          <h3>Upload Successful!</h3>
          <div
            className="video-info"
            style={{
              backgroundColor: '#f8f9fa',
              padding: '15px',
              borderRadius: '4px',
              marginTop: '10px'
            }}
          >
            <p><strong>Video ID:</strong> {uploadedVideoId}</p>
            <p><strong>Duration:</strong> {metadata.duration?.toFixed(2)} seconds</p>
            <p><strong>FPS:</strong> {metadata.fps?.toFixed(2)}</p>
            <p><strong>Resolution:</strong> {metadata.resolution}</p>
            <p><strong>Total Frames:</strong> {metadata.total_frames}</p>
          </div>
          
          <div style={{ marginTop: '15px' }}>
            <button
              onClick={() => window.location.href = `/videos/${uploadedVideoId}`}
              style={{
                padding: '10px 20px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '10px'
              }}
            >
              View Video Details
            </button>
            
            <button
              onClick={() => window.location.href = '/videos'}
              style={{
                padding: '10px 20px',
                backgroundColor: '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Go to Video List
            </button>
          </div>
        </div>
      )}

      <div className="instructions" style={{ marginTop: '30px', padding: '15px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
        <h4>Instructions:</h4>
        <ul style={{ marginLeft: '20px' }}>
          <li>Upload surveillance video footage for face detection</li>
          <li>Supported formats: MP4, AVI, MOV, MKV</li>
          <li>Maximum file size: 100MB</li>
          <li>After upload, go to Video List to process the video</li>
          <li>Processing will detect faces frame-by-frame and match against known criminals</li>
        </ul>
      </div>
    </div>
  );
};

export default VideoUpload;
