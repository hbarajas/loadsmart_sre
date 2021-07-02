import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from troposphere.autoscaling import AutoScalingGroup
from troposphere.autoscaling import LaunchConfiguration
from troposphere import (
    Base64,FindInMap, GetAtt, GetAZs, Join, Output,
    Parameter, Ref, Template)
from troposphere.cloudformation import (InitConfig, Init, InitFile, InitFiles,
                                        WaitConditionHandle)


user_data = """
echo "Test user data"
"""
def AddAMI(template):
    template.add_mapping(
        "RegionMap",
        {
            "us-west-2": {"AMI": "ami-fcff72cc"}
        },
    )


def main():
    template = Template()

    template.add_description(
        "AWS CloudFormation LoadSmart template: ELB with 1 EC2 instance"
    )

    AddAMI(template)

    # Add the Parameters
    KeyPair = template.add_parameter(
        Parameter(
            "KeyName",
            Type="String",
            Default="mark",
            Description="Name of an existing EC2 KeyPair to "
            "enable SSH access to the instance",
        )
    )

    InstanceType = template.add_parameter(
        Parameter(
            "InstanceType",
            Type="String",
            Description="EC2 instance type",
            Default="m1.small"
        )
    )

    webport_param = template.add_parameter(
        Parameter(
            "WebServerPort",
            Type="String",
            Default="8080",
            Description="TCP/IP port of the web server",
        )
    )

    # Define the instance security group
    instance_sg = template.add_resource(
        ec2.SecurityGroup(
            "InstanceSecurityGroup",
            GroupDescription="Enable SSH and HTTP access on the inbound port",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="22",
                    ToPort="22",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=Ref(webport_param),
                    ToPort=Ref(webport_param),
                    CidrIp="0.0.0.0/0",
                ),
            ],
        )
    )

    # Add the web server instances
    instance = template.add_resource(
        ec2.Instance(
            "LoadsmartInstance1",
            SecurityGroups=[Ref(instance_sg)],
            KeyName=Ref(KeyPair),
            InstanceType=Ref("InstanceType"),
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
            UserData=Base64(Ref(webport_param)),
        )
    )

    elasticLB = template.add_resource(
        elb.LoadBalancer(
            "defaultelb1",
            AvailabilityZones=GetAZs(""),
            ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
                Enabled=True,
                Timeout=300,
            ),
            CrossZone=True,
            Instances=[Ref(instance)],
            Listeners=[
                elb.Listener(
                    LoadBalancerPort="80",
                    InstancePort=Ref(webport_param),
                    Protocol="HTTP",
                ),
            ],
            HealthCheck=elb.HealthCheck(
                Target=Join("", ["HTTP:", Ref(webport_param), "/"]),
                HealthyThreshold="3",
                UnhealthyThreshold="5",
                Interval="30",
                Timeout="5",
            ),
        )
    )

    LoadSmartWaitHandle = template.add_resource(WaitConditionHandle(
        "LoadSmartWaitHandle",
    ))

    LoadSmartLaunchConfig = template.add_resource(LaunchConfiguration(
        "LoadSmartLaunchConfig",
        UserData=Base64(Join("", [
            "#!/bin/bash\nWAIT=\'",
            Ref(LoadSmartWaitHandle),
            "\'\n",
            user_data
        ])),
        ImageId='ami-fcff72cc',
        KeyName=Ref(KeyPair),
        SecurityGroups=Ref(instance_sg),
        IamInstanceProfile="autoscaling",
        InstanceType=Ref(InstanceType),
        ))

    template.add_resource(AutoScalingGroup(
        "LoadSmartAutoscalingGroup",
        LoadBalancerNames=[Ref(elasticLB)],
        MinSize='1',
        MaxSize='2',
        VPCZoneIdentifier=['us-west-2'],
        LaunchConfigurationName=Ref(LoadSmartLaunchConfig),
        TerminationPolicies=['ClosestToNextInstanceHour', 'OldestInstance', 'Default'],
    ))

    template.add_output(
        Output(
            "URL",
            Description="API URL",
            Value=Join("", ["http://", GetAtt(elasticLB, "DNSName")]),
        )
    )

    print(template.to_json())


if __name__ == "__main__":
    main()