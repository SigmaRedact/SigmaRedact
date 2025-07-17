SigmaRedact is a Redact clone for Reddit that edits your last 100 comments (not posts or replies, yet) into brainrot. We require some changes to app.py so we require a build (takes around ~2 minutes).

What is SigmaRedact?
A web app that connects to Reddit, retrieves your comments, and overwrites them with brainrotted text for anonymity, using Flask and Reddit's OAuth API.

Prerequisites
You’ll need:

Python 3.7+

pip installed

A Reddit App for OAuth (you will learn on step 3)

Step 1: Set Up Your Project Structure
SigmaRedact/
├── app.py
├── templates/
│   ├── index.html
│   └── redact.html


Step 2: Install Python Requirements
In your terminal:
pip install flask requests


Step 3: Create a Reddit App
Go to https://www.reddit.com/prefs/apps

Scroll down and click “create another app”

Fill out:

Name: SigmaRedact

App type: web app

Redirect URI: http://localhost:8000/callback

About URL: https://sigmaredact.github.io/ (optional)

Description: Make Reddit posts more sigma with maximum rizz™

Copy your:

client_id (under app name)

secret (shown after creation)

Step 4: Edit app.py
Replace:

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_SECRET_KEY"

With your real Reddit app values.

Also replace:
app.secret_key = "YOUR_SECRET_KEY"

Step 5: Run SigmaRedact
Open Command Prompt or PowerShell

Navigate to your project folder:

1. cd C:\where\you\put\SigmaRedact

2. Run:
python app.py
Make sure Python is installed and added to PATH (you can test with python --version).

🍎 On macOS
1. Open Terminal

2. Navigate to your folder:
cd ~/where/you/put/SigmaRedact

4. Run:
python3 app.py
⚠️ On macOS, use python3 because python may refer to Python 2.

🐧 On Linux:
1. Open Terminal

2. Navigate to your project folder:
cd ~/SigmaRedact

3. Run:
python3 app.py

💡 If python3 isn't recognized, install Python using:
sudo apt install python3 python3-pip

✅ If Flask Isn't Installed:
Install Flask using:
pip install flask requests
# or sometimes
pip3 install flask requests
