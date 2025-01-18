# API

<br>
<br>

## Setting up gspread

Follow [official documentation](https://docs.gspread.org/en/latest/oauth2.html#service-account) for setting up gspread apis.

<br>

### Enable api access for a project

1. Head to [Google Developers Console](https://console.cloud.google.com/apis/dashboard) and create a new project (or select the one you already have).
1. In the box labeled “Search for APIs and Services”, search for “Google Drive API” and enable it.
1. In the box labeled “Search for APIs and Services”, search for “Google Sheets API” and enable it.

<br>

### Using a serive account (basically a bot)

1. Enable to API access if not done already.
1. Go to “APIs & Services > Credentials” and choose “Create credentials > Service account key”.
1. Fill out the form
1. Click “Create” and “Done”.
1. Press “Manage service accounts” above Service Accounts.
1. Press on ⋮ near recently created service account and select “Manage keys” and then click on “ADD KEY > Create new key”.
1. Select JSON key type and press “Create”.

1. The downloaded json file will be something like

   ```json
   {
       "type": "service_account",
       "project_id": "api-project-XXX",
       "private_key_id": "2cd … ba4",
       "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
       "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
       "client_id": "473 … hd.apps.googleusercontent.com",
       ...
   }
   ```

1. Note down the path of the json file and the `client_email` present in the json file.
1. Very important! Go to your spreadsheet and share it with a client_email from the step above.
1. Move the downloaded file to `~/.config/gspread/service_account.json`. Windows users should put this file to `%APPDATA%\gspread\service_account.json`.

<br>
<br>
<br>

# Raspberry pi setup

<br>
<br>

## Static ip address

- Use the latest network manager tool.

  ```bash
  sudo nmtui
  ```

<br>
<br>

## Setting up serial port on raspberry pi

To get a basic understanding, watch [this video](https://www.youtube.com/watch?v=oevxqPk78sM) and [Saravanan's video](https://www.youtube.com/watch?v=LMQJAOjxFaw).

Follow the following steps:

1. Launch the raspberry pi configuration tool using `sudo raspi-config`
1. Select "Interface Options" and then select "Serial Port"
1. Click "No" for login shell.
1. Click "Yes" for enabling serial port hardware.
1. Click on "Finish" and reboot the Pi.
1. Open the config.txt file and see if `enable_uart=1` is present at the bottom of the file.

   ```bash
   sudo nano /boot/firmware/config.txt
   ```

1. Try the following command and confirm if `/dev/ttyS0`

   ```bash
   ls -l /dev/t*
   ```

1. Try the following commands aswell

   ```bash
   ls /dev/serial0
   ```

1. Try the following command and confirm if it points to `ttyS0`

   ```bash
   ls -l /dev/serial0
   ```

<br>
<br>

## Setting up a cron job

Follow these steps :

1. Use `crontab -e` to open the crontab file.
1. The following syntax is used to enter a cron task:

   ```
   * * * * * /path/to/command
   ```

   - Where the five asterisks represent:

     - Minute (0-59)
     - Hour (0-23)
     - Day of Month (1-31)
     - Month (1-12)
     - Day of Week (0-7, where both 0 and 7 represent Sunday)

   - To run a script every day at 10:15 PM:

     ```
         15 22 * * * /home/user/script.sh
     ```

   - To run a script every 5 minutes:

     ```
     */5 * * * * /path/to/command
     ```

1. Additionaly ensure the following:

   - Ensure your script has executable permissions using :

     ```
     chmod +x /path/to/your/script.sh
     ```

   - If the script uses any environment variables, it should be included in the crontab file in the following syntax :

     ```
     #syntax
     ENV_VARIABLE=value

     #example
     EMAIL=mymail.com
     ```

<br>
<br>

## Using minicom

- Ensure minicom is installed using the relevant linux package manager.
- Run the following :
  ```
  sudo minicom -s
  ```
- I get an interface to change some settings where I set the correct port setting to `ttyS0` in this case and the minicom is got upon escaping after the settings interface.

<br>
<br>

## SSH

Check if the device is in the network using :

```bash
ping <username>@<hostname>.local
```

SSH to it using :

```bash
ssh <username>@<hostname>.local
```

<br>
<br>
<br>

# Google smtp

Need to create a google app and use the generated app password to be able to send gmail using smtp server.

- The email and the app password is to be saved as environment variables (in ~/.bashrc in the case of linux)
