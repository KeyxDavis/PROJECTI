from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.routes.main import main_bp

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_mentor():
        return redirect(url_for('mentor.dashboard'))
    elif current_user.is_mentee():
        return redirect(url_for('mentee.dashboard'))
    return redirect(url_for('main.index'))