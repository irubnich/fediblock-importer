# This script suspends the instances from this list: https://joinfediverse.wiki/FediBlock
# HOW TO USE
# 1. Go to Preferences -> Development.
# 2. Create a new application. Name it anything you want and give it the "admin:write" scope.
#    Leave all other defaults.
# 3. Click into your new application and note the client ID and secret.
# 4. Fill in the INSTANCE_URL, CLIENT_ID, and CLIENT_SECRET variables below.
#    INSTANCE_URL should start with https:// and should not contain a trailing slash.
# 5. Run this to install dependencies:
#    pip install requests bs4 validators
# 6. Run the script and follow the instructions:
#    python importer.py

import requests
from bs4 import BeautifulSoup
import validators

INSTANCE_URL = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

LIST_URL = "https://joinfediverse.wiki/FediBlock"

def main():
  hosts = _get_hosts()
  token = _get_token()
  _block_hosts(token, hosts)

def _get_hosts():
  page = requests.get(LIST_URL)
  soup = BeautifulSoup(page.content, "html.parser")
  return soup.select("table tbody tr th")

def _get_token():
  print(f'Go here in your browser and copy the code: {INSTANCE_URL}/oauth/authorize?client_id={CLIENT_ID}&scope=admin:write&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code')
  code = input("Enter the code: ").rstrip()
  token_response = requests.post(
    f'{INSTANCE_URL}/oauth/token',
    data={
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET,
      'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
      'grant_type': 'authorization_code',
      'code': code,
      'scope': 'admin:write',
    },
  )
  return token_response.json()['access_token']

def _block_hosts(token, hosts):
  for instance in hosts:
    hostname = instance.string.replace('\n', '')
    result = validators.domain(hostname)
    if result == True:
      print(f'Blocking {hostname}...', end='')
      response = requests.post(
        f'{INSTANCE_URL}/api/v1/admin/domain_blocks',
        headers={'Authorization': f'Bearer {token}'},
        json={'domain': hostname, 'severity': 'suspend', 'public_comment': 'imported from PaulaToThePeople list'},
      )
      if response.status_code == 200:
        print('Done!')
      else:
        print(f'Error occurred! Context: {response.json()}')

if __name__ == '__main__':
  main()
