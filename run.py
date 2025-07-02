from app import create_app, db
from app.models import User, Skill, MentorshipRequest, MentorshipSession, MentorAvailability
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Skill': Skill,
        'MentorshipRequest': MentorshipRequest,
        'MentorshipSession': MentorshipSession,
        'MentorAvailability': MentorAvailability
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)