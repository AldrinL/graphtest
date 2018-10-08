"""Configuration settings for running the Python auth samples locally.

In a production deployment, this information should be saved in a database or
other secure storage mechanism.
"""
import os

REDIRECT_URI = os.environ.get('REDIRECT_URI', 'https://graphtest-aldrinl.c9users.io/login/authorized')

# AUTHORITY_URL ending determines type of account that can be authenticated:
# /organizations = organizational accounts only
# /consumers = MSAs only (Microsoft Accounts - Live.com, Hotmail.com, etc.)
# /common = allow both types of accounts
AUTHORITY_URL = 'https://login.chinacloudapi.cn/common'

AUTH_ENDPOINT = '/oauth2/authorize'
TOKEN_ENDPOINT = '/oauth2/token'

RESOURCE = 'https://microsoftgraph.chinacloudapi.cn/'
API_VERSION = 'v1.0'
SCOPES = ['User.Read'] # Add other scopes/permissions as needed.


# This code can be removed after configuring CLIENT_ID and CLIENT_SECRET above.
#if 'ENTER_YOUR' in CLIENT_ID or 'ENTER_YOUR' in CLIENT_SECRET:
#    print('ERROR: config.py does not contain valid CLIENT_ID and CLIENT_SECRET')
#    import sys
#    sys.exit(1)
