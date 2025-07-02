from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.routes.mentorship import mentorship_bp
from app.models import User, MentorshipRequest, MentorshipSession, MentorAvailability
from app.forms import MentorshipRequestForm, SessionFeedbackForm, AvailabilityForm
from datetime import datetime, time
from app.utils import role_required

@mentorship_bp.route('/mentors')
@login_required
@role_required('mentee')
def mentor_list():
    mentors = User.query.filter_by(role='mentor').all()
    skills = Skill.query.all()
    return render_template('mentee/mentors.html', mentors=mentors, skills=skills)

@mentorship_bp.route('/requests/send/<int:mentor_id>', methods=['GET', 'POST'])
@login_required
@role_required('mentee')
def send_request(mentor_id):
    mentor = User.query.get_or_404(mentor_id)
    form = MentorshipRequestForm()
    
    if form.validate_on_submit():
        request = MentorshipRequest(
            mentee_id=current_user.id,
            mentor_id=mentor_id,
            message=form.message.data
        )
        db.session.add(request)
        db.session.commit()
        flash('Your mentorship request has been sent!', 'success')
        return redirect(url_for('mentorship.my_requests'))
    
    return render_template('mentee/send_request.html', form=form, mentor=mentor)

@mentorship_bp.route('/requests/my')
@login_required
@role_required('mentee')
def my_requests():
    requests = MentorshipRequest.query.filter_by(mentee_id=current_user.id).all()
    return render_template('mentee/my_requests.html', requests=requests)

@mentorship_bp.route('/requests/received')
@login_required
@role_required('mentor')
def received_requests():
    requests = MentorshipRequest.query.filter_by(mentor_id=current_user.id, status='pending').all()
    return render_template('mentor/requests.html', requests=requests)

@mentorship_bp.route('/requests/<int:request_id>/respond', methods=['POST'])
@login_required
@role_required('mentor')
def respond_request(request_id):
    request = MentorshipRequest.query.get_or_404(request_id)
    if request.mentor_id != current_user.id:
        abort(403)
    
    action = request.form.get('action')
    if action == 'accept':
        request.status = 'accepted'
        db.session.commit()
        flash('Request accepted', 'success')
    elif action == 'reject':
        request.status = 'rejected'
        db.session.commit()
        flash('Request rejected', 'info')
    
    return redirect(url_for('mentorship.received_requests'))

@mentorship_bp.route('/availability', methods=['GET', 'POST'])
@login_required
@role_required('mentor')
def availability():
    form = AvailabilityForm()
    
    if form.validate_on_submit():
        availability = MentorAvailability(
            mentor_id=current_user.id,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        db.session.add(availability)
        db.session.commit()
        flash('Availability added!', 'success')
        return redirect(url_for('mentorship.availability'))
    
    availabilities = MentorAvailability.query.filter_by(mentor_id=current_user.id).all()
    return render_template('mentor/availability.html', form=form, availabilities=availabilities)

@mentorship_bp.route('/availability/<int:availability_id>/delete', methods=['POST'])
@login_required
@role_required('mentor')
def delete_availability(availability_id):
    availability = MentorAvailability.query.get_or_404(availability_id)
    if availability.mentor_id != current_user.id:
        abort(403)
    
    db.session.delete(availability)
    db.session.commit()
    flash('Availability removed', 'info')
    return redirect(url_for('mentorship.availability'))

@mentorship_bp.route('/sessions/book/<int:request_id>', methods=['GET', 'POST'])
@login_required
@role_required('mentee')
def book_session(request_id):
    request = MentorshipRequest.query.get_or_404(request_id)
    if request.mentee_id != current_user.id or request.status != 'accepted':
        abort(403)
    
    mentor = User.query.get(request.mentor_id)
    availabilities = MentorAvailability.query.filter_by(mentor_id=mentor.id).all()
    
    if request.method == 'POST':
        scheduled_time_str = request.form.get('scheduled_time')
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M')
        duration = int(request.form.get('duration', 30))
        
        session = MentorshipSession(
            mentor_id=mentor.id,
            mentee_id=current_user.id,
            request_id=request.id,
            scheduled_time=scheduled_time,
            duration=duration
        )
        db.session.add(session)
        db.session.commit()
        flash('Session booked successfully!', 'success')
        return redirect(url_for('mentorship.my_sessions'))
    
    return render_template('mentee/book_session.html', request=request, mentor=mentor, availabilities=availabilities)

@mentorship_bp.route('/sessions/my')
@login_required
def my_sessions():
    if current_user.is_mentor():
        sessions = MentorshipSession.query.filter_by(mentor_id=current_user.id).order_by(MentorshipSession.scheduled_time).all()
        return render_template('mentor/sessions.html', sessions=sessions)
    else:
        sessions = MentorshipSession.query.filter_by(mentee_id=current_user.id).order_by(MentorshipSession.scheduled_time).all()
        return render_template('mentee/my_sessions.html', sessions=sessions)

@mentorship_bp.route('/sessions/<int:session_id>/feedback', methods=['GET', 'POST'])
@login_required
def session_feedback(session_id):
    session = MentorshipSession.query.get_or_404(session_id)
    
    if current_user.id not in [session.mentor_id, session.mentee_id]:
        abort(403)
    
    form = SessionFeedbackForm()
    
    if form.validate_on_submit():
        if current_user.id == session.mentee_id:
            session.mentee_feedback = form.feedback.data
            session.mentee_rating = form.rating.data
        elif current_user.id == session.mentor_id:
            session.mentor_feedback = form.feedback.data
        
        db.session.commit()
        flash('Feedback submitted!', 'success')
        return redirect(url_for('mentorship.my_sessions'))
    
    return render_template('session_feedback.html', form=form, session=session)