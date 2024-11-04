from flask import Flask, render_template, jsonify, request, url_for
import subprocess
import threading
import webbrowser
import src.config as config
import json

app = Flask(__name__, template_folder='docs')


# This needs to be placed OUTSIDE run_script(), since that function represents the 'begin simulation' button
# clear_images('static/fes.png', overwrite=True)
# clear_images('static/MD_simulation.gif')

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
            f.write(f"metad = {metad}\n") # overriding this flag for now 
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
    # ON/OFF bool needs to be translated
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
    return '', 204 # do

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
        
        # HERE, the response is expecting all this value in a dictionary...
        # but it is NOT ACTUALLY BEING PASSED IN run_walker.py; I am simply calling the function to overwrite the previous images. 
        
        response = {
            'ns_day': output_data.get('ns/day', 0),
            'sim_time': output_data.get('sim_time', 0),
            # 'output': list(output_data.keys()), #in case there is anything else I want to access

            # links to files created by run_walker.py; where all the graphing functions are called.
            'rads_time_url': '/static/images/rads_time.png',
            'fes_url': '/static/images/reweight_fes.png'
        }

        return jsonify(response)

    except subprocess.CalledProcessError as e:
            # Capture stderr for specific error details and print to Flask site
            error_msg = e.stderr or "Unknown error occurred in run_walker.py"
            print(f"Error in run_walker.py: {error_msg}")  # Logs to server console for debugging
            return jsonify({'error': f'Simulation failed: {error_msg}'})


if __name__ == '__main__':
    threading.Timer(2, open_browser).start() #automatically open browser
    app.run(debug=True, use_reloader=False, threaded=True)