#!/bin/sh

# Required for SCPing database and server settings
export aws_pem_location=~/.ssh/xelaadryth_aws.pem
export ec2_username=ubuntu
export ec2_hostname=ec2-34-208-236-184.us-west-2.compute.amazonaws.com

# Required for backup.sh
export git_access_token=`cat git_access_token.txt`
export git_user=xelaadryth
export git_repo=larsethia
export git_branch=origin/master