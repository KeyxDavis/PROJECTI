from app import create_app, db
from app.models import User, Skill

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create initial skills
        skills = [
            'Marketing', 'UI/UX Design', 'Software Development', 
            'Product Management', 'Data Science', 'Business Strategy',
            'Finance', 'Leadership', 'Sales', 'Customer Success'
        ]
        
        for skill_name in skills:
            if not Skill.query.filter_by(name=skill_name).first():
                skill = Skill(name=skill_name)
                db.session.add(skill)
        
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@mentorship.com').first():
            admin = User(
                email='admin@mentorship.com',
                name='Admin User',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()