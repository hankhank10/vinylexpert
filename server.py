from flask import Flask, render_template, redirect, jsonify, request
import sys
import os.path
import requests

import backend_key
import backend_music

app = Flask(__name__)

## Empty variables

previous_artwork_url = ""

## Page servers

@app.route('/')
@app.route('/index')
def index():
    if backend_key.get_key() == "":
        return redirect ("setup")

    return render_template ("index.html", page_title="Vinyl Listener")

@app.route('/setup')
def setup():
    current_key = backend_key.get_key()

    if current_key == "":
        return render_template ('setup.html', page_title="First time setup", placeholder="insert new API key here", field_text="")

    if current_key != "":
        return render_template ('setup.html', page_title="Change API key",placeholder="", field_text=current_key)


# API setup
@app.route('/api/status')
def api_status():
    api_key = backend_key.get_key()

    if api_key == "":
        return redirect ("setup")
    else:
        return ("API key set to: " + api_key)

@app.route('/new_api_key', methods=['POST'])
def new_api_key():
    new_api_key = request.form['new_key']
    
    result = backend_key.set_key(new_api_key)
    return redirect ("index")

@app.route('/lookup_failed')
def lookup_failed():
    return render_template ("index.html", page_title="nothing playing")

@app.route('/listen')
def listening():
    if backend_key.get_key() == "":
        return redirect ("setup")
    
    return render_template('doing_something.html', doing_what="listening...", next_step="listen_action", spinner_colour="primary")

@app.route('/listen_action')
def listen():
    backend_music.listen()
    return render_template('doing_something.html', doing_what="identifying...", next_step="identify_action", spinner_colour="success")

@app.route('/identify_action')
def identify():
    output = backend_music.identify()

    if output['status'] == "Lookup failed":
        return redirect ("lookup_failed")

    return redirect ("display")

@app.route('/listen/json')
def listen_json():
    backend_music.listen()
    output = backend_music.identify()
    
    return jsonify(output)

@app.route('/listen/silent')
def listen_silent():
    backend_music.listen()
    backend_music.identify()
    
    return redirect ("display")

@app.route ('/download_art')
def download_art():
    
    response = backend_music.download_art()
    return jsonify(response)

@app.route ('/display')
@app.route ('/display/<display_option>')
def display(display_option="default"):
    output = backend_music.parse()

    if display_option == "json":
        return jsonify(output)

    # quit out if there's a lookup error
    if output['status'] == "Lookup failed":
        return redirect ("/lookup_failed")

    if display_option == "image" or display_option == "artwork" or display_option == "art":
        return redirect (output['art_tidy'])

    return render_template('display.html', art_url=output['art_tidy'], title=output['title'], artist=output['artist'], album=output['album'])


## Main loop
if __name__ == '__main__':
    app.run(debug=True, port=6006, host='0.0.0.0')