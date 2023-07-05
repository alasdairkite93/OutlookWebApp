import identity.web
import sys
import requests
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
import app_config
import json
from azure.identity import DeviceCodeCredential, ClientSecretCredential
from azure.identity.aio import OnBehalfOfCredential
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

this = sys.modules[__name__]

__version__ = "0.7.0"  # The version of this sample, for troubleshooting purpose

app = Flask(__name__)
app.config.from_object(app_config)
assert app.config["REDIRECT_PATH"] != "/", "REDIRECT_PATH must not be /"
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)


@app.route("/login")
def login():

    dict_logged = auth.log_in(scopes=app_config.SCOPE, redirect_uri='https://www.testoutlookapp.azurewebsites.net/getAToken')
    result = completeLogin(dict_logged)
    if "error" in result:
        print('ERROR IN RESULT')
        return render_template("auth_error.html", result=result)
    print('RETURNING INDEX')
    return redirect(url_for("index"))

    # return render_template("login.html", version=__version__, **auth.log_in(
    #     scopes=app_config.SCOPE, # Have user consent to scopes during log-in
    #     redirect_uri='https://www.testoutlookapp.azurewebsites.net/getAToken',
    #     # redirect_uri=url_for("auth_response", _external=True), # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
    #     ))

def completeLogin(dict_logged):
    result = auth.complete_log_in(dict_logged)
    return result

@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        print('ERROR IN RESULT')
        return render_template("auth_error.html", result=result)
    print('RETURNING INDEX')
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=auth.get_user(), version=__version__)


@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    print('TOKEN: ', token)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)


@app.route("/getmail")
def getMail():
    print('GET MAIL')
    token = auth.get_token_for_user(app_config.SCOPE)
    endpoint = "https://graph.microsoft.com/v1.0/me/messages"
    print('TOKEN: ', token['access_token'])

    url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"

    # Set the headers for the API call
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json"
    }

    # Send the API request and get the response
    response = requests.get(url, headers=headers)

    # Parse the response as JSON
    data = response.json()
    print('Data ', data)
    return render_template('display.html', result=data)


@app.route('/sendmail', methods=['GET', 'POST'])
def sendMail():

    token = auth.get_token_for_user(app_config.SCOPE)

    subject = 'First Message'
    body = 'Hey, first message.'
    recipient = 'alasdairkite93@gmail.com'

    request_body = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'text',
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': recipient
                    }
                }
            ]
        }
    }

    request_url = 'https://graph.microsoft.com/v1.0/me/sendmail'

    response = requests.post(url=request_url, headers={'Authorization':token['access_token'], 'Content-type':'application/json'}, data=json.dumps(request_body))
    print(response.status_code)
    print(response.content)
    return render_template('index.html', user=auth.get_user(), version=__version__)

if __name__ == "__main__":
    app.run(debug=True)
