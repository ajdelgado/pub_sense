#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script is licensed under GNU GPL version 2.0 or above
# (c) 2021 Antonio J. Delgado
# 

import sys
import os
import logging
import time
import json
import random
import click
import click_config_file
from logging.handlers import SysLogHandler
from sense_hat import SenseHat
from paho.mqtt import client as mqtt_client

class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class pub_sense:

    def __init__(self, debug_level, log_file, broker, port, topic, user, password, node_exporter_file_folder):
        ''' Initial function called when object is created '''
        self.debug_level = debug_level
        if log_file is None:
            log_file = os.path.join(os.environ.get('HOME', os.environ.get('USERPROFILE', os.getcwd())), 'log', 'pub_sense.log')
        self.log_file = log_file
        self._init_log()
        self.broker = broker
        self.port = port
        self.topic = topic
        self.user = user
        self.password = password
        self.node_exporter_file_folder = node_exporter_file_folder
        self._init_mqtt()
        self.data = dict()
        self._init_sense()

    def _init_mqtt(self):
        client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.mqttclient = mqtt_client.Client(client_id)
        self.mqttclient.username_pw_set(self.user, self.password)
        self.mqttclient.on_connect = self.on_connect
        self.mqttclient.connect(self.broker, self.port)

    def _init_sense(self):
        self.sense = SenseHat()
        self.sense.set_rotation(180)
        self.sense.low_light = True
        self._slow_message('On')
        self.get_data()

    def get_data(self):
        self.data['humidity'] = self.sense.get_humidity()
        self.data['temperature'] = self.sense.get_temperature()
        self.data['temperature_from_pressure'] = self.sense.get_temperature_from_pressure()
        self.data['pressure'] = self.sense.get_pressure()
        self.data['orientation'] = self.sense.get_orientation_degrees()
        self.data['compass'] = self.sense.get_compass()
        self.data['gyroscope'] = self.sense.get_gyroscope()
        self.data['accelerometer'] = self.sense.get_accelerometer()
        self._log.debug(f"Data from sense-hat: {json.dumps(self.data, indent=2)}")
        self.publish_data()
        self.save_node_exporter()

    def publish_data(self):
        # for key in self.data.keys():
        #     message = f"{{key}}={self.data[key]}"
        message = json.dumps(self.data)
        result = self.mqttclient.publish(self.topic, message)
        if result[0] != 0:
            self._log.error(f"Error {result[0]} publishing message '{message}'. {result}")
        else:
            self._log.debug(f"Result of publishing message '{message}': {result}")

    def _slow_message(self, message):
        for letter in message:
            self.sense.show_letter(letter)
            time.sleep(0.5)
            self.sense.clear()
            time.sleep(0.1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._log.debug("Connected to MQTT Broker!")
        else:
            self._log.error("Failed to connect, return code %d\n", rc)

    def _init_log(self):
        ''' Initialize log object '''
        self._log = logging.getLogger("pub_sense")
        self._log.setLevel(logging.DEBUG)

        sysloghandler = SysLogHandler()
        sysloghandler.setLevel(logging.DEBUG)
        self._log.addHandler(sysloghandler)

        streamhandler = logging.StreamHandler(sys.stdout)
        streamhandler.setLevel(logging.getLevelName(self.debug_level))
        #formatter = '%(asctime)s | %(levelname)8s | %(message)s'
        formatter = '[%(levelname)s] %(message)s'
        streamhandler.setFormatter(CustomFormatter(formatter))
        self._log.addHandler(streamhandler)

        if not os.path.exists(os.path.dirname(self.log_file)):
            os.mkdir(os.path.dirname(self.log_file))

        filehandler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=102400000)
        # create formatter
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.DEBUG)
        self._log.addHandler(filehandler)
        return True

    def dict2node_exporter(self, dictionary):
        if not isinstance(dictionary, dict):
            return False
        result = ""
        for key in dictionary.keys():
            result += f"# HELP {key}\n"
            result += f"# TYPE {key}\n"
            result += f"{key} {dictionary[key]}"
        return result

    def save_node_exporter(self):
        with open(os.path.join(self.node_exporter_file_folder, "sense_hat.prom"), 'w')  as node_exporter_file:
            node_exporter_file.write(self.dict2node_exporter(self.data))

@click.command()
@click.option("--debug-level", "-d", default="INFO",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        case_sensitive=False,
    ), help='Set the debug level for the standard output.')
@click.option('--log-file', '-l', help="File to store all debug messages.")
#@click.option("--dummy","-n", is_flag=True, help="Don't do anything, just show what would be done.") # Don't forget to add dummy to parameters of main function
@click.option('--broker', '-b', required=True, help="MQTT broker.")
@click.option('--port', '-p', default=1883, help="MQTT broker port.")
@click.option('--topic', '-t', default='sense-hat', help="MQTT topic.")
@click.option('--user', '-u', required=True, help="MQTT username.")
@click.option('--password', '-w', required=True, help="MQTT password.")
@click.option('--node-exporter-file-folder', '-f', default='/var/lib/prometheus/node-exporter/', required=False, help="MQTT password.")
@click_config_file.configuration_option()
def __main__(debug_level, log_file, broker, port, topic, user, password, node_exporter_file_folder):
    object = pub_sense(debug_level, log_file, broker, port, topic, user, password, node_exporter_file_folder)

if __name__ == "__main__":
    __main__()

