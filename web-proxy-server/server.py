# importing libraries
from flask import Flask, request, redirect, render_template, jsonify, send_file
from datetime import datetime
import http.client
import requests
import json
import matplotlib.pyplot as plt 
import numpy as np
from io import BytesIO
import base64
import math


# creating the main application
app = Flask(__name__)

DB = [] 

# # please consider this drop_down filter
# reference_point= request.args.get(REFERENCE_POINT)

data_format_send = {
  "contextElements": [
    {
      "id": "your_sensor_id",
      "attributes": [
        {
          "name": "sensorvalue",
          "value": "",
          "type": "string"
        },
        {
          "name": "timeOfData",
          "value": "",
          "type": "timestamp"
        },
      ],
      "type": "Gateway",
      "isPattern": "false"
    }
  ],
  "updateAction": "APPEND",
  "auth": {
    "username": "your_username",
    "password": "your password"
  }
}

# Server URL to send the sensor data
SSiO_URL = 'https://gw-server.research.ltu.se:9999/se.ltu.ssr.webapp/rest/proxy/updateContext'

# URL to retrieve the sensor data
RETRIEVE_URL = 'https://aaa-server.research.ltu.se/v1/queryContext'

# data fromat to retrieve
data_format_retrieve = {
  "entities": [
    {
      "id": "your_sensor_id",
      "type": "Gateway",
      "isPattern": False
    }
  ]
}

# header fromat to retrieve
headers_format_retrieve = {
  'Content-Type': 'application/json',
  'Authorization': ''
}

# token to retrieve the data
TOKEN = "Bearer your_token"

# count the requests from sensor
REQ_COUNTER = 0
max_reqs = 12
max_data_chart = 30 


# function to update the token every hour (when retrieving fails)
def update_token():
    global TOKEN
    conn = http.client.HTTPConnection("aaa-server.research.ltu.se", 3000)
    payload = 'grant_type=client_credentials&username=your_username&password=your_password'

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic your_key'}

    conn.request("POST", "/oauth2/token", payload, headers)
    res = conn.getresponse()
    data = res.read()

    token_dict = json.loads(data)
    TOKEN = "Bearer " + token_dict["access_token"]


@app.route('/', methods=["GET", "POST"])
def index():
    global DB
    global max_data_chart

    size = len(DB)

    if size > max_data_chart:
          temp = DB[-max_data_chart:]
    else:
          temp = DB

    times = [time["onlytime"] for time in temp]
    sounds = [float(sound["value"]) for sound in temp]
    
    img = BytesIO()

    fig, ax = plt.subplots()
    ax.set_ylim(0, 100)
    #ax.xaxis_date()
    fig.autofmt_xdate()
    fig.set_size_inches(10, 4, forward=True)
    ax.bar(times, sounds)
    ax.set_title('Noise Level')
    ax.set_xlabel('Time')
    ax.set_ylabel('Sound (db)')
    plt.axhline(35, color='orange', ls='dashed')
    plt.axhline(50, color='red', ls='dashed')
    plt.savefig(img, format='png')
    fig.clear(True)
    plt.close("all")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('index.html', sound=round(float(DB[-1]["value"]),1), plot_url=plot_url)


@app.route('/sensordata', methods=["POST"])
def receive_sensor_data():
    global REQ_COUNTER
    global DB
    # getting the data from sensor
    data = json.loads(request.data)
    print("Data from Sensor","*"*40)
    print(data)
    REQ_COUNTER += 1

    ready_to_send = data_format_send
    now = datetime.now()
    timestamp = str(now)
    onlytime_str = now.strftime("%H:%M:%S")
    onlytime = now
    value = str(data["value"])
    
    # Send the value to SSiO every one minute
    if REQ_COUNTER == max_reqs:
        ready_to_send["contextElements"][0]["attributes"][0]["value"] = value
        ready_to_send["contextElements"][0]["attributes"][1]["value"] = timestamp
        #sending the data to SSiO platform
        response = requests.post(SSiO_URL, json=ready_to_send, verify=False)
        print("Data from SSiO","*"*40)
        print(response)
        REQ_COUNTER = 0

    # write the value to database
    DB.append({"value":value, "timestamp":timestamp, "onlytime":onlytime_str})

    if len(DB)>50:
          DB = DB[-50:]

    # responding to the sensor
    resp = jsonify(success=True)
    return resp


@app.route('/getaudio', methods=["GET"])
def send_audio():
    audio = "alert.mp3"
    return send_file(audio)


if __name__ == "__main__":
	
	app.run(host="0.0.0.0", port=80, debug=True)