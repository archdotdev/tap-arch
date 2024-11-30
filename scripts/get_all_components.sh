#!/bin/bash

# Get all schema names from the components.schemas object
schema_names=$(jq -r '.components.schemas | keys[]' tap_arch/schemas/raw_components/openapi.json)

# Loop through each schema name and extract it to a separate file
for schema in $schema_names; do
    # Create the output filename - convert to lowercase using tr
    output_file="tap_arch/schemas/raw_components/$(echo "$schema" | tr '[:upper:]' '[:lower:]').json"

    # Extract the schema to a separate file
    jq ".components.schemas[\"$schema\"]" tap_arch/schemas/raw_components/openapi.json > "$output_file"

    echo "Created $output_file"
done
