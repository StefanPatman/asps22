from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

@app.route('/listen', methods = ['POST'])
def listen():
    logging.info('Enter')
    data = request.get_json()
    temperature = data['temperature']
    location = data['location']
    timestamp = data['timestamp']
    id = data['id']
    print(temperature, location, id, timestamp)
    return {}

if __name__ == '__main__':
    app.run(port=5000, debug=True)
