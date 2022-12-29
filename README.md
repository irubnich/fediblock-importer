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
5. Copy `.env.example` to just `.env`, edit it, and fill in all the values according to the instructions within.
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

## Trusted upstream instances

If you run a small instance and trust the blocking decisions of other specific instances, and those instances make their block lists public, you can aggregate their lists into your own.

```bash
python importer.py aggregate trusted1.example.com trusted2 trusted3...
```

Any domain blocked by *all* the trusted instances will be added to yours.

If you have more than a few trusted instances, you might also use `--at-least` to specify some smaller number to trust.
For example, if you have 5 trusted instances, you might want to block domains listed by any 4 of them.

## On public block lists

If you make your own block list public, that list will be used to try to reduce the number of calls to your instance.
You can find this in the Mastodon UI under:

Preferences > Administration > Server Settings > About > Show ...

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
