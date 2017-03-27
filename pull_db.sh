#!/bin/sh
aws_pem_location=~/.ssh/xelaadryth_aws.pem
ec2_username=ubuntu
ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Get the name of the newest db backup from the running EC2 instance
latest_db=`ssh -i ${aws_pem_location} ${ec2_username}@${ec2_hostname} ls -t1 /usr/src/larsethia/server/backups | head -n 1`
# Pulls the backup down next to your local db
scp -i ${aws_pem_location} ${ec2_username}@${ec2_hostname}:/usr/src/larsethia/server/backups/${latest_db} server/new-evennia.db3

# For your safety, not overwriting automatically
# mv server/new-evennia.db3 server/evennia.db3
