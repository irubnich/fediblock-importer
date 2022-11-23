# fediblock-importer
This is a CLI utility that imports lists of instances to block into Mastodon. This is sometimes also called "defederation" or "domain blocking".

By default, this imports the instances from the [@PaulaToThePeople](https://climatejustice.social/@PaulaToThePeople) list from https://joinfediverse.wiki/FediBlock but you can import any list that's in the right format (see Advanced usage below).

**Note that this only works with instances running Mastodon v4.0 or higher because the [admin domain blocks API](https://docs.joinmastodon.org/methods/admin/domain_blocks/) is new.**

## 🚨 Warning 🚨
This tool is what one might call a "blunt instrument" because it just defederates instances en masse. It is essentially a large banhammer.

Sometimes this is what you want - the PaulaToThePeople list is the worst of the worst so I think it's fine to just suspend those all at once.

But in general, please consider who you choose to defederate. This does ultimately affect people after all.

## Usage
First, make sure you have a Python 3 environment set up. If you don't have one, I recommend [pyenv](https://github.com/pyenv/pyenv).

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. In your instance, go to Preferences -> Development.
3. Click New application. Name it anything you want and select the `admin:write` scope. Leave all other defaults.
4. Click into your new application and note the client ID and secret.
5. Fill in the `INSTANCE_URL`, `CLIENT_ID`, and `CLIENT_SECRET` variables in `importer.py`. `INSTANCE_URL` should start with `https://` and should not contain a trailing slash.
6. Run the script:
    ```bash
    python importer.py
    ```
7. Feel free to delete the application you created if you want.

## Advanced usage
This script can import any list that conforms to this YAML format:
```yaml
- hostname: the instance domain
  public_comment: the public reason you this is blocked
  severity: one of "silence", "suspend", or "noop"
```

You can see a full example in `lists/paulatothepeople.yaml`.

To import a custom list, run the script with the `--list` parameter:
```bash
python importer.py --list /path/to/list.yaml
```

## PaulaToThePeople list generator
I included the script I used to generate the `lists/paulatothepeople.yaml` file. It can be used to regenerate the yaml if that list changes:
```bash
python tools/paulatothepeople_list.py > lists/paulatothepeople.yaml
```

I vendored the list here just in case the Join the Fediverse wiki were to go down or something else happened to the list.

## Contributing
I will consider PRs, including those adding new lists. But keep in mind I will only accept new lists based on my own values, which are in line with point 1 of the [Mastodon Server Covenant](https://joinmastodon.org/covenant):

> 1. Active moderation against racism, sexism, homophobia and transphobia

## Credits
Thanks to [@PaulaToThePeople](https://climatejustice.social/@PaulaToThePeople) for compiling this list, and the broader Mastodon #FediBlock community for spreading it around.
