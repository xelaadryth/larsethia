#!/bin/bash
aws_pem_location=~/.ssh/xelaadryth_aws.pem
ec2_username=ubuntu
ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Pushes the database file on the EC2 instance
ssh -i ${aws_pem_location} ${ec2_username}@${ec2_hostname} mkdir \~/.aws
scp -i ${aws_pem_location} ~/.aws/credentials ${ec2_username}@${ec2_hostname}:~/.aws/credentials
