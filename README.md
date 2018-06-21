# gdisk-analyzer

Tool for analysing your Google Drive.<br> It collects files metadata and shows you, what takes the most space.<br>
Uses Google Drive REST API.

Current implementation is a Flask server with a website.

### Features:
* Different handlers to make work with a Google Drive easier.
* Received information stored in database.
* If there were no changes in the user's Drive - tool uses saved data.
* File analysis shows disk structure and heavy/old files and folders.

## Getting started:
Here is a good instruction how to set up all the prerequisites: [Google Drive API Quickstart](https://developers.google.com/drive/api/v3/quickstart/python).

### Prerequisites

You need to have Python 3 and the Google Client Library installed:
``` bash
pip install --upgrade google-api-python-client
```
Then install libraries from the requirements.txt:
``` bash
pip install -r requirements.txt
```

The tool uses Google API credentials, so if you don't have one - you must make it here (create a project): [Google Developer Console](https://console.developers.google.com/flows/enableapi?apiid=drive). <br>

Since you have credentials, download it as json and put in your directory.<br>
Then change the "credentials" string in *app.py*.

### Running
Now you can run the server by executing the *app.py* file as:
``` bash
python app.py
```
Then all you need is to open http://127.0.0.1:5000/ in your browser.

## Feedback
All your thoughts you can send here: baraltiva@gmail.com
