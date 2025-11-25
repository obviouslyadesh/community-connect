from app import create_app, db
from app.models import User, Event, EventVolunteer

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create sample data
        org = User(username='sample_org', email='org@example.com', user_type='organization', is_admin=True)
        org.set_password('password123')
        
        volunteer = User(username='sample_volunteer', email='volunteer@example.com', user_type='volunteer')
        volunteer.set_password('password123')
        
        db.session.add(org)
        db.session.add(volunteer)
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)