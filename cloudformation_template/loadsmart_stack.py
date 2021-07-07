import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from troposphere.autoscaling import AutoScalingGroup
from troposphere.autoscaling import LaunchConfiguration
from troposphere import (
    Base64,FindInMap, GetAtt, GetAZs, Join, Output,
    Parameter, Ref, Template)
from troposphere.cloudformation import (InitConfig, Init, InitFile, InitFiles,
                                        WaitConditionHandle)


user_data = """#!/bin/bash
set -e
set -x

yum update -y
yum install -y git docker

service docker start

git clone https://hbarajas:{token}@github.com/hbarajas/loadsmart_sre.git
cd loadsmart_sre && docker build -t loadsmart_api:latest . 
docker run -d -p 5000:5000 loadsmart_api:latest

"""


def AddAMI(template):
    template.add_mapping(
        "RegionMap",
        {
            "us-west-2": {"AMI": "ami-0721c9af7b9b75114"}
        },
    )


def render_template():
    template = Template()

    template.set_description(
        "AWS CloudFormation LoadSmart template: ELB with 1 EC2 instance"
    )

    AddAMI(template)

    # Add the Parameters
    KeyPair = template.add_parameter(
        Parameter(
            "loadsmartkey",
            Type="String",
            Default="loadsmart",
            Description="key pair to ssh"
        )
    )

    InstanceType = template.add_parameter(
        Parameter(
            "InstanceType",
            Type="String",
            Description="EC2 instance type",
            Default="t2.micro"
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

    template.add_parameter(Parameter(
        "ServiceName",
        Default='default-elb',
        Type="String",
        Description="Service Name"))

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
    instances_list = []
    for instance_name in ['LoadsmartInstance1', 'LoadsmartInstance2']:
        instance = template.add_resource(
            ec2.Instance(
                instance_name,
                SecurityGroups=[Ref(instance_sg)],
                KeyName=Ref(KeyPair),
                InstanceType=Ref("InstanceType"),
                ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
                UserData=Base64(Ref(webport_param)),
            )
        )
        instances_list.append(instance)

    LoadSmartElb = template.add_resource(
        elb.LoadBalancer(
            "LoadSmartElb",
            AvailabilityZones=GetAZs(""),
            ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
                Enabled=True,
                Timeout=300,
            ),
            CrossZone=True,
            Instances=[Ref(i) for i in instances_list],
            Listeners=[
                elb.Listener(
                    LoadBalancerPort="80",
                    InstancePort=Ref(webport_param),
                    Protocol="HTTP",
                ),
            ],
            LoadBalancerName=Ref('ServiceName'),
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
        ImageId='ami-0721c9af7b9b75114',
        KeyName=Ref(KeyPair),
        SecurityGroups=[Ref(instance_sg)],
        IamInstanceProfile="loadsmart_service",
        InstanceType=Ref(InstanceType),
        ))

    template.add_output(
        Output(
            "URL",
            Description="API URL",
            Value=Join("", ["http://", GetAtt(LoadSmartElb, "DNSName")]),
        )
    )

    print(template.to_json())
    return template

# if __name__ == "__main__":
#     main()