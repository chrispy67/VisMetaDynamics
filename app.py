from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__, template_folder='docs')

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run-script', methods=['GET'])
def run_script():
    try: #by default, this is using my local interpreter: /opt/homebrew/bin/python3
        # since I don't have the budget for cloud computing costs, I may need to offer a way to
        # select or use a different python environment if I want OTHER people to use this.
        # 
        # Also, for some reason this isn't observed in the live github/repo.io URL? Pressing the button has no effect 
        result = subprocess.run(['python', 'walker.py'], capture_output=True, text=True)
        return jsonify({'output': result.stdout, "error": result.stderr})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)