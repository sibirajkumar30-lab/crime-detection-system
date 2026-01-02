"""Dashboard statistics routes."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app import db
from app.models.criminal import Criminal
from app.models.detection_log import DetectionLog
from app.models.user import User
from app.models.alert import Alert
from app.models.video_detection import VideoDetection, VideoFrameDetection
from app.services.analytics_service import AnalyticsService

bp = Blueprint('dashboard', __name__)


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics."""
    try:
        total_criminals = Criminal.query.count()
        wanted_criminals = Criminal.query.filter_by(status='wanted').count()
        arrested_criminals = Criminal.query.filter_by(status='arrested').count()
        total_detections = DetectionLog.query.count()
        total_users = User.query.count()
        total_alerts = Alert.query.count()
        pending_verifications = DetectionLog.query.filter_by(status='pending').count()
        verified_detections = DetectionLog.query.filter_by(status='verified').count()
        false_positives = DetectionLog.query.filter_by(status='false_positive').count()
        
        # Video statistics
        total_videos = VideoDetection.query.count()
        videos_processing = VideoDetection.query.filter_by(processing_status='processing').count()
        videos_completed = VideoDetection.query.filter_by(processing_status='completed').count()
        total_video_detections = VideoFrameDetection.query.count()
        
        # Calculate accuracy rate
        total_reviewed = verified_detections + false_positives
        accuracy_rate = (verified_detections / total_reviewed * 100) if total_reviewed > 0 else 0
        
        return jsonify({
            'total_criminals': total_criminals,
            'wanted_criminals': wanted_criminals,
            'arrested': arrested_criminals,
            'total_detections': total_detections,
            'pending_verifications': pending_verifications,
            'verified_detections': verified_detections,
            'false_positives': false_positives,
            'total_users': total_users,
            'total_alerts': total_alerts,
            'total_videos': total_videos,
            'videos_processing': videos_processing,
            'videos_completed': videos_completed,
            'total_video_detections': total_video_detections,
            'accuracy_rate': round(accuracy_rate, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch stats: {str(e)}'}), 500


@bp.route('/recent-detections', methods=['GET'])
@jwt_required()
def get_recent_detections():
    """Get recent detections."""
    try:
        limit = 10
        detections = DetectionLog.query.order_by(
            DetectionLog.detected_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'detections': [detection.to_dict(include_criminal=True) for detection in detections]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch recent detections: {str(e)}'}), 500


@bp.route('/top-criminals', methods=['GET'])
@jwt_required()
def get_top_criminals():
    """Get most detected criminals."""
    try:
        limit = int(request.args.get('limit', 5))
        
        # Query for criminals with most detections
        top_criminals = db.session.query(
            Criminal,
            func.count(DetectionLog.id).label('detection_count')
        ).join(
            DetectionLog, Criminal.id == DetectionLog.criminal_id
        ).group_by(
            Criminal.id
        ).order_by(
            func.count(DetectionLog.id).desc()
        ).limit(limit).all()
        
        result = []
        for criminal, count in top_criminals:
            criminal_dict = criminal.to_dict()
            criminal_dict['detection_count'] = count
            result.append(criminal_dict)
        
        return jsonify({
            'criminals': result
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch top criminals: {str(e)}'}), 500


@bp.route('/detections-timeline', methods=['GET'])
@jwt_required()
def get_detections_timeline():
    """Get detection counts over time."""
    try:
        days = int(request.args.get('days', 7))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query detections grouped by date
        detections_by_date = db.session.query(
            func.date(DetectionLog.detected_at).label('date'),
            func.count(DetectionLog.id).label('count')
        ).filter(
            DetectionLog.detected_at >= start_date
        ).group_by(
            func.date(DetectionLog.detected_at)
        ).order_by(
            func.date(DetectionLog.detected_at)
        ).all()
        
        # Format data for chart
        timeline_data = [
            {
                'date': str(date) if date else None,
                'count': count
            }
            for date, count in detections_by_date
        ]
        
        return jsonify({
            'timeline': timeline_data,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch timeline: {str(e)}'}), 500


@bp.route('/detection-status-breakdown', methods=['GET'])
@jwt_required()
def get_detection_status_breakdown():
    """Get breakdown of detections by status."""
    try:
        status_counts = db.session.query(
            DetectionLog.status,
            func.count(DetectionLog.id).label('count')
        ).group_by(
            DetectionLog.status
        ).all()
        
        breakdown = [
            {
                'status': status,
                'count': count
            }
            for status, count in status_counts
        ]
        
        return jsonify({
            'breakdown': breakdown
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch status breakdown: {str(e)}'}), 500


@bp.route('/confidence-distribution', methods=['GET'])
@jwt_required()
def get_confidence_distribution():
    """Get distribution of detection confidence scores."""
    try:
        # Define confidence ranges
        ranges = [
            {'min': 0.0, 'max': 0.5, 'label': '0-50%'},
            {'min': 0.5, 'max': 0.7, 'label': '50-70%'},
            {'min': 0.7, 'max': 0.85, 'label': '70-85%'},
            {'min': 0.85, 'max': 1.0, 'label': '85-100%'}
        ]
        
        distribution = []
        for range_def in ranges:
            count = DetectionLog.query.filter(
                and_(
                    DetectionLog.confidence_score >= range_def['min'],
                    DetectionLog.confidence_score < range_def['max']
                )
            ).count()
            distribution.append({
                'range': range_def['label'],
                'count': count
            })
        
        return jsonify({
            'distribution': distribution
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch confidence distribution: {str(e)}'}), 500


@bp.route('/location-stats', methods=['GET'])
@jwt_required()
def get_location_stats():
    """Get detection counts by location."""
    try:
        limit = int(request.args.get('limit', 10))
        
        location_counts = db.session.query(
            DetectionLog.location,
            func.count(DetectionLog.id).label('count')
        ).filter(
            DetectionLog.location.isnot(None)
        ).group_by(
            DetectionLog.location
        ).order_by(
            func.count(DetectionLog.id).desc()
        ).limit(limit).all()
        
        locations = [
            {
                'location': location,
                'count': count
            }
            for location, count in location_counts
        ]
        
        return jsonify({
            'locations': locations
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch location stats: {str(e)}'}), 500


@bp.route('/video-analytics', methods=['GET'])
@jwt_required()
def get_video_analytics():
    """Get video processing analytics."""
    try:
        # Total processing time
        completed_videos = VideoDetection.query.filter_by(
            processing_status='completed'
        ).filter(
            VideoDetection.processing_started_at.isnot(None),
            VideoDetection.processing_completed_at.isnot(None)
        ).all()
        
        total_processing_time = 0
        avg_processing_time = 0
        
        if completed_videos:
            processing_times = []
            for video in completed_videos:
                delta = video.processing_completed_at - video.processing_started_at
                processing_times.append(delta.total_seconds())
            
            total_processing_time = sum(processing_times)
            avg_processing_time = total_processing_time / len(processing_times)
        
        # Videos by status
        status_counts = db.session.query(
            VideoDetection.processing_status,
            func.count(VideoDetection.id).label('count')
        ).group_by(
            VideoDetection.processing_status
        ).all()
        
        status_breakdown = [
            {
                'status': status,
                'count': count
            }
            for status, count in status_counts
        ]
        
        # Total faces and criminals detected in videos
        total_faces = db.session.query(
            func.sum(VideoDetection.total_faces_detected)
        ).scalar() or 0
        
        total_criminals = db.session.query(
            func.sum(VideoDetection.unique_criminals_matched)
        ).scalar() or 0
        
        return jsonify({
            'avg_processing_time_seconds': round(avg_processing_time, 2),
            'total_processing_time_seconds': round(total_processing_time, 2),
            'status_breakdown': status_breakdown,
            'total_faces_detected': total_faces,
            'total_criminals_matched': total_criminals
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch video analytics: {str(e)}'}), 500


@bp.route('/alert-stats', methods=['GET'])
@jwt_required()
def get_alert_stats():
    """Get alert statistics."""
    try:
        # Alerts by status
        status_counts = db.session.query(
            Alert.status,
            func.count(Alert.id).label('count')
        ).group_by(
            Alert.status
        ).all()
        
        status_breakdown = [
            {
                'status': status,
                'count': count
            }
            for status, count in status_counts
        ]
        
        # Recent alerts trend (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        alerts_by_date = db.session.query(
            func.date(Alert.sent_at).label('date'),
            func.count(Alert.id).label('count')
        ).filter(
            Alert.sent_at >= seven_days_ago
        ).group_by(
            func.date(Alert.sent_at)
        ).order_by(
            func.date(Alert.sent_at)
        ).all()
        
        timeline = [
            {
                'date': str(date) if date else None,
                'count': count
            }
            for date, count in alerts_by_date
        ]
        
        return jsonify({
            'status_breakdown': status_breakdown,
            'timeline': timeline
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch alert stats: {str(e)}'}), 500


@bp.route('/analytics/report', methods=['GET'])
@jwt_required()
def get_analytics_report():
    """Get comprehensive analytics report."""
    try:
        days = int(request.args.get('days', 30))
        report = AnalyticsService.generate_summary_report(days)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'message': f'Failed to generate report: {str(e)}'}), 500


@bp.route('/analytics/performance', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Get performance metrics."""
    try:
        metrics = AnalyticsService.get_performance_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'message': f'Failed to fetch performance metrics: {str(e)}'}), 500


@bp.route('/analytics/activity', methods=['GET'])
@jwt_required()
def get_activity_report():
    """Get criminal activity report."""
    try:
        report = AnalyticsService.get_criminal_activity_report()
        return jsonify({'criminals': report}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to generate activity report: {str(e)}'}), 500


@bp.route('/analytics/locations', methods=['GET'])
@jwt_required()
def get_location_analytics():
    """Get location heatmap data."""
    try:
        data = AnalyticsService.get_location_heatmap_data()
        return jsonify({'locations': data}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to fetch location data: {str(e)}'}), 500


@bp.route('/analytics/patterns', methods=['GET'])
@jwt_required()
def get_time_patterns():
    """Get time-based detection patterns."""
    try:
        patterns = AnalyticsService.get_time_based_patterns()
        return jsonify(patterns), 200
    except Exception as e:
        return jsonify({'message': f'Failed to fetch patterns: {str(e)}'}), 500


@bp.route('/analytics/video-stats', methods=['GET'])
@jwt_required()
def get_detailed_video_stats():
    """Get detailed video processing statistics."""
    try:
        stats = AnalyticsService.get_video_processing_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'message': f'Failed to fetch video stats: {str(e)}'}), 500

