# pub_sense

## Requirements

- Python 3
- [Raspberry Pi](https://www.raspberrypi.org/) with [Raspbian](https://www.raspbian.org/RaspbianImages) installed
- [Raspberry Sense Hat](https://www.raspberrypi.org/products/sense-hat/)
- A [Prometheus](https://prometheus.io/docs/introduction/overview/) server

## Installation

### Linux

- Install the package/module

  ```bash
  sudo apt install python3-sense-hat libopenjp2-7 python3-paho-mqtt prometheus-node-exporter
  sudo python3 setup.py install
  ```

- Configure Prometheus Node Exporter to collect text files in the file /etc/default/prometheus-node-exporter be sure *ARGS* contains *--collector.textfile.directory='/var/lib/prometheus/node-exporter'*

- Configure your Prometheus server to have as target your raspberry node exporter. If *192.168.1.3* is the IP of your raspberry, this should be in your *prometheus.yml* file:

  ```yaml
  - job_name: 'servers-job'
  static_configs:
    - targets: ['192.168.1.3:9100']
  ```

- Create a file called /etc/systemd/system/pub_sense.timer with content:

  ```ini
  [Timer]
  OnBootSec=1min
  OnUnitActiveSec=1min
  Unit=pub_sense.service
  ```

- Create a file called /etc/pub_sense.conf based on [this one](https://github.com/ajdelgado/pub_sense/blob/master/pub_sense.conf.sample).

- Create a file called /etc/systemd/system/pub_sense.service with content:

  ```ini
  [Service]
  Type=simple
  ExecStart=python3 /var/lib/from_repos/pub_sense/pub_sense/pub_sense.py --config /etc/pub_sense.conf
  ```

- Reload systemd daemon:

    ```bash
    sudo systemctl daemon-reload
    ```

- Enable pub_sense service

    ```bash
    sudo systemctl enable pub_sense.service
    ```

- Start pub_sense timer

    ```bash
    sudo systemctl start pub_sense.timer
    ```

## Usage

The service will run scheduled every minute (or what you put in OnUnitActiveSec), but if you want to run it manually:

```bash
pub_sense.py [--help] [--broker <mqtt_broker>] [--port <mqtt_port>] [--topic <topic>] [--user <mqtt_user>] [--password <mqtt_password>] [--node-exporter-file-folder <node_exporter_file_collector_folder>] [--log-file <log_file>] [--debug-level|-d CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET] [--config <configuration_file>]
  ```

## Logs

If log-file is not specified, $HOME/log/pub_sense.log will be used. But it was also published in syslog.

## Security

Avoid using the *--password* parameter in the command line, and use a configuration file well protected, with as few permissions as possible. Command lines (including the password) run by a user can be seen by other users of the system.
