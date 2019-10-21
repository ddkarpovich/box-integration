# Box API integration
## Local usage

Edit `box/config.py` with a database settings.

Follow the next steps using console:
1. `python3.7 -m venv .venv/egnyte`
2. `source .venv/egnyte/bin/activate`
3. `pip install -r requirements.txt`
4. `export FLASK_APP=box.app`
5. `flask db upgrade`
6. `flask create-user admin admin@admin.com password`
7. `python run.py`
8. Run ngrok under 5000 port - `./ngrok http 5000`
9. Edit `box/integration/config.py`, change `BOX_REDIRECT_URI` settings to match your ngrok URL.

Then:
1. Open your ngrok URL and click on `Login` - enter `admin`/`password` credentials.
2. Click on `Integrate Box`.
3. Use Box login credentials from Slack.
4. Allow access for our app.
5. You should see a success integration message `Box integration successfully added!`.
6. Click on `Poll events` to initiate a long polling request and wait for a new event.
7. Click on `Admin logs` to retrieve all admin logs.
