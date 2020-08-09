#!/usr/bin/env bash

jump_host=blackjack.ec2
db_host=aay4sanz61mwsk.cr0buvyuleg4.us-east-2.rds.amazonaws.com
db_port=5432

local_port=5555

ssh -vNL $local_port:$db_host:$db_port $jump_host
