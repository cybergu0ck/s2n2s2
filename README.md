# Dev Notes

<br>
<br>

## Todo

1. Add exception handling and in the case of exception send fail log to admin number
1. Add sim center number in the code
1. Add whatsapp support
1. Figure out the mechanism for sending coms
1. Calculate the size of sd card needed based on log files generated or figure out a way to clean the log files.
1. Add google forms integration.
1. Organise the entire codebase
1. Figure out mix up between phone and whatsapp number input with and without country code

<br>
<br>
<br>

# Setup

1. Create a virtual python environment using the following command.

   ```
   python -m venv venv
   ```

2. Activate the python environment. The command will differ for different OS and shells.

   ```
   source venv/Scripts/activate
   ```

3. Install the required packages using the following command.

   ```
   pip install -r ./requirements.txt
   ```

<br>
<br>
<br>

# AT Errors

```
+CMS ERROR: SMS size more than expected
```
