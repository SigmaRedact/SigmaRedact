import os
import secrets
from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Change this in production

# Reddit OAuth2 configuration
CLIENT_ID = "Uf9g4ChR3x7-XdFdfu6G8A"
CLIENT_SECRET = "477YqdL-Ox--pwD5JkplWK-44O0LIw"
REDIRECT_URI = "http://localhost:8000/callback"
USER_AGENT = "SigmaRedactBot/v1 by OrganicGas1298"
SCOPES = ["identity", "edit", "history", "read"]

# In-memory user session cache (can be replaced by DB)
user_data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    state = secrets.token_hex(8)
    session["oauth_state"] = state
    auth_url = (
        f"https://www.reddit.com/api/v1/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&state={state}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&duration=temporary"
        f"&scope={' '.join(SCOPES)}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    if request.args.get("state") != session.get("oauth_state"):
        return "Invalid state parameter", 400

    code = request.args.get("code")
    if not code:
        return "Authorization code not found", 400

    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    headers = {"User-Agent": USER_AGENT}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    res = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers
    )

    if res.status_code != 200:
        return f"Failed to get token: {res.text}", 400

    token_json = res.json()
    access_token = token_json["access_token"]
    session["access_token"] = access_token

    # Get the Reddit username
    user_res = requests.get(
        "https://oauth.reddit.com/api/v1/me",
        headers={
            "Authorization": f"bearer {access_token}",
            "User-Agent": USER_AGENT
        }
    )

    if user_res.status_code != 200:
        return f"Failed to fetch user info: {user_res.text}", 400

    user_json = user_res.json()
    session["username"] = user_json["name"]

    return redirect(url_for("home"))

@app.route("/home")
def home():
    if "access_token" not in session:
        return redirect(url_for("index"))
    return render_template("redact.htm", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=8000, debug=True)
