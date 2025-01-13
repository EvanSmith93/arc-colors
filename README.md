# Arc Colors
Sync your smart light bulb with the color of your current space in Arc Browser using Python.

This is designed to work on Mac only, however something similar may be available on Windows. It is currently set up to talk to a Govee smart light bulb, but this can be changed to any smart light bulb with a public API.

## Setup
Create a .env file similar to the `.env-example` file. Include the name of your home directory, and an API key, MAC address, and device type for a Govee smart light. If using some other brand of light, you'll need to update the `BulbController` to make a request to that specific light.

Within a terminal navigate to the arc-colors folder and ensure you have python installed. Then run the following commands.
```
pip install -r requirements.txt
python arc_colors.py
```
You should now get a message that it's watching an Arc application file for updates. Note: it can sometimes take several seconds for the program to register that you've changed spaces.