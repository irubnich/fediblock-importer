# fediblock-importer
This is a CLI utility that imports domain blocklists into Mastodon.

By default, this imports the instances from the PaulaToThePeople list from https://joinfediverse.wiki/FediBlock but you can import any list that's in the right format (see Advanced usage below).

## Getting started
First, make sure you have a Python 3 environment set up. If you don't have one, I recommend [pyenv](https://github.com/pyenv/pyenv).

1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
2. Create an application in the admin panel:
    1. Go to Preferences -> Development.
    2. Click New application. Name it anything you want and select the `admin:write` scope. Leave all other defaults.
    3. Click into your new application and note the client ID and secret.
3. Fill in the `INSTANCE_URL`, `CLIENT_ID`, and `CLIENT_SECRET` variables in `importer.py`. `INSTANCE_URL` should start with `https://` and should not contain a trailing slash.
4. Run the script:
    ```bash
    python importer.py
    ```
5. Feel free to delete the application you created if you want.

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
