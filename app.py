import os
import secrets
from flask import Flask, redirect, request, session, url_for, render_template, jsonify
import requests

app = Flask(__name__)
app.secret_key = "477YqdL-Ox--pwD5JkplWK-44O0LIw"  # You should set this as an environment variable in production

# Reddit OAuth config
CLIENT_ID = "Uf9g4ChR3x7-XdFdfu6G8A"
CLIENT_SECRET = "477YqdL-Ox--pwD5JkplWK-44O0LIw"
REDIRECT_URI = "https://sigmaredact.onrender.com/callback"
USER_AGENT = "SigmaRedactBot/v1 by OrganicGas1298"
SCOPES = ["identity", "edit", "history", "read"]

BRAINROT_WORDS = [
    "skibidi", "rizz", "bussin", "cringe", "sigma", "alpha", "beta", "chud", "gigachad",
    "npc", "gyatt", "mewing", "mogging", "fanum", "sus", "ohio", "delulu", "mid", "blud", "yap"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    state = secrets.token_hex(8)
    session['oauth_state'] = state
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "duration": "temporary",
        "scope": " ".join(SCOPES)
    }
    auth_url = f"https://www.reddit.com/api/v1/authorize?" + "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if request.args.get('state') != session.get('oauth_state'):
        return "State mismatch. Authentication failed.", 400

    code = request.args.get('code')
    if not code:
        return "No code provided", 400

    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"User-Agent": USER_AGENT}
    res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    token_json = res.json()
    session['access_token'] = token_json.get("access_token")

    # Get user identity
    headers["Authorization"] = f"bearer {session['access_token']}"
    user_res = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    session['reddit_user'] = user_res.json()
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template('redact.html', user=session['reddit_user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/brainrotify_progress')
def brainrotify_progress():
    # Dummy API for progress bar
    return jsonify({"progress": 100})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
