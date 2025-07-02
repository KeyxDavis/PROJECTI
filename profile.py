from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.routes.profile import profile_bp
from app.models import User, Skill, UserSkill
from app.forms import ProfileForm

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    
    # Populate skills choices
    all_skills = Skill.query.all()
    form.skills.choices = [(skill.id, skill.name) for skill in all_skills]
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.bio = form.bio.data
        current_user.goals = form.goals.data
        
        # Update skills
        selected_skill_ids = form.skills.data
        current_skills = {us.skill_id for us in current_user.skills}
        
        # Remove unselected skills
        for skill_id in current_skills - set(selected_skill_ids):
            UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill_id).delete()
        
        # Add new skills
        for skill_id in set(selected_skill_ids) - current_skills:
            new_user_skill = UserSkill(user_id=current_user.id, skill_id=skill_id)
            db.session.add(new_user_skill)
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.bio.data = current_user.bio
        form.goals.data = current_user.goals
        form.skills.data = [us.skill_id for us in current_user.skills]
    
    return render_template('profile/edit.html', form=form)