"""
Helper functions for video test generation.
"""
import cv2
import numpy as np
import tempfile
import os


def create_test_video(duration=2, fps=10, width=640, height=480, format='mp4'):
    """
    Create a test video file with random frames.
    
    Args:
        duration: Duration in seconds
        fps: Frames per second
        width: Frame width
        height: Frame height
        format: Video format (mp4, avi)
    
    Returns:
        Path to created video file
    """
    # Create temp file
    suffix = f'.{format}'
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    video_path = temp_file.name
    temp_file.close()
    
    # Determine codec based on format
    if format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    else:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    # Create video writer
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    # Generate frames
    num_frames = int(duration * fps)
    for i in range(num_frames):
        # Create a frame with random colors
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        # Add frame number text
        cv2.putText(frame, f'Frame {i}', (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        out.write(frame)
    
    out.release()
    return video_path


def create_test_video_with_faces(duration=2, fps=10):
    """
    Create a test video with synthetic face-like patterns.
    
    Args:
        duration: Duration in seconds
        fps: Frames per second
    
    Returns:
        Path to created video file
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    video_path = temp_file.name
    temp_file.close()
    
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    num_frames = int(duration * fps)
    for i in range(num_frames):
        # Create frame with light background
        frame = np.ones((height, width, 3), dtype=np.uint8) * 200
        
        # Draw face-like oval
        center_x, center_y = width // 2, height // 2
        cv2.ellipse(frame, (center_x, center_y), (80, 100), 0, 0, 360, (220, 180, 150), -1)
        
        # Draw eyes
        cv2.circle(frame, (center_x - 30, center_y - 20), 10, (50, 50, 50), -1)
        cv2.circle(frame, (center_x + 30, center_y - 20), 10, (50, 50, 50), -1)
        
        # Draw mouth
        cv2.ellipse(frame, (center_x, center_y + 30), (40, 20), 0, 0, 180, (100, 50, 50), 2)
        
        out.write(frame)
    
    out.release()
    return video_path
