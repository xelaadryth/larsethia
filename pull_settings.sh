#!/bin/sh
aws_pem_location=~/.ssh/xelaadryth_aws.pem
ec2_username=ubuntu
ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Copies the current settings.py file on the EC2 instance next to your current settings file
scp -i ${aws_pem_location} ${ec2_username}@${ec2_hostname}:/usr/src/larsethia/server/conf/settings.py server/conf/new-settings.py

# For your safety, not overwriting automatically
# mv server/conf/new-settings.py server/conf/settings.py
