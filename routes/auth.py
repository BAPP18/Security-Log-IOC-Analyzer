from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from utils.helpers import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter username and password.', 'warning')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            log_activity(
                user.id,
                'Login',
                f'User {user.username} logged in',
                request.remote_addr
            )
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.index'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    log_activity(
        current_user.id,
        'Logout',
        f'User {current_user.username} logged out',
        request.remote_addr
    )
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
