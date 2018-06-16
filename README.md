# gdisk-analyzer

Tool for analysing your Google Drive.<br> It collects files metadata and shows you, what takes the most space.<br>
Uses Google Drive REST API.

## Getting started:
Here is a good instruction how to set up all the prerequisites: [Google Drive API Quickstart](https://developers.google.com/drive/api/v3/quickstart/python).

### Prerequisites

You need to have Python 3 and the Google Client Library installed:
``` bash
pip install --upgrade google-api-python-client
```

The tool uses Google API credentials, so if you don't have one - you must make it here (create a project): [Google Developer Console](https://console.developers.google.com/flows/enableapi?apiid=drive). <br>

Since you have credentials, download it as json and put in your directory.<br>
Then change the "credentials" string in *start.py*.

### Running
Now you can run the tool by executing the *start.py* file as:
``` bash
python start.py
```
It will run your browser, where you need to allow access to the application.

## Feedback
All your thoughts you can send here: baraltiva@gmail.com
