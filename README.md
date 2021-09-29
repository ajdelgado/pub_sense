# pub_sense

## Requirements

- Python 3
- [Raspberry Pi](https://www.raspberrypi.org/) with [Raspbian](https://www.raspbian.org/RaspbianImages) installed
- [Raspberry Sense Hat](https://www.raspberrypi.org/products/sense-hat/)
- A [Prometheus](https://prometheus.io/docs/introduction/overview/) server

## Installation

### Linux

  1. Install the package/module
  
  ```bash
sudo apt install python3-sense-hat libopenjp2-7 python3-paho-mqtt prometheus-node-exporter
sudo python3 setup.py install
  ```

  1. Configure Prometheus Node Exporter to collect text files in the file /etc/default/prometheus-node-exporter be sure *ARGS* contains *--collector.textfile.directory='/var/lib/prometheus/node-exporter'*
  
  1. Create a file called /etc/systemd/system/pub_sense.timer with content:

```ini
[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Unit=pub_sense.service
```

  1. Create a file called /etc/pub_sense.conf based on [this one](https://github.com/ajdelgado/pub_sense/blob/master/pub_sense.conf.sample).

  1. Create a file called /etc/systemd/system/pub_sense.service with content:

```ini
[Service]
Type=simple
ExecStart=python3 /var/lib/from_repos/pub_sense/pub_sense/pub_sense.py --config /etc/pub_sense.conf
```

  1. Reload systemd daemon:

  ```bash
  sudo systemctl daemon-reload
  ```
  
  1. Enable pub_sense service
  
  ```bash
  sudo systemctl enable pub_sense.service
  ```
  
  1. Start pub_sense timer
  
  ```bash
  sudo systemctl start pub_sense.timer
  ```

## Usage

The service will run scheduled every minute (or what you put in OnUnitActiveSec), but if you want to run it manually:
  ```bash
  pub_sense.py [--debug-level|-d CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET] --config <configuration_file>
  ```
