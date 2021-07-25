import boto3
import json
import os


def elb_validation(client, elb_name):
	"""Validate if the ELB provided exist """
	response = client.describe_load_balancers()
	for elb in response['LoadBalancerDescriptions']:
		return True if elb_name == elb.get('LoadBalancerName') else False


def get_instances(client, elb_name):
	"""Retrive all the instances from a ELB """
	response = client.describe_load_balancers(
		LoadBalancerNames=[elb_name]
	)
	return [instance['InstanceId'] for instance in response['LoadBalancerDescriptions'][0]['Instances']]


def instances_health(client, elb_name):
	"""Get instances health within LoadBalancer """
	instances_status = {}
	instances_ids = get_instances(client, elb_name)
	for ids in instances_ids:
		response = client.describe_instance_health(
			LoadBalancerName=elb_name,
			Instances=[
				{
					'InstanceId': ids
				}
			]
		)
		for instance_state in response['InstanceStates']:
			instances_status.update({ids: instance_state['State']})
	
	return instances_status


def register_instance(client, elb_name, instance_id):
	"""Register an instance to a ELB """


	response = client.register_instances_with_load_balancer(
		LoadBalancerName=elb_name,
		Instances=[
			{
				'InstanceId': instance_id
			}
		]
	)

	return response


def deregister_instance(client, elb_name, instance_id):
	"""Remove/deregister an instance from the ELB """
	response = client.deregister_instances_from_load_balancer(
		LoadBalancerName=elb_name,
		Instances=[
			{
				'InstanceId': instance_id
			}
		]
	)

	return response


# if __name__ == '__main__':
# 	client = boto3.client('elb', 'us-west-2')
# 	instances = instances_health(client, 'default-elb')
# 	print(instances)
# 	#return instances_status
