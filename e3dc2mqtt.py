#!/usr/bin/python3
from modbus.client import *
import ctypes
import ssl
import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv

def getInt32(data1, data2):
  return ctypes.c_long(data1 + (data2 << 16)).value

def main():
  load_dotenv()
  MQTT_USER = os.getenv('E3DC2MQTT_MQTT_USER')
  MQTT_PW = os.getenv('E3DC2MQTT_MQTT_PW')
  MQTT_CLIENT_ID = os.getenv('E3DC2MQTT_MQTT_CLIENT_ID', default='e3dc2mqtt')
  MQTT_BROKER = os.getenv('E3DC2MQTT_MQTT_BROKER', default='localhost')
  MQTT_PORT = os.getenv('E3DC2MQTT_MQTT_PORT', default=8883)
  MQTT_CA_CERT = os.getenv('E3DC2MQTT_MQTT_CA_CERT', default='/etc/ssl/certs/ca-certificates.crt')
  MQTT_TOPIC = os.getenv('E3DC2MQTT_MQTT_TOPIC', default='energy/yourHome')
  MODBUS_HOST = os.getenv('E3DC2MQTT_MODBUS_HOST', default='localhost')
  INFLUX_MEASUREMENT_TAG = os.getenv('E3DC2MQTT_INFLUX_MEASUREMENT_TAG', default='energy,Location=yourHome')

  mqttClient = mqtt.Client(client_id=MQTT_CLIENT_ID, transport="tcp")
  mqttClient.tls_set(ca_certs=MQTT_CA_CERT, tls_version=ssl.PROTOCOL_TLS)
  mqttClient.username_pw_set(MQTT_USER, password=MQTT_PW)
  mqttClient.connect(MQTT_BROKER, MQTT_PORT, 60)
  mqttClient.loop_start()

  c = client(host=MODBUS_HOST)

  while True:
    data = c.read(FC=3, ADR=40067, LEN=16)

    pv_power = getInt32(data[0], data[1])
    battery_power = getInt32(data[2], data[3])
    home_usage = getInt32(data[4], data[5])
    grid_power = getInt32(data[6], data[7])
    autarcy = data[14] >> 8
    ownusage = data[14] & 0xff
    battery_soc = data[15]

    if grid_power >= 0:
      grid_usage_power = grid_power
      grid_feed_power = 0
    else:
      grid_usage_power = 0
      grid_feed_power = grid_power * -1

    if battery_power >= 0:
      battery_usage_power = 0
      battery_feed_power = battery_power
    else:
      battery_usage_power = battery_power * -1
      battery_feed_power = 0

    influxInline = f"{INFLUX_MEASUREMENT_TAG} "
    influxInline += f"pv_power={pv_power}"
    influxInline += f",home_usage={home_usage}"
    influxInline += f",grid_power={grid_power}"
    influxInline += f",battery_power={battery_power}"
    influxInline += f",grid_feed_power={grid_feed_power}"
    influxInline += f",grid_usage_power={grid_usage_power}"
    influxInline += f",battery_feed_power={battery_feed_power}"
    influxInline += f",battery_usage_power={battery_usage_power}"
    influxInline += f",battery_soc={battery_soc}"
    influxInline += f",autarcy={autarcy}i"
    influxInline += f",ownusage={ownusage}i"

    mqttClient.publish(MQTT_TOPIC, influxInline)
    time.sleep(10)

  mqttClient.disconnect

if __name__ == '__main__':
  main()
