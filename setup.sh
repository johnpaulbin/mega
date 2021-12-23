#!/bin/bash

mkdir NudeNet

wget "https://github.com/johnpaulbin/mega/releases/download/v1/classifier_lite.onnx" -O NudeNet/classifier_lite.onnx

mv NudeNet .NudeNet

echo setup complete