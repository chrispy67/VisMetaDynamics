from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__, template_folder='docs')
print(app)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        result = subprocess.run(['python3', 'walker.py'], capture_output=True)
        return jsonify({'output': result.stdout, "error": result.stderr})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)