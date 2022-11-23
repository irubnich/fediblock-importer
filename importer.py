import click
import requests
import validators
import yaml

INSTANCE_URL = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

LIST_URL = "https://joinfediverse.wiki/FediBlock"

@click.command()
@click.option('--list', default='lists/paulatothepeople.yaml', help='The list to import.')
def main(list):
  hosts = _parse_list(list)
  token = _get_token()
  _block_hosts(token, hosts)

def _parse_list(file):
  with open(file, "r") as stream:
    return yaml.safe_load(stream)

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

def _block_hosts(token, instances):
  for instance in instances:
    hostname = instance['hostname']
    result = validators.domain(hostname)
    if result == True:
      print(f'Blocking {hostname}... ', end='')
      response = requests.post(
        f'{INSTANCE_URL}/api/v1/admin/domain_blocks',
        headers={'Authorization': f'Bearer {token}'},
        json={'domain': hostname, 'severity': instance['severity'], 'public_comment': instance['public_comment']},
      )
      if response.status_code == 200:
        print('done!')
      else:
        print(f'error! Context: {response.json()}')

if __name__ == '__main__':
  main()
