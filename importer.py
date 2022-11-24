import click
import requests
import validators
import yaml

INSTANCE_URL = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

class ValidationException(BaseException):
  pass

class AuthorizationException(BaseException):
  pass

@click.command()
@click.option('--list', default='lists/paulatothepeople.yaml', help='The list to import.')
def main(list):
  try:
    _validate()
  except ValidationException as e:
    print(f'Validation error: {e}')
    return

  hosts = _parse_list(list)

  try:
    token = _get_token()
  except AuthorizationException as e:
    print('Authorization error. Check your application\'s permissions, client ID, and secret, and try again.')
    print(f'Error details: {e}')
    return

  _block_hosts(token, hosts)

def _validate():
  result = validators.url(INSTANCE_URL)
  if result != True:
    raise ValidationException('Invalid INSTANCE_URL')

  result = validators.length(CLIENT_ID, min=1)
  if result != True:
    raise ValidationException('You must provide a CLIENT_ID')

  result = validators.length(CLIENT_SECRET, min=1)
  if result != True:
    raise ValidationException('You must provide a CLIENT_SECRET')

def _parse_list(file):
  with open(file, "r") as stream:
    return yaml.safe_load(stream)

def _get_token():
  url = INSTANCE_URL.rstrip('/')

  print(f'Go here in your browser and copy the code: {url}/oauth/authorize?client_id={CLIENT_ID}&scope=admin:write&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code')
  code = input("Enter the code: ").rstrip()
  token_response = requests.post(
    f'{url}/oauth/token',
    data={
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET,
      'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
      'grant_type': 'authorization_code',
      'code': code,
      'scope': 'admin:write',
    },
  )

  json = token_response.json()
  if 'access_token' in json.keys():
    return json['access_token']
  else:
    raise AuthorizationException(json)

def _block_hosts(token, instances):
  url = INSTANCE_URL.rstrip('/')

  for instance in instances:
    hostname = instance['hostname']
    result = validators.domain(hostname)
    if result == True:
      print(f'Blocking {hostname}... ', end='')
      response = requests.post(
        f'{url}/api/v1/admin/domain_blocks',
        headers={'Authorization': f'Bearer {token}'},
        json={'domain': hostname, 'severity': instance['severity'], 'public_comment': instance['public_comment']},
      )
      if response.status_code == 200:
        print('done!')
      else:
        print(f'error! Context: {response.json()}')

if __name__ == '__main__':
  main()
