import requests
import requests.auth
import os

# In: General Settings > App clients > Show details
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

callback_uri = "http://localhost:3000/callback"

# Find this in: App Integration > Domain
cognito_app_url = os.getenv('cognito_app_url')

# this is the response code you received - you can get a code to test by going to
# going to App Integration > App client settings > Lunch Hosted UI
# and doing the login steps, even if it redirects you to an invalid URL after login
# you can see the code in the querystring, for example:
# http://localhost:8001/accounts/amazon-cognito/login/callback/?code=b2ca649e-b34a-44a7-be1a-121882e27fe6
code="1234"

token_url = f"{cognito_app_url}/oauth2/token"
auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

params = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "code": code,
    "redirect_uri": callback_uri
    }

response = requests.post(token_url, auth=auth, data=params, headers=headers)

print(response.json()) # don't judge me, this is an example