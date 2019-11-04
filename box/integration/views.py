from flask import render_template, redirect, request, flash, url_for
from flask_login import current_user, login_required

import requests

from boxsdk import Client, OAuth2
from boxsdk.exception import BoxAPIException

from box.integration import config
from box.integration.models import BoxIntegration

from box.app import app, db, csrf


csrf_token = ''
oauth = OAuth2(
    client_id=config.BOX_CLIENT_ID,
    client_secret=config.BOX_CLIENT_SECRET
)
REQUIRED_USER_ROLE = 'admin'
WEBHOOK_EVENTS = ['FILE.UPLOADED']


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/authorize/')
@login_required
def box_app_authorize():
    global csrf_token
    auth_url, csrf_token = oauth.get_authorization_url(config.BOX_REDIRECT_URI)
    return redirect(auth_url)


@app.route('/return')
@login_required
def box_app_callback():
    """Box API OAuth 2 callback."""
    # Capture auth code and csrf token via state
    code = request.args.get('code')
    state = request.args.get('state')

    # If csrf token matches, fetch tokens
    if state != csrf_token:
        flash('CSRF verification failed, please try again.')
        return redirect(url_for('home'))

    access_token, refresh_token = oauth.authenticate(code)

    client = Client(oauth)

    try:
        user_role = client.user().get(['role']).role
    except BoxAPIException as e:
        if e.code == 'access_denied_insufficient_permissions':
            flash(f'Can not process Box integration - {REQUIRED_USER_ROLE} user role is required.')
        else:
            flash(f'Something went wrong while trying to integrate Box APP (code {e.code})')
        return redirect(url_for('home'))

    if user_role != REQUIRED_USER_ROLE:
        integration = current_user.box_integration
        if integration is None:
            integration = BoxIntegration(
                user=current_user,
                access_token=access_token,
                refresh_token=refresh_token
            )
        else:
            integration.access_token = access_token
            integration.refresh_token = refresh_token

        db.session.add(integration)
        db.session.commit()

        flash('Box integration successfully added!')
    else:
        flash(f'Can not process Box integration - {REQUIRED_USER_ROLE} user role is required.')

    return redirect(url_for('home'))


@app.route('/poll', methods=['GET'])
def box_app_poll():
    integration = current_user.box_integration

    if integration is None or not (integration.access_token and integration.refresh_token):
        flash('You have to integrate BOX app first')
        return redirect(url_for('home'))

    user_oauth = OAuth2(
        client_id=config.BOX_CLIENT_ID,
        client_secret=config.BOX_CLIENT_SECRET,
        access_token=integration.access_token,
        refresh_token=integration.refresh_token
    )
    client = Client(user_oauth)
    events = client.events().generate_events_with_long_polling()

    for event in events:
        flash(f'Got {event.event_type} event - {event.response_object}')
        return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/admin_logs', methods=['GET'])
def box_app_admin_logs():
    integration = current_user.box_integration

    if integration is None or not (integration.access_token and integration.refresh_token):
        flash('You have to integrate BOX app first')
        return redirect(url_for('home'))

    user_oauth = OAuth2(
        client_id=config.BOX_CLIENT_ID,
        client_secret=config.BOX_CLIENT_SECRET,
        access_token=integration.access_token,
        refresh_token=integration.refresh_token
    )
    client = Client(user_oauth)
    events = client.events().get_admin_events(event_types=['UPLOAD'])

    flash(integration.access_token)
    flash(integration.refresh_token)

    for event in events['entries']:
        flash(f'Got {event.event_type} event - {event.response_object}')

    return redirect(url_for('home'))


@app.route('/event', methods=['POST'])
@csrf.exempt
def box_app_event():
    """Box API WebHook notification listener."""
    return '', 204
