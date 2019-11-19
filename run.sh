#!/bin/bash

for job in jobs/fetch*.json ; do
    echo "Found job ${job}"
    fetch_data.py --url https://spclgitlab.ethz.ch --token "${GITLAB_API_PRIVATE_TOKEN}" --config "${job}"
done

for job in jobs/paper/plot*.json ; do
    echo "Found job ${job}"
    plot_file.py --config "${job}"
done

for job in jobs/rest/plot*.json ; do
    echo "Found job ${job}"
    plot_file.py --config "${job}"
done