from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import random

# MQTT config
clientID = "Watch1"
endpoint = "a11tiojfrl1fep-ats.iot.us-east-1.amazonaws.com" 
port = 8883
topic = 'immersivity/data'

#port = 443
#topic = "wearable/temperature"

# Init MQTT client
mqttc = AWSIoTMQTTClient(clientID)
mqttc.configureEndpoint(endpoint,port)
mqttc.configureCredentials("certificates/AmazonRootCA1.pem","certificates/private.pem.key","certificates/certificate.pem.crt")

# Send message to the iot topic
def send_data(message):
    mqttc.publish(topic, json.dumps(message), 0)
    print("message: ",message)
    print("Message Published")

# Loop until terminated
def loop():
     
     while(True):
          try:
               
               temperature = random.uniform(35.5,36.4)
               bpm = random.randrange(82,89,1)
               oxy = random.uniform(98.3,98.6)
               luminosity = random.randrange(95,100)
               timestamp = time.gmtime()
               unixtime = time.mktime(timestamp)
               
               print("Temp: {}    BPM: {}  ResponseTime: {} ".format(temperature, bpm, unixtime)) 
               
               message = {
                         'temperature': temperature,
                         'bpm': float(bpm),
                         'oxysaturation': oxy,
                         'luminosity' : float(luminosity)
                         }
                
               # Send data to topic
               
               send_data(message)

               time.sleep(5)
          except RuntimeError as error:     
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
