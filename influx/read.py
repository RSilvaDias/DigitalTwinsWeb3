import codecs
import json
from datetime import datetime
from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

mytoken = "WPhWR-JdcWrXVhzqngZMxXTkzfImrv1jECDvHXQyLQHodzNd_2vrJvt7NvXUc2TFuvoUnz1ujUjNpASfFi7zog=="
org = "ufg"
url = "http://200.137.197.215:31505"
bucket = 'digitaltwin'

client = InfluxDBClient(url=url, token=mytoken, org=org, debug=False) 

#with InfluxDBClient(url=url, token=mytoken, org=org, debug=False) as client:
query_api = client.query_api()


# Execute the query
query = '''
    from(bucket: "digitaltwin")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "paciente")
    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
result = client.query_api().query_data_frame(query, org=org)

# Parse the results
data = {}
for index, row in result.iterrows():
    time = row['_time'].isoformat()
    fields = row.to_dict()
    data[time] = {
        'temperature': float(fields.get('temperature', 0.0)),
        'bpm': float(fields.get('bpm', 0.0)),
        'oxysaturation': float(fields.get('oxysaturation', 0.0))
    }

# Convert the data to JSON
json_data = json.dumps(data, indent=2)
print(json_data)