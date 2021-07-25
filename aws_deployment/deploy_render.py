import json
import boto3
import os
import argparse

from cloudformation_template.loadsmart_stack import aws_template


def deploy(stack_name, template):

	client = boto3.client('cloudformation', 'us-west-2')

	response = client.create_stack(
		StackName=stack_name,
		TemplateBody=template,
		)
	
	return response

def render(template):
	output = template.to_json()

	return output


def render_to_file(template, path):
	"""Render cloudformation template to file path."""
	template = template.to_json(indent=None, separators=(',', ':'))
	with open(path, 'w') as file:
		file.write(template)


def main(args):
	""" """
	template = aws_template()
	if args.action == 'launch':
		response = deploy(args.stack_name, template)
		print(response)

	elif args.action == 'render':
		output = render()
		print(output)

	else:
		raise Exception("Action not supported, please use one of this two options deploy/render")


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Create and deploy cloudformation template to AWS')
	parser.add_argument(
		'--action',
		type=str,
		required=True,
		default='render',
		help="Deploy template to AWS")
	parser.add_argument(
		'--stack_name',
		type=str,
		required=False,
		default='test_stack',
		help="Deploy template to AWS")
	
	args = parser.parse_args()
	main(args)
