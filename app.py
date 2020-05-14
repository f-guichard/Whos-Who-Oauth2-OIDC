import json
import os
import sqlite3

from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

from repertoire.database import init_db_command
from entites.utilisateur import User

# Configuration
# Voir .credentials.oauth2 pour les exports
_CLIENT_ID = os.environ.get("CLIENT_ID", None)
_CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def print_oauth2_clients():
    print(f'_CLIENT_ID: {_CLIENT_ID}')
    print(f'_CLIENT_SECRET: {_CLIENT_SECRET}')

def get_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)

# database setup
try:
    init_db_command()
except Exception as e:
    print(f'Erreur init db: {e}')
    pass

# OAuth 2 client setup
client_oauth2 = WebApplicationClient(_CLIENT_ID)

# Flask-Login: retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Avatar:</p>"
            '<img src="{}" alt="Google avatar"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.nom, current_user.email, current_user.avatar
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

@app.route("/login")
def login():
    print(f'Catch /login from {request}')
    print_oauth2_clients()

    provider_cfg = get_provider_cfg()
    print(f'oidc conf: {provider_cfg}')
    
    authorization_endpoint = provider_cfg["authorization_endpoint"]
    app_redirect_uri=request.base_url + "/callback" ## client en local !
    print(f'Params oauth2 builder: \n- {authorization_endpoint},\n- {app_redirect_uri}')

    request_uri = client_oauth2.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=app_redirect_uri, 
        scope=["openid", "email", "profile"],
        prompt="select_account"
    )
    return redirect(request_uri)

#Necessaire pour récupérer le code d'autorisation à rejouer sur /token
@app.route("/login/callback")
def callback():
    print(f'Catch /login/callback from {request}')
    
    code = request.args.get("code")

    provider_cfg = get_provider_cfg()
    token_endpoint = provider_cfg["token_endpoint"]

    token_url, headers, body = client_oauth2.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    print(f'Token build: {token_url}, {headers}, {body}.')

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(_CLIENT_ID, _CLIENT_SECRET),
    )

    print(f'Token recupere: {token_response.json()}.')
    client_oauth2.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = provider_cfg["userinfo_endpoint"]
    uri, headers, body = client_oauth2.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        ravatar = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "email_verified field: pb email ", 400

    user = User(
        id_=unique_id, nom=users_name, email=users_email, avatar=ravatar
    )

    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, ravatar)

    login_user(user)

    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    print(f'Launching app....')
    app.run(ssl_context=('.certs/mon_certificat_serveur.pem', '.certs/ma_cle_privee.pem'))
