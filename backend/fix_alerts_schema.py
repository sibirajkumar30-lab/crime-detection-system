"""Quick fix: Make detection_log_id nullable in alerts table"""
import sqlite3
import shutil
import os

# Backup database first
db_path = 'instance/crime_detection.db'
backup_path = 'instance/crime_detection.db.backup'

print("Creating database backup...")
shutil.copy2(db_path, backup_path)
print(f"✓ Backup created: {backup_path}")

# Connect and fix schema
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\nFixing alerts table schema...")

try:
    cursor.execute('PRAGMA foreign_keys=off')
    
    # First, fix NULL values in existing data BEFORE creating new table
    print("Updating NULL values in existing records...")
    cursor.execute("UPDATE alerts SET delivery_method = 'email' WHERE delivery_method IS NULL OR delivery_method = ''")
    cursor.execute("UPDATE alerts SET severity = 'info' WHERE severity IS NULL OR severity = ''")
    cursor.execute("UPDATE alerts SET category = 'operational' WHERE category IS NULL OR category = ''")
    cursor.execute("UPDATE alerts SET alert_type = 'general' WHERE alert_type IS NULL OR alert_type = ''")
    cursor.execute("UPDATE alerts SET priority = 3 WHERE priority IS NULL")
    cursor.execute("UPDATE alerts SET acknowledged = 0 WHERE acknowledged IS NULL")
    cursor.execute("UPDATE alerts SET retry_count = 0 WHERE retry_count IS NULL")
    cursor.execute("UPDATE alerts SET status = 'sent' WHERE status IS NULL OR status = ''")
    cursor.execute("UPDATE alerts SET created_at = sent_at WHERE created_at IS NULL")
    conn.commit()
    print("✓ NULL values updated")
    
    cursor.execute('BEGIN TRANSACTION')
    
    # Create new table with correct schema (detection_log_id is nullable)
    cursor.execute('''
        CREATE TABLE alerts_new (
            id INTEGER PRIMARY KEY,
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) DEFAULT 'info' NOT NULL,
            category VARCHAR(50) NOT NULL,
            priority INTEGER DEFAULT 3 NOT NULL,
            detection_log_id INTEGER,  -- NOW NULLABLE
            video_detection_id INTEGER,
            criminal_id INTEGER,
            user_id INTEGER,
            title VARCHAR(200),
            subject VARCHAR(200),
            message TEXT NOT NULL,
            delivery_method VARCHAR(20) DEFAULT 'email' NOT NULL,
            recipient_email VARCHAR(100),
            recipient_phone VARCHAR(20),
            status VARCHAR(20) DEFAULT 'sent' NOT NULL,
            acknowledged BOOLEAN DEFAULT 0 NOT NULL,
            acknowledged_by INTEGER,
            acknowledged_at DATETIME,
            sent_at DATETIME NOT NULL,
            expires_at DATETIME,
            retry_count INTEGER DEFAULT 0 NOT NULL,
            created_at DATETIME NOT NULL,
            data JSON,
            FOREIGN KEY(detection_log_id) REFERENCES detection_logs(id),
            FOREIGN KEY(video_detection_id) REFERENCES video_detections(id),
            FOREIGN KEY(criminal_id) REFERENCES criminals(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(acknowledged_by) REFERENCES users(id)
        )
    ''')
    
    # Copy data from old table to new table (specify column order)
    cursor.execute('''
        INSERT INTO alerts_new (
            id, detection_log_id, recipient_email, subject, message, sent_at,
            status, retry_count, severity, category, alert_type, priority,
            recipient_phone, acknowledged, acknowledged_by, acknowledged_at,
            delivery_method, data, expires_at, created_at, user_id, criminal_id,
            video_detection_id, title
        )
        SELECT 
            id, detection_log_id, recipient_email, subject, message, sent_at,
            status, retry_count, severity, category, alert_type, priority,
            recipient_phone, acknowledged, acknowledged_by, acknowledged_at,
            delivery_method, data, expires_at, created_at, user_id, criminal_id,
            video_detection_id, title
        FROM alerts
    ''')
    
    # Drop old table and rename new one
    cursor.execute('DROP TABLE alerts')
    cursor.execute('ALTER TABLE alerts_new RENAME TO alerts')
    
    # Recreate indexes
    cursor.execute('CREATE INDEX ix_alerts_severity ON alerts (severity)')
    cursor.execute('CREATE INDEX ix_alerts_category ON alerts (category)')
    cursor.execute('CREATE INDEX ix_alerts_acknowledged ON alerts (acknowledged)')
    cursor.execute('CREATE INDEX ix_alerts_expires_at ON alerts (expires_at)')
    cursor.execute('CREATE INDEX ix_alerts_created_at ON alerts (created_at)')
    cursor.execute('CREATE INDEX ix_alerts_user_id ON alerts (user_id)')
    cursor.execute('CREATE INDEX ix_alerts_criminal_id ON alerts (criminal_id)')
    
    cursor.execute('COMMIT')
    cursor.execute('PRAGMA foreign_keys=on')
    
    conn.commit()
    print("✓ Schema fixed successfully!")
    print("✓ detection_log_id is now NULLABLE")
    print("\nYou can now add criminals without detection logs.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Restoring from backup...")
    conn.close()
    shutil.copy2(backup_path, db_path)
    print("✓ Database restored from backup")
    raise

finally:
    conn.close()
