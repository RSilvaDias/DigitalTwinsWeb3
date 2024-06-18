import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "vEftsdZwczSSuClHwAHtoLO7y5wBsharcMHe8t8ZtUhVaeG8W5oMJSvxQ1FUUjUJNdnr3xMnrhBCYpv75tnsaw=="
org = "ufg"
url = "http://200.137.197.215:31505"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="DigitalTwin"

write_api = write_client.write_api(write_options=SYNCHRONOUS)
   
for value in range(5):
  point = (
    Point("measurement1")
    .tag("tagname1", "tagvalue1")
    .field("field1", value)
  )
  write_api.write(bucket=bucket, org="ufg", record=point)
  time.sleep(1) # separate points by 1 second

query_api = write_client.query_api()

query = """from(bucket: "DigitalTwin")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "measurement1")
  |> mean()"""
tables = query_api.query(query, org="ufg")

for table in tables:
  for record in table.records:
    print(record)
    
    
    
    
    
records = query_api.query_stream('''
    from(bucket:"digitaltwin") 
        |> range(start: -10m)  
        |> filter(fn: (r) => r["_measurement"] == "paciente")
    ''')
    
    #for record in records:
    #    if record["_field"] == "temperature":
    #        print(f'Temperature is {record["_value"]} at {record["_time"]}')