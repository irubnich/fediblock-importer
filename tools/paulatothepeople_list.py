# helper script to scrape the PaulaToThePeople list and turn it into a format importable by the importer
# https://joinfediverse.wiki/FediBlock
# usage: python paulatothepeoplelist.py > list.yaml

from bs4 import BeautifulSoup
import requests
import yaml

def main():
  page = requests.get("https://joinfediverse.wiki/FediBlock")
  soup = BeautifulSoup(page.text, "html.parser")

  rows = soup.find("table").find("tbody").find_all("tr")

  instances = []

  for row in rows:
    instance = {}

    host = row.find('th').text.rstrip()
    other = row.find_all('td')

    if host != "instance" and len(host) > 0:
      instance['hostname'] = host
      instance['severity'] = 'suspend'
    else:
      continue

    instance['public_comment'] = other[1].text.rstrip()
    if len(instance['public_comment']) == 0:
      instance['public_comment'] = other[0].text.rstrip()

    instances.append(instance)

  print(yaml.dump(instances))

if __name__ == '__main__':
  main()