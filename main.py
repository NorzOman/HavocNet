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
    port = request.form.get('port')  # Port is optional

    # Check if port is provided and convert it to integer if present
    if port:
        port = int(port)

    return redirect(url_for('attack'))

@app.route('/attack', methods=['GET'])
def attack():
    if attack_type in ['syn', 'http']:
        if port:
            command = f"python3 core.py --ip {target_ip} --port {port} --threads 5 --attack {attack_type}"
        else:
            command = f"python3 core.py --ip {target_ip} --threads 5 --attack {attack_type}"
    else:
        command = f"python3 core.py --ip {target_ip} --threads 5 --attack {attack_type}"

    return render_template('attack.html', command=command)


if __name__ == '__main__':  # Corrected the typo here
    app.run(debug=True)
