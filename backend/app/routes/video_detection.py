"""Video detection routes."""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import json
import logging

from app import db
from app.models.video_detection import VideoDetection, VideoFrameDetection
from app.services.video_processing_service import video_processing_service

logger = logging.getLogger(__name__)

bp = Blueprint('video_detection', __name__)


@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_video():
    """
    Upload video file for face detection processing.
    
    Request:
        - file: video file (mp4, avi, mov, etc.)
        - location: optional location string
        - camera_id: optional camera identifier
    
    Response:
        - video_id: ID of created VideoDetection record
        - metadata: video file metadata
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # Validate file
        if 'video' not in request.files:
            return jsonify({'message': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'message': 'No video file selected'}), 400
        
        location = request.form.get('location', '')
        camera_id = request.form.get('camera_id', '')
        
        # Save video file
        video_path = video_processing_service.save_video_upload(file)
        if not video_path:
            return jsonify({'message': 'Invalid video format or upload failed'}), 400
        
        # Extract video metadata
        metadata = video_processing_service.get_video_metadata(video_path)
        
        # Create VideoDetection record
        video_detection = VideoDetection(
            video_filename=secure_filename(file.filename),
            video_path=video_path,
            uploaded_by=current_user_id,
            duration_seconds=metadata.get('duration_seconds'),
            fps=metadata.get('fps'),
            total_frames=metadata.get('total_frames'),
            resolution_width=metadata.get('width'),
            resolution_height=metadata.get('height'),
            file_size_mb=metadata.get('file_size_mb'),
            location=location,
            camera_id=camera_id,
            processing_status='pending'
        )
        
        db.session.add(video_detection)
        db.session.commit()
        
        logger.info(f"Video uploaded: {video_detection.id} by user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Video uploaded successfully',
            'video_id': video_detection.id,
            'metadata': metadata
        }), 201
        
    except Exception as e:
        logger.error(f"Video upload failed: {str(e)}")
        return jsonify({'message': f'Video upload failed: {str(e)}'}), 500


@bp.route('/process/<int:video_id>', methods=['POST'])
@jwt_required()
def process_video(video_id):
    """
    Start processing video for face detection.
    
    Args:
        video_id: ID of uploaded video
    
    Request Body:
        - frame_skip: Process every Nth frame (default: 5)
        - confidence_threshold: Minimum confidence for match (default: 0.70)
    
    Response:
        - processing_started: boolean
        - video_id: ID of video being processed
    """
    try:
        video_detection = VideoDetection.query.get(video_id)
        if not video_detection:
            return jsonify({'message': 'Video not found'}), 404
        
        if video_detection.processing_status == 'processing':
            return jsonify({'message': 'Video is already being processed'}), 400
        
        if video_detection.processing_status == 'completed':
            return jsonify({'message': 'Video has already been processed'}), 400
        
        # Get processing parameters
        data = request.get_json() or {}
        frame_skip = data.get('frame_skip', 5)
        confidence_threshold = data.get('confidence_threshold', 0.70)
        
        # Start processing (in a real production app, this should be async/background task)
        # For now, we'll process synchronously but could use Celery/RQ for async
        result = video_processing_service.process_video(
            video_id,
            frame_skip=frame_skip,
            confidence_threshold=confidence_threshold
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Video processing completed',
                'video_id': video_id,
                'results': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Processing failed'),
                'video_id': video_id
            }), 500
        
    except Exception as e:
        logger.error(f"Video processing failed: {str(e)}")
        return jsonify({'message': f'Video processing failed: {str(e)}'}), 500


@bp.route('/list', methods=['GET'])
@jwt_required()
def list_videos():
    """
    Get list of uploaded videos.
    
    Query Parameters:
        - limit: Number of videos to return (default: 20)
        - status: Filter by processing status (pending/processing/completed/failed)
    
    Response:
        - videos: List of video detection records
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        status_filter = request.args.get('status', None)
        
        query = VideoDetection.query
        
        if status_filter:
            query = query.filter_by(processing_status=status_filter)
        
        videos = query.order_by(
            VideoDetection.upload_date.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'videos': [v.to_dict() for v in videos],
            'count': len(videos)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to list videos: {str(e)}")
        return jsonify({'message': f'Failed to list videos: {str(e)}'}), 500


@bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video_details(video_id):
    """
    Get detailed results for a specific video.
    
    Args:
        video_id: ID of video detection
    
    Response:
        - video: Complete video detection data including frame detections
    """
    try:
        video = VideoDetection.query.get(video_id)
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        # Parse summary report if available
        summary = None
        if video.summary_report:
            try:
                summary = json.loads(video.summary_report)
            except:
                pass
        
        return jsonify({
            'success': True,
            'video': video.to_dict(include_frames=True),
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get video details: {str(e)}")
        return jsonify({'message': f'Failed to get video details: {str(e)}'}), 500


@bp.route('/<int:video_id>/frames', methods=['GET'])
@jwt_required()
def get_video_frames(video_id):
    """
    Get frame detection results for a video.
    
    Args:
        video_id: ID of video detection
    
    Query Parameters:
        - matched_only: Only return frames with matches (default: false)
    
    Response:
        - frames: List of frame detections
    """
    try:
        video = VideoDetection.query.get(video_id)
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        matched_only = request.args.get('matched_only', 'false').lower() == 'true'
        
        query = VideoFrameDetection.query.filter_by(video_detection_id=video_id)
        
        if matched_only:
            query = query.filter(VideoFrameDetection.criminal_id.isnot(None))
        
        frames = query.order_by(VideoFrameDetection.frame_number).all()
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'frames': [f.to_dict(include_criminal=True) for f in frames],
            'count': len(frames)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get video frames: {str(e)}")
        return jsonify({'message': f'Failed to get video frames: {str(e)}'}), 500


@bp.route('/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    """
    Delete a video detection record and associated files.
    
    Args:
        video_id: ID of video to delete
    
    Response:
        - success: boolean
        - message: status message
    """
    try:
        video = VideoDetection.query.get(video_id)
        if not video:
            return jsonify({'message': 'Video not found'}), 404
        
        # Delete video file
        if os.path.exists(video.video_path):
            os.remove(video.video_path)
        
        # Delete annotated video if exists
        if video.annotated_video_path and os.path.exists(video.annotated_video_path):
            os.remove(video.annotated_video_path)
        
        # Delete frame images
        for frame in video.frame_detections:
            if frame.frame_image_path and os.path.exists(frame.frame_image_path):
                os.remove(frame.frame_image_path)
        
        # Delete database record (cascade will delete frame detections)
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete video: {str(e)}")
        return jsonify({'message': f'Failed to delete video: {str(e)}'}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_video_stats():
    """
    Get statistics about video processing.
    
    Response:
        - total_videos: Total number of videos
        - videos_by_status: Count by processing status
        - total_faces_detected: Sum of all faces detected
        - total_criminals_matched: Sum of unique criminals matched
    """
    try:
        total_videos = VideoDetection.query.count()
        
        pending = VideoDetection.query.filter_by(processing_status='pending').count()
        processing = VideoDetection.query.filter_by(processing_status='processing').count()
        completed = VideoDetection.query.filter_by(processing_status='completed').count()
        failed = VideoDetection.query.filter_by(processing_status='failed').count()
        
        # Sum statistics from completed videos
        completed_videos = VideoDetection.query.filter_by(processing_status='completed').all()
        total_faces = sum(v.total_faces_detected or 0 for v in completed_videos)
        total_criminals = sum(v.unique_criminals_matched or 0 for v in completed_videos)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_videos': total_videos,
                'videos_by_status': {
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'failed': failed
                },
                'total_faces_detected': total_faces,
                'total_criminals_matched': total_criminals
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get video stats: {str(e)}")
        return jsonify({'message': f'Failed to get video stats: {str(e)}'}), 500
