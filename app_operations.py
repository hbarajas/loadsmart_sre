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

	if elb_validation(client, elbName):
		instances = get_instances(client, elb_name)
		return instances
	else:
		return "resource not found"


def elb_add_instances(elbName, instance_add):

	# elb_instances - is a list of instances
	# instance_add - dictionary with below structure:
	# {'name': 'instance_id', 'description': 'instance to add'}
	# return 400 - wrong format data
	# return 409 - Instance already on load balancer
	# return 201 - instance added

	if elb_validation(client, elbName):
		instances = get_instances(client, elb_name)
		if not instance_add['name'] in instances:
			response = register_instances(client, elb_name, instance_id)

			return {
				'message': "Instance added",
				'status_code': '201'
			}, 201

		else:
			return {
				'message': 'Instance already on load balancer',
				'status_code': '409'}, 409 


def elb_remove_instances():
	if elb_validation(client, elbName):
		instances = get_instances(client, elb_name)
		if not instance_add['name'] in instances:
			return {
				'message': 'Instance not found in load balancer',
				'status_code': ''
			}
		else:
			response = deregister_instance(client, elbName)
			if response.get('ResponseMetadata')['HTTPStatusCode'] == 200:
				return {
					'message': 'Instance removed/deregistered from ELB',
					'status_code': 200
				}, 200

