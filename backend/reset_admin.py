"""Create or reset admin user for testing"""
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(email='sibirajkumar30@gmail.com').first()
    
    if admin:
        # Update password using model's method
        admin.set_password('Sibi@123')
        db.session.commit()
        print("✓ Admin user password reset successfully")
        print(f"  Email: {admin.email}")
        print(f"  Username: {admin.username}")
        print(f"  Role: {admin.role}")
    else:
        # Create new admin user
        admin = User(
            username='sibirajkumar',
            email='sibirajkumar30@gmail.com',
            role='admin',
            is_active=True
        )
        admin.set_password('Sibi@123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created successfully")
        print(f"  Email: {admin.email}")
        print(f"  Username: {admin.username}")
        print(f"  Role: {admin.role}")
    
    print("\nYou can now login with:")
    print("  Email: sibirajkumar30@gmail.com")
    print("  Password: Sibi@123")
