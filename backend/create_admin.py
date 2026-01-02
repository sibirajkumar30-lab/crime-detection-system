"""
Create an admin user for the system
"""
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        # Update password for existing admin
        print(f"Admin user found: {admin.username} ({admin.email})")
        print(f"Updating password...")
        admin.set_password('admin123')
        db.session.commit()
        print("✅ Admin password updated successfully!")
        print(f"Role: {admin.role}, Active: {admin.is_active}")
    else:
        # Create new admin user with proper password hashing
        admin = User(
            username='admin',
            email='admin@crimedetection.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')  # Use the model's set_password method
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
    
    print()
    print("You can now login with:")
    print("  Email: admin@crimedetection.com")
    print("  Password: admin123")
