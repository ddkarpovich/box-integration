from flask import render_template, redirect, request, flash, url_for
from flask_login import current_user, login_required

from boxsdk import Client
from boxsdk import OAuth2

from box.integration import config
from box.integration.models import BoxIntegration, BoxWebHook

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
    user_roles = [u.role for u in client.users(fields=['role'])]

    if any([r for r in user_roles if r == REQUIRED_USER_ROLE]):
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

        user_oauth = OAuth2(
            client_id=config.BOX_CLIENT_ID,
            client_secret=config.BOX_CLIENT_SECRET,
            access_token=access_token,
            refresh_token=refresh_token
        )
        user_client = Client(user_oauth)

        # Since Box WebHooks can not be applied to listen root event, we should attach a separate webhooks
        # https://community.box.com/t5/Platform-and-Development-Forum/Listen-to-root-events-with-webhook-v2/td-p/63328#
        for folder in user_client.root_folder().get_items():
            query = BoxWebHook.query.filter_by(
                integration=integration,
                resource_id=folder.id,
                events=','.join(WEBHOOK_EVENTS)
            ).exists()
            if not db.session.query(query).scalar():
                webhook = user_client.create_webhook(folder, WEBHOOK_EVENTS, config.BOX_WEBHOOK_URL)
                hook_instance = BoxWebHook(
                    integration=integration,
                    resource_id=folder.id,
                    webhook_id=webhook.id,
                    events=','.join(WEBHOOK_EVENTS)
                )
                db.session.add(hook_instance)
                db.session.commit()

        flash('Box integration successfully added!')
    else:
        flash(f'Can not process Box integration - {REQUIRED_USER_ROLE} user role is required.')

    return redirect(url_for('home'))


@app.route('/event', methods=['POST'])
@csrf.exempt
@login_required
def box_app_event():
    """Box API WebHook notification listener."""
    return '', 204
