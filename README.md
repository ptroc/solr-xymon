# solr-xymon

Plugin for Xymon for Solr monitoring.

## Overview

This project provides a plugin for monitoring Solr instances using Xymon. It checks the status of Solr cores and reports their health based on the number of documents and the last modified date.

## Features

- Monitors multiple Solr cores.
- Reports status to Xymon with color-coded messages (green, yellow, red).
- Configurable thresholds for document count and last modified time.

## Requirements

- Python 3.x
- `requests` and `Xymon` library python packages
- Xymon client

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd solr-xymon
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Place the `solr.py` script in the appropriate directory:
    ```sh
    sudo cp solr.py /usr/lib/xymon/client/ext/
    ```

4. Ensure the script is executable:
    ```sh
    sudo chmod +x /usr/lib/xymon/client/ext/solr.py
    ```

5. Copy the `10-solr.cfg` file to the appropriate directory:
    ```sh
    sudo cp 10-solr.cfg /usr/lib/xymon/client/etc/clientlaunch.d/
    ```

## Configuration

Edit the `solr.py` script to configure the following parameters:

- `service`: The name of the service (e.g., "solr").
- `yellow_time`: The threshold in minutes for yellow status based on the last modified time.
- `red_time`: The threshold in minutes for red status based on the last modified time.
- `yellow_count`: The threshold for yellow status based on the number of documents.
- `red_count`: The threshold for red status based on the number of documents.
- `core_list`: A list of Solr cores to monitor.
- `solr_admin_url`: The URL for the Solr admin API.


## Restart Xymon client
```sh
sudo systemctl restart xymon-client
``` 
