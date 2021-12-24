#!/bin/bash

mkdir ~/.NudeNet/

wget "https://github.com/johnpaulbin/mega/releases/download/1.0/classifier_lite.onnx" -O ~/.NudeNet/classifier_lite.onnx

wget "https://github.com/johnpaulbin/mega/releases/download/1.0/trust.json" -O trust.json

echo installing requirements...

pip3 install -q -r requirements.txt
pip3 uninstall dataclasses -y

echo setup complete