"""Update existing pending detections to verified status based on confidence."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.detection_log import DetectionLog

def update_detection_statuses():
    """Update detection statuses based on confidence score."""
    app = create_app()
    
    with app.app_context():
        # Get all pending detections
        pending_detections = DetectionLog.query.filter_by(status='pending').all()
        
        print(f"Found {len(pending_detections)} pending detections")
        
        updated_count = 0
        for detection in pending_detections:
            # Auto-verify detections with confidence >= 80%
            if detection.confidence_score >= 0.80:
                detection.status = 'verified'
                updated_count += 1
        
        # Commit changes
        db.session.commit()
        
        print(f"Updated {updated_count} detections to 'verified' status")
        print(f"{len(pending_detections) - updated_count} detections remain as 'pending' (confidence < 80%)")
        
        # Print summary
        print("\nCurrent status breakdown:")
        verified = DetectionLog.query.filter_by(status='verified').count()
        pending = DetectionLog.query.filter_by(status='pending').count()
        false_pos = DetectionLog.query.filter_by(status='false_positive').count()
        
        print(f"  Verified: {verified}")
        print(f"  Pending: {pending}")
        print(f"  False Positives: {false_pos}")

if __name__ == '__main__':
    update_detection_statuses()
