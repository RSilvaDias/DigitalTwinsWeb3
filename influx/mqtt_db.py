import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# MQTT Configuration
MQTT_BROKER = '200.137.197.215'
MQTT_PORT = 31507
MQTT_TOPIC = 'digitaltwin/data'

# InfluxDB Configuration
INFLUXDB_URL = '200.137.197.215:31505'
INFLUXDB_BUCKET = 'digitaltwin'
INFLUXDB_TOKEN = 'WPhWR-JdcWrXVhzqngZMxXTkzfImrv1jECDvHXQyLQHodzNd_2vrJvt7NvXUc2TFuvoUnz1ujUjNpASfFi7zog=='
INFLUXDB_ORG = 'ufg'

# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

# InfluxDB Client Setup
client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

# MQTT Message Handler
def on_message(client, userdata, message):
    # Extract the topic and payload from the MQTT message
    topic = message.topic
    payload = message.payload.decode('utf-8')

    # Write the data to InfluxDB
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=INFLUXDB_BUCKET, record=[{
        'measurement': 'your_measurement',
        'fields': {
            'value': payload
        }
    }])
    print("Succesfully sent to db with message:"+payload)

# Subscribe to the MQTT topic
mqtt_client.subscribe(MQTT_TOPIC)

# Start the MQTT message handler
mqtt_client.on_message = on_message

# Run the MQTT client
mqtt_client.loop_forever()