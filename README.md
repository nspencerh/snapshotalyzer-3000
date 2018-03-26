# snapshotalyzer-3000

Demo project to manage AWS EC2 instance snapshots

# About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots

# Configuring

Shotty uses the configuration file created by the AWS cli:

`aws configure --profile shotty`

# Running

`pipeenv run 'python shotty/shotty.py <command> <subcommand> <--project=PROJECT>'`

*command* is instances, volumes, or snapshots
*subcommand* - depends on the command. (list, start, stop or snapshot)
*project* is optional
