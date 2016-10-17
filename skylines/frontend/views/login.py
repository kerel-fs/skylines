import base64

from datetime import datetime

from flask import render_template, redirect, request, url_for, g, jsonify
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.babel import _

from skylines.model import User
from skylines.frontend.forms import LoginForm
from skylines.schemas import CurrentUserSchema, ValidationError


def register(app):
    """ Register the /login and /logout routes on the given app """

    @app.login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    @app.login_manager.header_loader
    def load_user_from_header(header_val):
        try:
            header_val = header_val.replace('Basic ', '', 1)
            header_val = base64.b64decode(header_val)
            email, password = header_val.split(':', 1)
            return User.by_credentials(email, password)
        except:
            return None

    @app.before_request
    def inject_current_user():
        """
        Inject a current_user variable into the global object. current_user is
        either None or points to the User that is currently logged in.
        """

        if current_user.is_anonymous():
            g.current_user = None
        else:
            g.current_user = current_user

    @app.before_request
    def inject_login_form():
        if g.current_user:
            g.login_form = None
        else:
            g.login_form = LoginForm()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if g.current_user:
            return redirect(get_next())

        form = g.login_form

        if form.validate_on_submit():
            # Find a user matching the credentials
            user = User.by_credentials(form.email_address.data,
                                       form.password.data)

            # Check if the user wants a cookie
            remember = form.remember_me.data

            # Check if a user was found and try to login
            if user and login_user(user, remember=remember):
                user.login_ip = request.remote_addr
                user.login_time = datetime.utcnow()

                return redirect(get_next())
            else:
                form.email_address.errors.append(_('Login failed. Please check your email address.'))
                form.password.errors.append(_('Login failed. Please check your password.'))

        return render_template('login.jinja', form=form, next=get_next())

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(get_next())

    @app.route('/session', methods=('PUT',))
    def create_session():
        if g.current_user:
            return jsonify(error='already-authenticated'), 422

        json = request.get_json()
        if json is None:
            return jsonify(error='invalid-request'), 400

        try:
            data = CurrentUserSchema(only=('email', 'password')).load(json).data
        except ValidationError, e:
            return jsonify(error='validation-failed', fields=e.messages), 422

        user = User.by_credentials(data['email_address'], data['password'])
        if not user or not login_user(user, remember=True):
            return jsonify(error='wrong-credentials'), 403

        return jsonify()

    def get_next():
        return request.values.get("next") or request.referrer or url_for("index")
