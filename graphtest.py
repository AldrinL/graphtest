"""ADAL/Flask sample for Microsoft Graph """
# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
# See LICENSE in the project root for license information.
import os
import urllib.parse
import uuid

import adal
import flask
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, validators
from flask_bootstrap import Bootstrap
import json

import config

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # enable non-HTTPS for testing
APP = flask.Flask(__name__, template_folder='static/templates')
APP.debug = True
Bootstrap(APP)
APP.secret_key = 'development'

class AppForm(FlaskForm):
    AppID = StringField('AppID', validators=[validators.Length(min=25, max=40)])
    Secret = StringField('Secret', validators=[validators.Length(min=30)])
    submit = SubmitField("Connect")
class GraphForm(FlaskForm):
    API = StringField(validators=[validators.Length(min=2)], default='https://microsoftgraph.chinacloudapi.cn/v1.0/me')
    submit = SubmitField("Test")
class GPForm(FlaskForm):
    api = StringField("API endpoint", validators=[validators.Length(min=2)], default='https://microsoftgraph.chinacloudapi.cn/v1.0/me', )
    method = SelectField('HTTP method', choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE')])
    body = TextAreaField("Request Body")
    submit = SubmitField("Test")
    

SESSION = requests.Session()

@APP.route('/', methods=('GET', 'POST'))
def homepage():
    """Render the home page."""
    msapp = AppForm()
    if msapp.validate_on_submit():
        SESSION.APP = msapp
        return flask.redirect('/login')
    return flask.render_template('homepage.html', msapp=msapp, redirect_uri = config.REDIRECT_URI)

@APP.route('/login')
def login():
    """Prompt user to authenticate."""
    auth_state = str(uuid.uuid4())
    SESSION.auth_state = auth_state
    # For this sample, the user selects an account to authenticate. Change
    # this value to 'none' for "silent SSO" behavior, and if the user is
    # already authenticated they won't need to re-authenticate.
    prompt_behavior = 'select_account'

    params = urllib.parse.urlencode({'response_type': 'code',
                                     'client_id': SESSION.APP.AppID.data,
                                     'redirect_uri': config.REDIRECT_URI,
                                     'state': auth_state,
                                     'resource': config.RESOURCE,
                                     'prompt': prompt_behavior})

    return flask.redirect(config.AUTHORITY_URL + '/oauth2/authorize?' + params)

@APP.route('/login/authorized')
def authorized():
    """Handler for the application's Redirect Uri."""
    code = flask.request.args['code']
    auth_state = flask.request.args['state']
    if auth_state != SESSION.auth_state:
        raise Exception('state returned to redirect URL does not match!')
    auth_context = adal.AuthenticationContext(config.AUTHORITY_URL, api_version=None)
    token_response = auth_context.acquire_token_with_authorization_code(
        code, config.REDIRECT_URI, config.RESOURCE, SESSION.APP.AppID.data, SESSION.APP.Secret.data)
    SESSION.headers.update({'Authorization': token_response['accessToken'],
                            'User-Agent': 'adal-sample',
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'SdkVersion': 'sample-python-adal',
                            'return-client-request-id': 'true'})
    return flask.redirect('/graphcall')

@APP.route('/graphcall', methods=('GET', 'POST'))
def graphcall():
    """Confirm user authentication by calling Graph and displaying some data."""
    gp = GPForm()
    if gp.validate_on_submit():
        SESSION.API = gp.api.data
        endpoint = SESSION.API
        http_headers = {'client-request-id': str(uuid.uuid4())}
        if gp.method.data == 'GET':
            response = SESSION.get(endpoint, headers=http_headers, stream=False).json()
        elif gp.method.data == 'POST':    
            response = SESSION.post(endpoint, headers=http_headers, stream=False, data=gp.body.data).json()
        elif gp.method.data == 'PUT':    
            response = SESSION.put(endpoint, headers=http_headers, stream=False, data=gp.body.data).json()
        elif gp.method.data == 'PATCH':    
            response = SESSION.patch(endpoint, headers=http_headers, stream=False, data=gp.body.data).json()
        elif gp.method.data == 'DELETE':    
            response = SESSION.delete(endpoint, headers=http_headers, stream=False, data=gp.body.data).json()
        print(SESSION.API, gp.body.data, gp.method.data)
        return flask.render_template('graphcall.html',
                                 response=response,
                                 endpoint=endpoint,
                                 headers=SESSION.headers,
                                 gp = gp)
    return flask.render_template('graphcall.html', gp = gp)

if __name__ == '__main__':
    HOST = os.environ.get('IP', '0.0.0.0')
    try:
        PORT = int(os.environ.get('PORT', '8080'))
    except ValueError:
        PORT = 5555
    APP.run(HOST, PORT)
#    APP.run()
