from flask import Flask, render_template, jsonify, send_from_directory, url_for
import subprocess
import threading
import webbrowser
from plots import clear_images

# I need to organize this stuff to be used like modules and script ASAP
#   - something about where the graphs are coming from when app.py is ran. 

# This needs to be placed OUTSIDE the function, since that function represents the 'begin simulation' button
clear_images('static/fes.png', overwrite=True)

app = Flask(__name__, template_folder='docs')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

@app.route('/run-script', methods=['GET'])
def run_script():
    try: #by default, this is using my local interpreter: /opt/homebrew/bin/python3
        # since I don't have the budget for cloud computing costs, I may need to offer a way to
        # select or use a different python environment if I want OTHER people to use this.
        # The option to select an interpreter/install dependecies should be here. 
        result = subprocess.check_output(['python', 'walker.py'], text=True)

        image_url = url_for('static', filename='fes.png') # EXAMPLE 

        grid_items = result.splitlines()
        return jsonify({'output': grid_items, 'image_url': image_url}) # modify this dict to return ALL images of interest
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    threading.Timer(1, open_browser).start() #automatically open browser
    app.run(debug=True, use_reloader=False)