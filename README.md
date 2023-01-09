# Overview

Use this script to find available slots for you US visa appointment on  https://ais.usvisa-info.com/.

Their website uses cookies for authentication, so there are two modes of operation for this script:
- Obtain authentication cookie;
- Check available slots.

Once a new slot is found, you should receive an SMS (you'll need to create a free Twilio account).

## Authentication

I tried many different things and hacks to log in to the website in a truly "script" way - including services to bypass captchas,
imitating "human" behavior, patching the driver etc. None of that worked.

The only thing that works is a Selenium driver which actually goes through the auth flow. Somehow it only works on the machine
 you've previously used for manual authentication (likely your personal laptop) - I guess they remember some fingerprint or w/e.

Note that auth cookie is valid for about 4 hours last time I checked. So you have to run "auth" mode every couple of hours, and you can run "check" mode however often you like. "Every 5 minutes" worked fine for me so far. 

## Operation modes

You may want to either run both `auth` and `check` on your laptop, or split them in some way.
This is useful if you want to run `check` on a remote server which is only 24/7 and can monitor slots while your personal machine is turned off.

Auth mode:
```shell
python main.py auth
```
Check mode (will try to auth if you set `AUTO_REFRESH_AUTH=1`):
```shell
python main.py
```

### All on personal machine 

Run "check" mode on your laptop with `AUTO_REFRESH_AUTH=1`. It will of course only check for new slots while your machine is awake.

### `auth` on personal machine, `check` on a dedicated server
Run "auth" mode on your laptop, export cookie to a remote server and run "check" mode there with `AUTO_REFRESH_AUTH=0`. This will give you slightly better "check" coverage (assuming your server runs 24/7 - unlike your personal machine). 

## Setting up

### Prerequisites
1. Clone this repo
```shell
git clone https://github.com/arseniy-panfilov/usvisa-check-slots.git
```
2. Get yourself python 3.7, e.g. using [pyenv](https://github.com/pyenv/pyenv);
3. Install script requirements:
```shell
pip install -r requirements.txt
```
4. Download [Chrome driver](https://chromedriver.chromium.org/downloads) for Selenium. Make sure driver version matches your browser version (you can find it in `Chrome -> About Chrome`):
5. You might need to `right click -> open` on the driver if you're on Mac to pass the security check;
6. In the repo folder, create an `.env` file:
```shell
cp .env.example .env
```
7. Provide values for all the env variables (see description below);

### Env variables

- `ACCOUNT_ID`: group ID from the website. You can see it in the url, e.g. `https://ais.usvisa-info.com/en-ca/niv/schedule/<ACCOUNT_ID>/continue_actions`
- `CHROMEDRIVER_PATH`: path to the Chrome driver, e.g. `/usr/local/bin/chromedriver` or wherever you place it;
- `USVISA_COOKIE_PATH`: where to store auth cookie, can be any location e.g. `cookie/cookie.txt`;
- `USVISA_USER / USVISA_PASSWORD`: credentials to login on https://ais.usvisa-info.com/en-ca/niv/users/sign_in
- `USVISA_CURRENT_DATE`: date in `YYYY-MM-DD` format. If you already have an appointment, put its date here so that bot doesn't bother you with irrelevant dates;
- `AUTO_REFRESH_AUTH`: whether to automatically refresh auth cookie. Set to `1` if you're running everything on your personal laptop; set to `0` if you're running `check` mode on a VPS or something like that - it won't be able to obtain auth cookie anyway.

Twilio configuration:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_TO_NUM`
- `TWILIO_FROM_NUM`

### Tweaking the code

You may want to modify cities list in `src.run.CITIES_TO_CHECK`. I think Montreal doesn't actually take appointments now, and I had most luck with Ottawa.

### Running 

1. Try running it manually:
 ```shell
 python main.py
 ```
2. Make the script run every 5 minutes or so. Depending on your OS it can be `cron` for *nix, `launchd` for macOS etc. 
3. **(Optional)** if you want to run `check` on a remote server, you'll need to export the auth cookie there. So you should end with running this on your personal machine every hour:
```shell
python main.py auth
```
and then export it to your dedicated server, e.g.:
```shell
scp cookie/cookie.txt yourvps:/path/to/cookie.txt
```
On the server itself, repeat all the steps above, but make sure to set `AUTO_REFRESH_AUTH=0` in the `.env` file. This mode also doesn't require `USVISA_USER / USVISA_PASSWORD` so you can leave them empty. 

Example script to export cookie:
```
#!/bin/bash

venv/bin/python main.py
scp cookie/cookie.txt <YOUR_SSH>:/home/apps/usvisa/cookie/cookie.txt
echo "Cookie exported"
```

### Setting up `launchd` on a macOS machine

Create a `.plist` file for the service, e.g.
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.anon.usvisa-watcher</string>
    <key>WorkingDirectory</key>
    <string>/Users/anon/dev/usvisa/</string>
    <key>ProgramArguments</key>
    <array>
        <string>./export-cookie.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>StandardOutPath</key>
    <string>/tmp/usvisa.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/usvisa.log</string>
</dict>
</plist>
```

Then run:
```
cp com.custom.usvisa-watcher.plist ~/Library/LaunchAgents/com.anon.usvisa-watcher.plist
launchctl load -w ~/Library/LaunchAgents/com.anon.usvisa-watcher.plist
```

Make sure it's added:
```
➜  ~ launchctl list | grep usvisa
-	0	com.anon.usvisa-watcher
```

To run immediately:
```
launchctl kickstart gui/501/com.anon.usvisa-watcher
```



