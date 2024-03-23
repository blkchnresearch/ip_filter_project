import os
from flask import Flask, jsonify, request
import sqlite3
import requests
import re
from socket import gethostbyname, gethostname

app = Flask(__name__)
# Let's set up the database in case it does not exist
path_to_db = 'excluded_ips.db'
# If path does not exist, set up a connection to the path, create ip table and token table
if not os.path.exists(path_to_db):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    # Exclude IP table. Syntax here: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html.
    # create table excluded_ips (id INTEGER PRIMARY KEY, ip, TEXT UNIQUE) -> Seems the key phrases need to be in capital
    cursor.execute('''CREATE TABLE excluded_ips (id INTEGER PRIMARY KEY,ip TEXT UNIQUE)''')

    # As an experiment, just add local IP to the allow-list.
    localip = gethostbyname(gethostname())
    cursor.execute('INSERT INTO excluded_ips (ip) VALUES (?)', (localip,))
    connection.commit()

    connection.close()
    # Ok we are done with the initial part.

# Function to interact with the database: fetch non-Tor IPs
def get_non_tor_ips():
    # This is easy. Just make a connection, and get the data.
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute('SELECT ip FROM excluded_ips')
    rows = cursor.fetchall()
    connection.close()
    return {row[0] for row in rows}

# Function to interact with the database: add IP to non-Tor list
def add_to_non_tor_ips(ips):
    # Again. Simple thing. Just make a connection, and insert the ip.
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    for ip in ips:
        cursor.execute('INSERT OR IGNORE INTO excluded_ips (ip) VALUES (?)', (ip,))
    connection.commit()
    connection.close()

# Function to interact with the database: verify token
# Commenting it out. Something to test in the future. 
"""
def verify_token(token):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    row = cursor.fetchone()
    connection.close()
    return row is not None
"""


# Endpoint to fetch Tor IPs
@app.route('/tor', methods=['GET'])
def tor():
    # List of external URLs to fetch IP data
    urls = [
        "https://www.dan.me.uk/torlist/?exit",
        "https://udger.com/resources/ip-list/tor_exit_node"
    ]

    # Set to store all IPs from external sources
    allips = set()
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            # collect ips using Regex. Regex obtained from here:  https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s16.html
            ip_addrs = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', response.text)
            allips.update(ip_addrs)

    # This is the fun part. Remove IPs collected from the second endpoint.
    non_tor_ips = get_non_tor_ips()
    filtered_ips = allips - non_tor_ips
    return jsonify(list(filtered_ips)), 200  

# Endpoint to add IPs to non-Tor list
@app.route('/non-tor', methods=['POST'])
def non_tor():
    data = request.get_json()
    ips = data.get('ips')
    ip = data.get('ip')

    if ips:
        if isinstance(ips, list):
            add_to_non_tor_ips(ips)
            return jsonify({'message': 'IPs added to non-Tor list'}), 200
        elif isinstance(ips, str):
            add_to_non_tor_ips([ips])
            return jsonify({'message': 'IP added to non-Tor list'}), 200
    elif ip:
        add_to_non_tor_ips([ip])
        return jsonify({'message': 'IP added to non-Tor list'}), 200

    return jsonify({'error': 'Invalid IP addresses provided'}), 400

#Error Handling: 
#Sources :https://flask.palletsprojects.com/en/3.0.x/errorhandling/
#Source: https://www.geeksforgeeks.org/use-jsonify-instead-of-json-dumps-in-flask/
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized Access'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    context = ('server.crt', 'server.key')  # Need to add these certificates for access Auth.
    # commenting it out since Docker keeps throwing error. Going without SSL
    # app.run(debug=True, ssl_context=context, port=6000)
    app.run(debug=True, host="0.0.0.0", port=6000, ssl_context=context)
