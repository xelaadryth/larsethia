#!/bin/sh
aws_pem_location=~/.ssh/xelaadryth_aws.pem
ec2_username=ubuntu
ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Pushes the database file on the EC2 instance. Replace evennia.db3 when the server isn't running.
scp -i ${aws_pem_location} server/evennia.db3 ${ec2_username}@${ec2_hostname}:~/evennia_new.db3
