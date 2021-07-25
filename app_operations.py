import json
from loadsmart_elb_operations.elb_operations import *


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


def instances_list(client, elb_name):

	instances = get_instances(client, elb_name)

	return instances


def elb_add_instances(elbName, instance_add):

	# elb_instances - is a list of instances
	# instance_add - dictionary with below structure:
	# {'name': 'instance_id', 'description': 'instance to add'}
	# return 400 - wrong format data
	# return 409 - Instance already on load balancer
	# return 201 - instance added
	instances = get_instances(client, elb_name)
	response = register_instances(client, elb_name, instance_id)
	pass


def elb_remove_instances():
	pass


def elb_validation(client, elb_name):
	pass

