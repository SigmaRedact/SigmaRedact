import os
import secrets
from flask import Flask, redirect, request, session, url_for, render_template, jsonify
import requests

app = Flask(__name__)
app.secret_key = "477YqdL-Ox--pwD5JkplWK-44O0LIw"  # Fixed secret key

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

AUTH_URL = "https://www.reddit.com/api/v1/authorize"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_ME_URL = "https://oauth.reddit.com/api/v1/me"

@app.route("/")
def index():
    return render_template("index.html", logged_in="access_token" in session)

@app.route("/home")
def home():
    if "access_token" not in session:
        return redirect(url_for("index"))

    headers = {
        "Authorization": f"bearer {session['access_token']}",
        "User-Agent": USER_AGENT
    }
    r = requests.get(API_ME_URL, headers=headers)
    if r.status_code != 200:
        return redirect(url_for("logout"))

    username = r.json().get("name", "Redditor")
    return render_template("redact.htm", username=username)

@app.route("/login")
def login():
    state = secrets.token_hex(8)
    session["state"] = state
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "duration": "permanent",
        "scope": " ".join(SCOPES)
    }
    url = requests.Request("GET", AUTH_URL, params=params).prepare().url
    return redirect(url)

@app.route("/callback")
def callback():
    if request.args.get("error"):
        return "Error during authentication."

    if request.args.get("state") != session.get("state"):
        return "State mismatch.", 400

    code = request.args.get("code")
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"User-Agent": USER_AGENT}
    token = requests.post(TOKEN_URL, auth=auth, data=data, headers=headers)
    
    if token.status_code != 200:
        return f"Failed to retrieve token: {token.text}", 400

    token_json = token.json()
    session["access_token"] = token_json["access_token"]
    session["refresh_token"] = token_json.get("refresh_token")

    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/api/brainrotify_progress")
def brainrotify_progress():
    if "access_token" not in session:
        return jsonify({"error": "Not authenticated"}), 403

    if "comments" not in session:
        headers = {
            "Authorization": f"bearer {session['access_token']}",
            "User-Agent": USER_AGENT
        }
        me = requests.get(API_ME_URL, headers=headers)
        username = me.json().get("name", "")
        comments = []
        after = None
        while True:
            url = f"https://oauth.reddit.com/user/{username}/comments"
            params = {"limit": 100}
            if after:
                params["after"] = after
            resp = requests.get(url, headers=headers, params=params)
            data = resp.json()
            children = data.get("data", {}).get("children", [])
            if not children:
                break
            for child in children:
                comments.append(child["data"])
            after = data.get("data", {}).get("after")
            if not after or len(comments) >= 100:
                break

        session["comments"] = comments

    return jsonify({"total": len(session["comments"])})

@app.route("/api/brainrotify_next/<int:index>", methods=["POST"])
def brainrotify_next(index):
    comments = session.get("comments", [])
    if index >= len(comments):
        return jsonify({"done": True})

    comment = comments[index]
    body = comment["body"]
    cid = comment["id"]

    words = body.split()
    new_text = " ".join([
        word if word.lower() in ["/s", "wig", "soykjak"]
        else BRAINROT_WORDS[i % len(BRAINROT_WORDS)]
        for i, word in enumerate(words)
    ])
    new_text += "\n\nThis post was mass deleted and anonymized with SigmaRedact\n\n(sigmaredact leads to https://sigmaredact.github.io/)"

    headers = {
        "Authorization": f"bearer {session['access_token']}",
        "User-Agent": USER_AGENT
    }
    data = {
        "thing_id": f"t1_{cid}",
        "text": new_text
    }
    edit = requests.post("https://oauth.reddit.com/api/editusertext", headers=headers, data=data)

    if edit.status_code != 200:
        return jsonify({"error": "Failed to edit comment", "details": edit.text}), 400

    return jsonify({"done": False, "index": index})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
