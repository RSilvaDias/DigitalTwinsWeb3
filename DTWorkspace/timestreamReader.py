import logging
import json
import os
import boto3

from datetime import datetime

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Get db and table name from Env variables as well as TwinMaker component name and entityId
DATABASE_NAME = os.environ['TIMESTREAM_DATABASE_NAME']
TABLE_NAME = os.environ['TIMESTREAM_TABLE_NAME']
TM_COMPONENT_NAME = os.environ['TWINMAKER_COMPONENT_NAME']
TM_ENTITY_ID = os.environ['TWINMAKER_ENTITY_ID']

# Python boto client for AWS Timestream
QUERY_CLIENT = boto3.client('timestream-query')


# Utility function: parses a timestream row into a python dict for more convenient field access
def parse_row(column_schema, timestream_row):
    """
    Example:
    column=[
        {'Name': 'TelemetryAssetId', 'Type': {'ScalarType': 'VARCHAR'}},
        {'Name': 'measure_name', 'Type': {'ScalarType': 'VARCHAR'}},
        {'Name': 'time', 'Type': {'ScalarType': 'TIMESTAMP'}},
        {'Name': 'measure_value::double', 'Type': {'ScalarType': 'DOUBLE'}},
        {'Name': 'measure_value::varchar', 'Type': {'ScalarType': 'VARCHAR'}}
    ]
    row={'Data': [
        {'ScalarValue': 'Mixer_15_7e3c0bdf-3b1c-46b9-886b-14f9d0b9df4d'},
        {'ScalarValue': 'alarm_status'},
        {'ScalarValue': '2021-10-15 20:45:43.287000000'},
        {'NullValue': True},
        {'ScalarValue': 'ACTIVE'}
    ]}

    ->

    {
        'TelemetryAssetId': 'Mixer_15_7e3c0bdf-3b1c-46b9-886b-14f9d0b9df4d',
        'measure_name': 'alarm_status',
        'time': '2021-10-15 20:45:43.287000000',
        'measure_value::double': None,
        'measure_value::varchar': 'ACTIVE'
    }
    """
    data = timestream_row['Data']
    result = {}
    for i in range(len(data)):
        info = column_schema[i]
        datum = data[i]
        key, val = parse_datum(info, datum)
        result[key] = val
    return result

# Utility function: parses timestream datum entries into (key,value) tuples. Only ScalarTypes currently supported.
def parse_datum(info, datum):
    """
    Example:
    info={'Name': 'time', 'Type': {'ScalarType': 'TIMESTAMP'}}
    datum={'ScalarValue': '2021-10-15 20:45:25.793000000'}

    ->

    ('time', '2021-10-15 20:45:25.793000000')
    """
    if datum.get('NullValue', False):
        return info['Name'], None
    column_type = info['Type']
    if 'ScalarType' in column_type:
        return info['Name'], datum['ScalarValue']
    else:
        raise Exception(f"Unsupported columnType[{column_type}]")

# This function extracts the timestamp from a Timestream row and returns in ISO8601 basic format
def get_iso8601_timestamp(str):
    #  e.g. '2022-04-06 00:17:45.419000000' -> '2022-04-06T00:17:45.419000000Z'
    return str.replace(' ', 'T') + 'Z'

# Main logic
def lambda_handler(event, context):
    selected_property = event['selectedProperties'][0]

    LOGGER.info("Selected property is %s", selected_property)

    # 1. EXECUTE THE QUERY TO RETURN VALUES FROM DATABASE
    query_string = f"SELECT measure_name, time, measure_value::bigint" \
        f" FROM {DATABASE_NAME}.{TABLE_NAME} " \
        f" WHERE time > from_iso8601_timestamp('{event['startTime']}')" \
        f" AND time <= from_iso8601_timestamp('{event['endTime']}')" \
        f" AND measure_name = '{selected_property}'" \
        f" ORDER BY time ASC"
            
    try:
        query_page = QUERY_CLIENT.query(
            QueryString = query_string
        )
    except Exception as err:
        LOGGER.error("Exception while running query: %s", err)
        raise err

    # Query result structure: https://docs.aws.amazon.com/timestream/latest/developerguide/API_query_Query.html

    next_token = None
    if query_page.get('NextToken') is not None:
       next_token = query_page['NextToken']
    schema = query_page['ColumnInfo']

    # 2. PARSE TIMESTREAM ROWS
    result_rows = []
    for row in query_page['Rows']:
        row_parsed = parse_row(schema,row)
        #LOGGER.info('row parsed: %s', row_parsed)
        result_rows.append(row_parsed)

    # 3. CONVERT THE QUERY RESULTS TO THE FORMAT TWINMAKER EXPECTS

    # There must be one entityPropertyReference for bpm OR one for Temperature
    entity_property_reference_temp = {}
    entity_property_reference_temp['componentName'] = TM_COMPONENT_NAME
    entity_property_reference_temp['propertyName'] = 'temperature'
    entity_property_reference_temp['entityId'] = TM_ENTITY_ID


    entity_property_reference_bpm = {}
    entity_property_reference_bpm['componentName'] = TM_COMPONENT_NAME
    entity_property_reference_bpm['propertyName'] = 'bpm'
    entity_property_reference_bpm['entityId'] = TM_ENTITY_ID


    values_temp = []
    values_hum = []

    for result_row in result_rows:
        ts = result_row['time']
        measure_name = result_row['measure_name']
        measure_value = result_row['measure_value::bigint']

        time = get_iso8601_timestamp(ts)
        value = { 'doubleValue' : str(measure_value) }

        if measure_name == 'temperature':
            values_temp.append({
                'time': time,
                'value':  value
            })
        elif measure_name == 'bpm':
             values_hum.append({
                'time': time,
                'value':  value
            })

    # The final structure "propertyValues"
    property_values = []

    if(measure_name == 'temperature'):
        property_values.append({
            'entityPropertyReference': entity_property_reference_temp,
            'values': values_temp
        })
    elif(measure_name == 'bpm'):
        property_values.append({
            'entityPropertyReference': entity_property_reference_bpm,
            'values': values_hum
        })
    LOGGER.info("property_values: %s", property_values)

    # marshall propertyValues and nextToken into final response
    return_obj = {
       'propertyValues': property_values,
       'nextToken': next_token
       }

    return return_obj
