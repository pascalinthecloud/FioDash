#!/bin/bash

# Base URL of the Flask server
BASE_URL="http://127.0.0.1"

# Function to nuke the database
nuke_database() {
    echo "Nuking the database..."
    curl -X POST "$BASE_URL/nuke" -H "Content-Type: application/json"
}

# Function to generate a random float between min and max
generate_random_float() {
    local min=$1
    local max=$2
    echo "$(awk -v min=$min -v max=$max 'BEGIN{srand(); print min + (rand() * (max - min))}')"
}

# Function to generate a random integer between min and max
generate_random_int() {
    local min=$1
    local max=$2
    echo $((RANDOM % (max - min + 1) + min))
}

# Function to generate a random hostname
generate_random_hostname() {
    local prefix="host"
    local suffix=$(generate_random_int 1 100)  # Random number between 1 and 100
    echo "${prefix}${suffix}"
}

# Function to post a test entry
post_entry() {
    local hostname=$1
    local read_iops=$(generate_random_float 10000 100000)
    local write_iops=$(generate_random_float 10000 100000)
    echo "Posting entry: hostname=$hostname, read_iops=$read_iops, write_iops=$write_iops"
    curl -X POST "$BASE_URL/update" -H "Content-Type: application/json" -d "{\"hostname\": \"$hostname\", \"read_iops\": $read_iops, \"write_iops\": $write_iops}"
}

# Nuke the database to start fresh
# nuke_database

# Post multiple entries with different hostnames and randomized IOPS values
for i in $(seq 1 10); do
    hostname=$(generate_random_hostname)
    num_entries=$(generate_random_int 1 5)  # Random number of entries (1 to 5) for each hostname
    for ((j=0; j<num_entries; j++)); do
        post_entry "$hostname"
        # sleep $(generate_random_int 1 2)  # Random delay between posts (1 to 2 seconds)
    done
done

echo "All test data has been posted."
