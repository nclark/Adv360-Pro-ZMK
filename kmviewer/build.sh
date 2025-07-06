#!/bin/bash

# Build script for kmviewer terminal image viewer

set -e

echo "Building kmviewer..."
go build -o kmviewer

echo "Build complete! Run with: ./kmviewer <image1> <image2> ..."