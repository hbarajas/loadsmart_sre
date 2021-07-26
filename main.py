import boto3
from flask import Flask, json, request
from flask_expects_json import expects_json
from app_operations import *
from app_operations import (
    instances_health, get_instances)

app = Flask(__name__)


schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
    },
    'required': ['name']
}

@app.route('/health')
def health:
    response = app.response_class(
        response={'message': 'OK'},
        status='200',
        mimetype='application/json'
    )

    return response

@app.route('/healthcheck')
def health_status():

    elb_name = 'default-elb'
    client = boto3.client('elb', 'us-west-2')
    data = elb_healthcheck(client, elb_name)
    response = app.response_class(
        response=json.dumps(data),
        status=data['status_code'],
        mimetype='application/json'
    )

    return response


@app.route('/elb/<elbName>', methods=['GET', 'POST', 'DELETE'])
@expects_json(schema, ignore_for=['GET'])
def elb_instances_operations(elbName):

    client = boto3.client('elb', 'us-west-2')
    if request.method == 'POST':
        elb_add_instances(elbName, request.json)

        response = app.response_class(
            response=json.dumps(request.json),
            mimetype='application/json'
        )
        return response

    elif request.method == "DELETE":
        pass

    elif request.method == "GET":
        pass


if __name__ == '__main__':
    app.run(debug=True, port=8080)
