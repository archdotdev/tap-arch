#!/bin/bash

# Create the directory path if it doesn't exist
mkdir -p tap_arch/schemas/raw_components

# Download the file using curl
curl -o tap_arch/schemas/raw_components/openapi.json https://api.arch.dev/openapi.json
