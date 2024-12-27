# Setup gspread

<br>

## Enable API Access for a Project

1. Head to [Google Developers Console](https://console.cloud.google.com/apis/dashboard) and create a new project (or select the one you already have).
1. In the box labeled “Search for APIs and Services”, search for “Google Drive API” and enable it.
1. In the box labeled “Search for APIs and Services”, search for “Google Sheets API” and enable it.

<br>
<br>

## Using a Serive Account (Basically a Bot)

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

## Resources

- Follow [official documentation](https://docs.gspread.org/en/latest/oauth2.html#service-account) for setting up gspread apis.

<br>
<br>
<br>

# Setup Serial Port on Raspberry Pi

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

## Resources

- Follow [this video](https://www.youtube.com/watch?v=oevxqPk78sM) to get a basic understanding
- [Saravanan's Video](https://www.youtube.com/watch?v=LMQJAOjxFaw)

<br>
<br>
<br>
