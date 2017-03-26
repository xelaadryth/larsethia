#!/bin/sh

# Pushes the database file on the EC2 instance. Replace evennia.db3 when the server isn't running.
scp -i ${aws_pem_location} server/evennia.db3 ${ec2_username}@${ec2_hostname}:/usr/src/larsethia/server/evennia_new.db3
