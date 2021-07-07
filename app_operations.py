import json
from loadsmart_elb_operations.elb_operations import *

client = boto3.client('elb', 'us-west-2')

def elb_healthcheck(client, elb_name):

	health = True
	instances_state = instances_health(client, elb_name)
    if 'OutOfService' in instances_state.values():
        health = False

    if health:
        res = {
                'status_code': 200,
                'Description': 'The service is up'
              }
    else:
        res = {
                'status_code': 400,
                'Description': 'The service is down'
              }

	return res


def instances_list():

	pass


def elb_add_instances(elbName, instances_running, instance_add):

	pass


def elb_remove_instances():
	pass


def elb_ops(elbName, request_ops):
	pass

