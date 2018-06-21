# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, Markup
import sys
sys.path.append("..")
from start import analyze
# create the application object
app = Flask(__name__)

credentials = '../secret/client_secret.json'


# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('main.html')  # return a string

@app.route('/analytics')
def analytics():
    info, user_id, success = analyze(credentials)
    if not success:
        sys.exit(0)
    args = {"info_{0}".format(k) : Markup(v.replace('\n', "<br />")) for (k, v) in enumerate(info)}
    ans = render_template('analytics.html', **args, user_id=user_id)
    return ans  # return a string

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')  # render a template


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=False)
