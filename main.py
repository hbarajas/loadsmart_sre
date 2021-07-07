import boto3
from flask import Flask, json, request
from app_operations import *
from loadsmart_elb_operations.elb_healthcheck import (
    instances_health, get_instances)

app = Flask(__name__)


@app.route('/healthcheck')
def health_status():

    elb_name = 'default-elb'
    data = elb_healthcheck()
    response = app.response_class(
        response=json.dumps(data),
        status=data['status_code'],
        mimetype='application/json'
    )

    return response


@app.route('/elb/<elbName>', methods=['GET', 'POST', 'DELETE'])
def elb_instances_operations(elbName):

    if request.method == 'POST':
        elb_ops(elbName, request.json)
        print(type(request.json))
        response = app.response_class(
            response=json.dumps(request.json),
            mimetype='application/json'
        )
        return response

    elif request.method == "DELETE":
        pass

    elif request.method == "GET":
        pass
    else:
        client = boto3.client('elb', 'us-west-2')
        res = get_instances(client, elbName)

        if res:
            data = {
                      'status_code': 200,
                      'Description': 'Instances Listed',
                      'instances_id': res
                   }
        else:
            data = {
                      'status_code': 401,
                      "Description": 'The ELB does not exist'
                   }

        response = app.response_class(
            response=json.dumps(data),
            mimetype='application/json'
        )

        return response

if __name__ == '__main__':
    app.run(debug=True)