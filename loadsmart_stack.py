from troposphere import Parameter, Ref, Template, GetAtt
from troposphere.ec2 import Instance
from troposphere.elasticloadbalancingv2 import (
	TargetGroup, ListenerRule, Listener, LoadBalancer,
	LoadBalancerAttributes, Action, Condition)


t = Template()

t.add_description("Stack creating a VPC")


ec2_instance = template.add_resource(
    Instance(
        "Ec2Instance",
        ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
        InstanceType="t1.micro",
        KeyName=Ref(keyname_param),
        SecurityGroups=["default"],
        UserData=Base64("80"),
    )
)
