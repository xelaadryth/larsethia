#!/bin/sh
aws_pem_location=~/.ssh/xelaadryth_aws.pem
ec2_username=ubuntu
ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Pushes the settings file onto the EC2 instance
scp -i ${aws_pem_location} server/conf/settings.py ${ec2_username}@${ec2_hostname}:~/settings.py

# Don't have permissions to actually move it
# sudo mv ~/settings.py /usr/src/larsethia/server/conf/settings.py
