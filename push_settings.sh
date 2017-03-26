#!/bin/sh
aws_pem_location=~/.ssh/xelaadryth_aws.pem
ec2_username=ubuntu
ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Replaces the settings file on the EC2 instance
scp -i ${aws_pem_location} server/conf/settings.py ${ec2_username}@${ec2_hostname}:/usr/src/larsethia/server/conf/settings.py