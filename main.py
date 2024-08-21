import json
from flask import Flask, render_template, redirect, request, url_for, session

app = Flask(__name__)
app.secret_key = "reallysupersecret"

def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username  # Corrected variable name
            return redirect(url_for('dashboard'))
        else:
            error = "Incorrect Username or Password"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html',number=0)

@app.route('/start_attack', methods=['POST'])
def start_attack():
    global target_ip, attack_type, port
    target_ip = request.form.get('target_ip')
    attack_type = request.form.get('attack_type')
    port_str = request.form.get('port')

    port = int(port_str) if port_str else None

    if attack_type == 'syn' and port is None:
        return render_template('dashboard.html',error="Port must be provided for SYN flood attacks.")

    return redirect(url_for('attack'))

@app.route('/attack', methods=['GET'])
def attack():
    if attack_type == 'syn':
        if port is None:
            return "Port is required for SYN flood attacks.", 400
        command = f"python3 core.py --ip {target_ip} --port {port} --threads 10 --attack {attack_type}"
    else:
        command = f"python3 core.py --ip {target_ip} --threads 10 --attack {attack_type}"
    
    return render_template('attack.html', command=command)


if __name__ == '__main__': 
    app.run(debug=True)
