import argparse
import base64
import json

import numpy
import socketio
import eventlet
import eventlet.wsgi
import time
from PIL import Image
from PIL import ImageOps
from flask import Flask, render_template
from io import BytesIO

from keras.models import model_from_json

sio = socketio.Server()
app = Flask(__name__)
model = None


@sio.on('telemetry')
def telemetry(sid, data):
    # Parse the Data and Emit a New Steering Command
    # predicted_angle = model.predict(None)
    # print("telemetry", sid)
    steering_angle = data["steering_angle"]
    throttle = data["throttle"]
    speed = data["speed"]
    image = Image.open(BytesIO(base64.decodestring(data["image"])))
    image_array = numpy.asarray(image)
    steering_angle = model.predict(
        numpy.uint8(image_array[None, :, :, :].transpose(0, 3, 1, 2)))
    print steering_angle
    send_control(float(steering_angle[0]), 1.0)


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    send_control(0, 0)


def send_control(steering_angle, throttle):
    # print("Sending Steering...", steering_angle, throttle)
    sio.emit("steer", data={
        'steering_angle': steering_angle.__str__(),
        'throttle': throttle.__str__()
    }, skip_sid=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument('model', type=str,
                        help='Path to model definition json. Model weights should be on the same path.')
    args = parser.parse_args()
    with open(args.model, 'r') as jfile:
        model = model_from_json(json.load(jfile))

    model.compile("sgd", "mse")
    weights_file = args.model.replace('json', 'keras')
    model.load_weights(weights_file)

    # Fetch Image from Simulator

    # Send Predicted Angle back to Simulator

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
