from flask import Flask, render_template, jsonify, request, url_for
import subprocess
import threading
import webbrowser
import src.config as config
import json
import os

app = Flask(__name__, template_folder='docs')


# Clunky, but I don't think I can deal with args the same way I did with cgen2gmx.
# Each time a new simulation is run, the config file is overwritten with update_config()
def update_config(steps, temp, x0, #mratio,
    metad, w, delta, hfreq):
    try:
        with open('src/config.py', 'w') as f:
            #MD parameters
            f.write(f"steps = {steps}\n")
            f.write(f"temp = {temp}\n")
            f.write(f"x0 = {x0}\n")
            # f.write(f"mratio = {mratio}\n")

            # MetaD parameters
            f.write(f"metad = {metad}\n") 
            f.write(f"w = {w}\n")
            f.write(f"delta = {delta}\n")
            f.write(f"hfreq = {hfreq}\n")
    except Exception as e:
        print(e)

@app.route('/submit_params', methods=['POST'])
def submit_params():
    # MD parameters
    temp = request.form.get('temp')
    steps = request.form.get('steps')
    x0 = request.form.get('x0')
    # mratio = request.form.get('mratio')

    metad = None
    # ON/OFF bool needs to be translated because case sensitive??
    metad_from_switch = request.form.get('metadynamics')

    if metad_from_switch == 'true':
        metad = True
    
    if metad_from_switch == 'false':
        metad = False
    # Metadynamics parameters
    w = request.form.get('w')
    delta = request.form.get('delta')
    hfreq = request.form.get('hfreq')

    #apply changes with helper function organized the same way
    update_config(steps, temp, x0, #mratio,
        metad, w, delta, hfreq)
    
    # no content on success
    return '', 204 

# Slightly different from submit_params
@app.route('/process_switch', methods=['POST'])
def process_switch():
    data = request.get_json()
    metadynamics_state = data.get('metadynamics', False)  # Get the boolean state, default is False
    
    return jsonify({'success': True, 'metadynamics': metadynamics_state})

@app.route('/')
def home():
    return render_template('index.html')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        result = subprocess.run(
            ['python', 'src/run_walker.py'],
            capture_output=True,
            text=True,
            check=True
        )

        output_data = json.loads(result.stdout)
        
        response = {
            'ns_day': output_data.get('ns/day', 0),
            'sim_time': output_data.get('sim_time', 0),

            # links to files created by run_walker.py; where all the graphing functions are called.
            # but these are NOT in output_data{}
            'rads_time_url': '/static/images/rads_time.png',
            'fes_url': '/static/images/reweight_fes.png',
            'underlying_fes_url': '/static/images/underlying_fes.png',
            'metad_gif_url': '/static/images/MD_simulation.gif'
        }

        # Restart the progress bar each time the button is pressed 
        if os.path.exists('static/.progress.json'):
            os.remove('static/.progress.json')
        return jsonify(response) 

    except subprocess.CalledProcessError as e:
        # Capture stderr for specific error details and print to Flask site
        error_msg = e.stderr or "Unknown error occurred in run_walker.py"
        print(f"Error in run_walker.py: {error_msg}")  # Logs to server console for debugging
        return jsonify({'error': f'Simulation failed: {error_msg}'})

    except json.JSONDecodeError as e:
        # Handle invalid JSON
        print(f"Invalid JSON output from run_walker.py: {e}")
        return jsonify({'error': 'Invalid JSON output from run_walker.py'})

    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {e}'})

# This is the function that will be called periodically in index.html 
@app.route('/static/.progress.json')
def get_progress():
    file_path = os.path.join(app.root_path, 'static', '.progress.json')

    if os.path.exists(file_path):
        with open (file_path) as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"value": 0})

if __name__ == '__main__':
    try:
        os.remove('static/.progress.json')
    except FileNotFoundError:
        pass


    threading.Timer(2, open_browser).start() #automatically open browser
    app.run(debug=False, use_reloader=False)

