import base64
import logging
from base64 import b64encode

import requests as re

import os
# clientid = '4d76436f1f6748b89e03ebe8d633dc3d'
# secretkey = '6gcwvLk94I0id6ke4ATxZqXcTPKnnpxyof16hXBu'
from dotenv import load_dotenv

token_url = 'https://login.eveonline.com/oauth/token'
verify_url = 'https://login.eveonline.com/oauth/verify'

load_dotenv()
eve_id = os.getenv('EVE_CLIENT_ID')
eve_secret = os.getenv('EVE_SECRET_KEY')
auth = 'Basic ' + b64encode('{}:{}'.format(eve_id, eve_secret).encode()).decode("utf-8")
REDIRECT_URI = "http://localhost:8000/callback/"

def authorize(code):
    """
    Validate an authorization token recieved from

    :param code: client id and secret to authenticate with
    :return: json response
    """


    data = {
        'grant_type': 'authorization_code',
        'code': code,
    }

    r = re.post(token_url, json=data, headers={'Authorization': auth})
   # if r.status_code != 200:
   #     logging.log('ESI request error: {} - {}'.format(r.status_code, r.content))
   #     raise Exception('Error authorizing')

    return r.json()


def verify(access_token, token_type):
    """
    Verifies the access token and retrieves character information

    :param auth: authorization header to be sent
    :return: character information
    """
    r = re.get(verify_url, headers={'Authorization': '{} {}'.format(token_type, access_token)})
    return r.json()

def get_accesstoken():
    f = open("keys.key", "r")
    accesstoken = f.read().split(" ")[0]
    return accesstoken

def refresh(CLIENT_ID, CLIENT_SECRET, refresh_token):
    """
    Refresh expired access token.

    :param CLIENT_ID:
    :param CLIENT_SECRET:

    :param refresh_token: refresh token associated with the expired access token
    :return: json response
    """
    base64_encoded_clientid_clientsecret = base64.b64encode(str.encode(f'{CLIENT_ID}:{CLIENT_SECRET}'))  # concatenate with : and encode in base64
    base64_encoded_clientid_clientsecret = base64_encoded_clientid_clientsecret.decode('ascii')  # turn bytes object into ascii string


    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': f'Basic {base64_encoded_clientid_clientsecret}'
        }

    data = {
        "grant_type": "refresh_token",
        'redirect_uri' : REDIRECT_URI,
        "refresh_token": refresh_token
    }

    r = re.post(token_url, json=data, headers={'Authorization': auth})

   # if r.status_code != 200:
   #     logging.log('Error refreshing token: {}\n'.format(token_id))
  #      raise Exception('Error refreshing token')
    resp = r.json()
    return resp