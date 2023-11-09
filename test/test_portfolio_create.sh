#!/bin/bash

# Read the JSON file and get the length of the "data" array
length=$(jq '.data | length' testJSON/portfolio_create.json)

# Accept an ID as a command line argument
input_id=$1

# Check if an ID is provided
if [ -z "$input_id" ]; then
  # Loop through each object in the "data" array
  for (( i=0; i<$length; i++ ))
  do
    # Extract each "details" object based on the index
    details=$(jq -c ".data[$i].details" testJSON/portfolio_create.json)

    # Make the curl request
    curl -X POST -H "Content-Type: application/json" -d "$details" http://localhost:5000/portfolio_create
  done
else
  # Loop through each object in the "data" array to find the one with the matching ID
  for (( i=0; i<$length; i++ ))
  do
    id=$(jq -r ".data[$i].id" testJSON/portfolio_create.json)
    if [ "$id" -eq "$input_id" ]; then
      # Extract the "details" object based on the index
      details=$(jq -c ".data[$i].details" testJSON/portfolio_create.json)
      
      # Make the curl request
      curl -X POST -H "Content-Type: application/json" -d "$details" http://localhost:5000/portfolio_create
      break
    fi
  done
fi