#!/bin/bash

for job in jobs/fetch*.json ; do
    echo "Found job ${job}"
    fetch_data.py --url https://spclgitlab.ethz.ch --token "${GITLAB_API_PRIVATE_TOKEN}" --config "${job}"
done

for job in jobs/plot*.json ; do
    echo "Found job ${job}"
    plot_file.py --config "${job}"
done