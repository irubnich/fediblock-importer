import os
import click
import requests
import validators
import yaml

from operator import itemgetter
from dotenv import load_dotenv

GENERATED_COMMENT = '<generated>'

load_dotenv()

INSTANCE_URL = os.getenv('INSTANCE_URL')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

class ValidationException(BaseException):
  pass

class AuthorizationException(BaseException):
  pass

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
  if ctx.invoked_subcommand is None:
    import_list()

@cli.command()
@click.option('--list', default='lists/paulatothepeople.yaml', help='The list to import.')
def import_list(list):
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

@cli.command()
@click.option('--at-least', default='ALL', required=True, help='Min. # of instances required to use a block')
@click.option('--comment', default=GENERATED_COMMENT, help='Specify public comment')
@click.argument('hostnames', required=True, nargs=-1)
def aggregate(at_least, comment, hostnames):
  try:
    token = _get_token()
  except AuthorizationException as e:
    print('Authorization error. Check your application\'s permissions, client ID, and secret, and try again.')
    print(f'Error details: {e}')
    return
  # Unless otherwise specified, ALL trusted instances must agree.
  # This is the safest default.
  if str(at_least).lower() == 'all':
    at_least = len(hostnames)
  else:
    at_least = int(at_least)
  blocked_domains = {}
  # Fetch the block lists from the trusted instances.
  sorted_hostnames = list(hostnames)
  sorted_hostnames.sort()
  for hostname in hostnames:
    host_blocks = fetch_blocks(hostname)
    for block in host_blocks:
      domain, severity = itemgetter('domain', 'severity')(block)
      if str(domain).find("*") > -1:
        # Masked domain, which we can't use here
        continue
      blocked = blocked_domains.get(domain, dict())
      # This ends up looking like:
      # malefactor.example.com:
      #   suspend: [trusted1.tld, trusted2.tld]
      #   silence: [trusted3.tld]
      blocked[severity] = blocked.get(severity, list())
      blocked[severity].append(hostname)
      blocked_domains[domain] = blocked
  to_block = list()
  for blocked_domain, blocks in blocked_domains.items():
    suspenders = blocks.get('suspend', list())
    silencers = blocks.get('silence', list())
    if len(suspenders) >= at_least:
      print(f'Will suspend: {blocked_domain}')
      to_block.append({
        'hostname': blocked_domain,
        'severity': 'suspend',
        'public_comment': comment if comment != GENERATED_COMMENT else f'via: {" ".join(suspenders)}'
      })
    elif len(suspenders) + len(silencers) >= at_least:
      print(f'Will silence: {blocked_domain}')
      to_block.append({
        'hostname': blocked_domain,
        'severity': 'silence',
        'public_comment': comment if comment != GENERATED_COMMENT else f'via: {" ".join(list(suspenders + silencers))}'
      })
    else:
      print(f'Not enough strikes: {blocked_domain}')

  _block_hosts(token, to_block)

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
  print(f'Using list: {file}')
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

def fetch_blocks(hostname):
  print(f'Fetching blocklist from {hostname}')
  host = hostname
  if not host.startswith('https://'):
    host = f'https://{host}'
  if not host.endswith('/'):
    host = f'{host}/'
  # In theory, you should be able to fetch this with an Admin token ...
  # but that seems broken at the moment?
  response = requests.get(f'{host}api/v1/instance/domain_blocks', headers={'User-Agent': 'fediblock-importer'})
  blocks = yaml.safe_load(response.content)
  if blocks is None:
    print(f'WARNING: {host} does not publish blocks, or does not have any.')
    return list()
  else:
    print(f'Found {len(blocks)} from {host}')
  return blocks

def _block_hosts(token, instances):
  url = INSTANCE_URL.rstrip('/')

  existing_blocks = fetch_blocks(INSTANCE_URL)
  existing_severities = dict()
  for block in existing_blocks:
    domain, severity = itemgetter('domain', 'severity')(block)
    existing_severities[domain] = severity

  for instance in instances:
    hostname = instance['hostname']
    severity = instance['severity']
    result = validators.domain(hostname)
    if not result:
      continue

    existing_severity = existing_severities.get(hostname, '')
    if existing_severity == 'suspend' or (existing_severity == 'silence' and severity == 'silence'):
      # Try to reduce requests, because the API will limit you after a few hundred.
      continue
    verb = 'Suspending' if severity == 'suspend' else 'Silencing'
    print(f'{verb} {hostname}... ', end='')
    response = requests.post(
      f'{url}/api/v1/admin/domain_blocks',
      headers={'Authorization': f'Bearer {token}'},
      json={'domain': hostname, 'severity': severity, 'public_comment': instance['public_comment']},
    )
    if response.status_code == 200:
      print('done!')
    else:
      print(f'error! Context: {response.json()}')

if __name__ == '__main__':
  cli()
