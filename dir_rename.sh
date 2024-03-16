#!/bin/bash

# Iterate through all directories matching the pattern
for dir in Session\ *; do
    # Extract the session number and topic from the directory name
    session_number=$(echo "$dir" | sed -n 's/Session #\([0-9]*\) (.*)/\1/p')
    topic=$(echo "$dir" | sed -n 's/Session #[0-9]* (\(.*\))/\1/p')

    # Replace spaces with underscores in the topic
    topic=$(echo "$topic" | sed 's/ /_/g')

    # Replace commas with underscores in the topic
    topic=$(echo "$topic" | sed 's/,/_/g')

    # New directory name format
    new_dir="session_${session_number}_${topic}"

    # Rename the directory
    mv "$dir" "$new_dir"
done
