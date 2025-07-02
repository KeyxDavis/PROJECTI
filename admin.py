from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.routes.admin import admin_bp
from app.models import User, MentorshipRequest, MentorshipSession
from app.forms import AdminUserForm
from app.utils import role_required

@admin_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def dashboard():
    users_count = User.query.count()
    mentors_count = User.query.filter_by(role='mentor').count()
    mentees_count = User.query.filter_by(role='mentee').count()
    sessions_count = MentorshipSession.query.count()
    
    return render_template('admin/dashboard.html', 
                         users_count=users_count,
                         mentors_count=mentors_count,
                         mentees_count=mentees_count,
                         sessions_count=sessions_count)

@admin_bp.route('/admin/users')
@login_required
@role_required('admin')
def users():
    users = User.query.order_by(User.role, User.name).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_user():
    form = AdminUserForm()
    
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            name=form.name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.name} created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/matches')
@login_required
@role_required('admin')
def matches():
    matches = MentorshipRequest.query.filter_by(status='accepted').order_by(MentorshipRequest.updated_at.desc()).all()
    return render_template('admin/matches.html', matches=matches)

@admin_bp.route('/admin/sessions')
@login_required
@role_required('admin')
def sessions():
    sessions = MentorshipSession.query.order_by(MentorshipSession.scheduled_time.desc()).all()
    return render_template('admin/sessions.html', sessions=sessions)

@admin_bp.route('/admin/assign-mentor', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def assign_mentor():
    if request.method == 'POST':
        mentee_id = request.form.get('mentee_id')
        mentor_id = request.form.get('mentor_id')
        
        mentee = User.query.get(mentee_id)
        mentor = User.query.get(mentor_id)
        
        if not mentee or not mentor or mentor.role != 'mentor':
            flash('Invalid selection', 'danger')
            return redirect(url_for('admin.assign_mentor'))
        
        # Check if request already exists
        existing_request = MentorshipRequest.query.filter_by(
            mentee_id=mentee_id,
            mentor_id=mentor_id
        ).first()
        
        if existing_request:
            existing_request.status = 'accepted'
            db.session.commit()
            flash('Mentorship match already existed and has been accepted', 'info')
        else:
            request = MentorshipRequest(
                mentee_id=mentee_id,
                mentor_id=mentor_id,
                status='accepted'
            )
            db.session.add(request)
            db.session.commit()
            flash('Mentor assigned successfully!', 'success')
        
        return redirect(url_for('admin.matches'))
    
    mentees = User.query.filter_by(role='mentee').all()
    mentors = User.query.filter_by(role='mentor').all()
    return render_template('admin/assign_mentor.html', mentees=mentees, mentors=mentors)