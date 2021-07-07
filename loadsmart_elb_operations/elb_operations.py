import boto3
import json
import os


def get_instances(client, elb_name):

	try:
		response = client.describe_load_balancers(
			LoadBalancerNames=[elb_name]
		)
		return [instance['InstanceId'] for instance in response['LoadBalancerDescriptions'][0]['Instances']]

	except Exception as err:
		return None


def instances_health(client, elb_name):

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
	try:
		response = client.register_instances_with_load_balancer(
			LoadBalancerName=elb_name,
			Instances=[
				{
					'InstanceId': instance_id
				}
			]
		)

	except Exception as err:
		print(err)
	
	return response


def deregister_instance(client, elb_name, instance_id):

	pass


# if __name__ == '__main__':
# 	client = boto3.client('elb', 'us-west-2')
# 	instances = instances_health(client, 'default-elb')
# 	print(instances)
# 	#return instances_status
