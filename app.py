from flask import Flask, render_template, jsonify, request, redirect, url_for
import subprocess
import threading
import webbrowser
import time
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
    try: #by default, this is using my local interpreter: /opt/homebrew/bin/python3
        # since I don't have the budget for cloud computing costs, I may need to offer a way to
        # select or use a different python environment if I want OTHER people to use this.
        # The option to select an interpreter/install dependecies should be here. 
        # result = subprocess.check_output(['python', 'src/walker.py'], text=True)
        from src.walker import walker, integrator_performance
        t0 = time.time()
        bias, q, V, E = walker()
        print(bias)
        tplus = time.time()
        integrator_performance(t0, tplus)

        bias_list = bias.tolist()
        q_list = q.tolist()
        V_list = V.tolist()
        E_list = E.tolist()

        image_url = url_for('static', filename='fes.png') # EXAMPLE 

        return jsonify({'bias': bias_list, 
        'q': q_list,
        'V': V_list,
        'E': E_list,
        'image_url': image_url}) # modify this dict to return ALL images of interest
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    threading.Timer(2, open_browser).start() #automatically open browser
    app.run(debug=True, use_reloader=False)