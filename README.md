# About

Simple CloudFormation templates designed with best practices in mind.

## Wordpress

Deploy a functional Wordpress instance on AWS with EC2 and RDS. Ability to restore from RDS snapshots. Automatic snapshot on stack deletion and backed up config files to a versioned S3 bucket.

Customization options include SSH CIDR IP range, instance size, and EC2 SSH key-pair.

## Wordpress Datacenter

Readme coming soon.

## Creating an EC2 Key Pair

The use of these AWS CloudFormation templates will require you to specify an Amazon EC2 key pair for configuring SSH access to your instances.

Amazon EC2 key pairs can be created with the AWS Management Console. For more information, see Amazon EC2 Key Pairs in the Amazon EC2 User Guide for Linux Instances.
