from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import random

# MQTT config (clientID must be unique within the AWS account)
clientID = "Wearable1"
endpoint = "a14181np570969-ats.iot.us-east-1.amazonaws.com" #Use the endpoint from the settings page in the IoT console
port = 8883
topic = "wearable/temperature"

# Init MQTT client
mqttc = AWSIoTMQTTClient(clientID)
mqttc.configureEndpoint(endpoint,port)
mqttc.configureCredentials("certificates/AmazonRootCA1.pem","certificates/wearable-private.pem.key","certificates/wearable-certificate.pem.crt")

# Send message to the iot topic
def send_data(message):
    mqttc.publish(topic, json.dumps(message), 0)
    print("message: ",message)
    print("Message Published")

# Loop until terminated
def loop():
     
     while(True):
          try:
               
               temperature = random.randint(37,41)
               bpm = random.randint(70,100)
               print("Temp: {}    BPM: {} ".format(temperature, bpm)) 
               
               message = {
                         'temperature': temperature,
                         'bpm': bpm
                         }
                    
               # Send data to topic
               send_data(message)

               time.sleep(5)
          except RuntimeError as error:     # Errors happen fairly often, DHT's are hard to read, just keep going
               print(error.args[0])

# Main
if __name__ == '__main__':
    print("Starting program...")
    try:
        # Connect
        mqttc.connect()
        print("Connect OK!")

        # Main loop called
        loop()
    except KeyboardInterrupt:
        mqttc.disconnect()
        exit()
