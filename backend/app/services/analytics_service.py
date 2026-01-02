"""Analytics service for generating reports and insights."""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app import db
from app.models.criminal import Criminal
from app.models.detection_log import DetectionLog
from app.models.alert import Alert
from app.models.video_detection import VideoDetection, VideoFrameDetection


class AnalyticsService:
    """Service for generating analytics and reports."""
    
    @staticmethod
    def get_detection_trends(days=30):
        """Get detection trends over specified number of days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily detections
        daily_detections = db.session.query(
            func.date(DetectionLog.detected_at).label('date'),
            func.count(DetectionLog.id).label('total'),
            func.count(func.nullif(DetectionLog.status == 'verified', False)).label('verified'),
            func.count(func.nullif(DetectionLog.status == 'pending', False)).label('pending')
        ).filter(
            DetectionLog.detected_at >= start_date
        ).group_by(
            func.date(DetectionLog.detected_at)
        ).order_by(
            func.date(DetectionLog.detected_at)
        ).all()
        
        return [
            {
                'date': str(date) if date else None,
                'total': total,
                'verified': verified,
                'pending': pending
            }
            for date, total, verified, pending in daily_detections
        ]
    
    @staticmethod
    def get_criminal_activity_report():
        """Get comprehensive criminal activity report."""
        # Most active criminals
        top_criminals = db.session.query(
            Criminal,
            func.count(DetectionLog.id).label('detection_count'),
            func.max(DetectionLog.detected_at).label('last_detected'),
            func.avg(DetectionLog.confidence_score).label('avg_confidence')
        ).join(
            DetectionLog, Criminal.id == DetectionLog.criminal_id
        ).group_by(
            Criminal.id
        ).order_by(
            func.count(DetectionLog.id).desc()
        ).limit(20).all()
        
        result = []
        for criminal, count, last_detected, avg_conf in top_criminals:
            criminal_dict = criminal.to_dict()
            criminal_dict.update({
                'detection_count': count,
                'last_detected': last_detected.isoformat() if last_detected else None,
                'avg_confidence': round(float(avg_conf), 3) if avg_conf else 0
            })
            result.append(criminal_dict)
        
        return result
    
    @staticmethod
    def get_location_heatmap_data():
        """Get data for location heatmap visualization."""
        location_data = db.session.query(
            DetectionLog.location,
            func.count(DetectionLog.id).label('total_detections'),
            func.count(func.distinct(DetectionLog.criminal_id)).label('unique_criminals'),
            func.avg(DetectionLog.confidence_score).label('avg_confidence')
        ).filter(
            DetectionLog.location.isnot(None)
        ).group_by(
            DetectionLog.location
        ).order_by(
            func.count(DetectionLog.id).desc()
        ).all()
        
        return [
            {
                'location': location,
                'total_detections': total,
                'unique_criminals': unique,
                'avg_confidence': round(float(avg_conf), 3) if avg_conf else 0
            }
            for location, total, unique, avg_conf in location_data
        ]
    
    @staticmethod
    def get_performance_metrics():
        """Get system performance metrics."""
        # Detection accuracy
        total_reviewed = DetectionLog.query.filter(
            or_(DetectionLog.status == 'verified', DetectionLog.status == 'false_positive')
        ).count()
        
        verified = DetectionLog.query.filter_by(status='verified').count()
        false_positives = DetectionLog.query.filter_by(status='false_positive').count()
        
        accuracy = (verified / total_reviewed * 100) if total_reviewed > 0 else 0
        false_positive_rate = (false_positives / total_reviewed * 100) if total_reviewed > 0 else 0
        
        # Average confidence scores
        avg_confidence_all = db.session.query(
            func.avg(DetectionLog.confidence_score)
        ).scalar() or 0
        
        avg_confidence_verified = db.session.query(
            func.avg(DetectionLog.confidence_score)
        ).filter_by(status='verified').scalar() or 0
        
        avg_confidence_false = db.session.query(
            func.avg(DetectionLog.confidence_score)
        ).filter_by(status='false_positive').scalar() or 0
        
        # Response time (alerts sent)
        alerts_with_delay = db.session.query(
            Alert.sent_at,
            DetectionLog.detected_at
        ).join(
            DetectionLog, Alert.detection_log_id == DetectionLog.id
        ).filter(
            Alert.status == 'sent'
        ).all()
        
        avg_response_time = 0
        if alerts_with_delay:
            response_times = [
                (alert_time - detection_time).total_seconds()
                for alert_time, detection_time in alerts_with_delay
                if alert_time and detection_time
            ]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'accuracy_rate': round(accuracy, 2),
            'false_positive_rate': round(false_positive_rate, 2),
            'total_reviewed': total_reviewed,
            'verified_detections': verified,
            'false_positives': false_positives,
            'avg_confidence_all': round(float(avg_confidence_all), 3),
            'avg_confidence_verified': round(float(avg_confidence_verified), 3),
            'avg_confidence_false_positive': round(float(avg_confidence_false), 3),
            'avg_response_time_seconds': round(avg_response_time, 2)
        }
    
    @staticmethod
    def get_video_processing_stats():
        """Get detailed video processing statistics."""
        completed_videos = VideoDetection.query.filter_by(
            processing_status='completed'
        ).all()
        
        if not completed_videos:
            return {
                'total_videos_processed': 0,
                'total_frames_processed': 0,
                'total_faces_detected': 0,
                'total_criminals_matched': 0,
                'avg_processing_time': 0,
                'avg_frames_per_video': 0,
                'avg_faces_per_video': 0
            }
        
        total_frames = sum(v.frames_processed or 0 for v in completed_videos)
        total_faces = sum(v.total_faces_detected or 0 for v in completed_videos)
        total_criminals = sum(v.unique_criminals_matched or 0 for v in completed_videos)
        
        processing_times = []
        for video in completed_videos:
            if video.processing_started_at and video.processing_completed_at:
                delta = video.processing_completed_at - video.processing_started_at
                processing_times.append(delta.total_seconds())
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            'total_videos_processed': len(completed_videos),
            'total_frames_processed': total_frames,
            'total_faces_detected': total_faces,
            'total_criminals_matched': total_criminals,
            'avg_processing_time': round(avg_processing_time, 2),
            'avg_frames_per_video': round(total_frames / len(completed_videos), 2),
            'avg_faces_per_video': round(total_faces / len(completed_videos), 2)
        }
    
    @staticmethod
    def get_time_based_patterns():
        """Analyze detection patterns by time of day and day of week."""
        # Get all detections
        detections = DetectionLog.query.all()
        
        # Initialize patterns
        hourly_counts = {hour: 0 for hour in range(24)}
        daily_counts = {day: 0 for day in range(7)}  # 0 = Monday
        
        for detection in detections:
            if detection.detected_at:
                hour = detection.detected_at.hour
                day = detection.detected_at.weekday()
                hourly_counts[hour] += 1
                daily_counts[day] += 1
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'hourly_pattern': [
                {'hour': hour, 'count': count}
                for hour, count in sorted(hourly_counts.items())
            ],
            'daily_pattern': [
                {'day': day_names[day], 'count': count}
                for day, count in sorted(daily_counts.items())
            ]
        }
    
    @staticmethod
    def generate_summary_report(days=30):
        """Generate a comprehensive summary report."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Period statistics
        period_detections = DetectionLog.query.filter(
            DetectionLog.detected_at >= start_date
        ).count()
        
        period_criminals = db.session.query(
            func.count(func.distinct(DetectionLog.criminal_id))
        ).filter(
            DetectionLog.detected_at >= start_date
        ).scalar() or 0
        
        period_alerts = Alert.query.filter(
            Alert.sent_at >= start_date
        ).count()
        
        # Get trends
        trends = AnalyticsService.get_detection_trends(days)
        
        # Get performance metrics
        performance = AnalyticsService.get_performance_metrics()
        
        # Get top locations
        top_locations = db.session.query(
            DetectionLog.location,
            func.count(DetectionLog.id).label('count')
        ).filter(
            DetectionLog.detected_at >= start_date,
            DetectionLog.location.isnot(None)
        ).group_by(
            DetectionLog.location
        ).order_by(
            func.count(DetectionLog.id).desc()
        ).limit(5).all()
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_detections': period_detections,
                'unique_criminals': period_criminals,
                'alerts_sent': period_alerts
            },
            'performance': performance,
            'trends': trends,
            'top_locations': [
                {'location': loc, 'count': count}
                for loc, count in top_locations
            ]
        }
