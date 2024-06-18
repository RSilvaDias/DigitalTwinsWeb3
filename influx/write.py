import codecs
import time
from datetime import datetime

from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

mytoken = "WPhWR-JdcWrXVhzqngZMxXTkzfImrv1jECDvHXQyLQHodzNd_2vrJvt7NvXUc2TFuvoUnz1ujUjNpASfFi7zog=="
org = "ufg"
url = "http://200.137.197.215:31505"

with InfluxDBClient(url=url, token=mytoken, org=org, debug=False) as client:

    query_api = client.query_api()

    p = Point("paciente").tag("device", "watch").field("bpm", 98).field("temperature", 36.451).field("oxysaturation", 98.38376).time(datetime.utcnow(),WritePrecision.MS)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    # write using point structure
    write_api.write(bucket="digitaltwin", record=p)
    # write using line protocol
    #write_api.write(bucket="digitaltwin", record=line_protocol)

    line_protocol = p.to_line_protocol()
    print(line_protocol)