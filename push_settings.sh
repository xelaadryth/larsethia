#!/bin/sh

# Replaces the settings file on the EC2 instance
scp -i ${aws_pem_location} server/conf/settings.py ${ec2_username}@${ec2_hostname}:/usr/src/larsethia/server/conf/settings.py