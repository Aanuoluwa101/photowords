import requests
import requests.auth

# In: General Settings > App clients > Show details
client_id = "r5n1u8dodck65qnftsc26bb4u"
client_secret = "ol6qjprdhfmd5hnvrn48vcl07uak4l4l4d33cfm878ljqcssc08"

callback_uri = "http://localhost:3000/callback"

# Find this in: App Integration > Domain
cognito_app_url = "https://eu-west-2imng8pdh4.auth.eu-west-2.amazoncognito.com"

# this is the response code you received - you can get a code to test by going to
# going to App Integration > App client settings > Lunch Hosted UI
# and doing the login steps, even if it redirects you to an invalid URL after login
# you can see the code in the querystring, for example:
# http://localhost:8001/accounts/amazon-cognito/login/callback/?code=b2ca649e-b34a-44a7-be1a-121882e27fe6
code="66c59979-59da-468e-84cf-e6e15bf7339f"

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