# About

Simple CloudFormation templates designed with best practices in mind.

## Wordpress

Deploy a functional Wordpress instance on AWS with EC2 and RDS. Ability to restore from RDS snapshots. Automatic snapshot on stack deletion and backed up config files to a versioned S3 bucket.

Custom options include SSH CIDR IP range, instance size, and EC2 SSH key-pair.

## Wordpress Datacenter

Deploy a Virtual Private Cloud to host multiple scalable and fault tolerant Wordpress applications. Automatically create database and subnets for multiple Wordpress installations, at scale. Centralized MariaDB instance to maximize cost efficiency, and multiple size Wordpress applications available.

Can be used in multiple AWS regions. Multiple servers synced using AWS EFS.

### Setup

1. Deploy `1-base-infrastructure` template and configure basic networking infrastructure
2. Upload `custom-resources.zip` to a S3 bucket (could use the bucket created by first template)
3. Deploy `2a-shared-mariadb` and `2b-auto-subnet` to setup automatic resource allocation
4. Deploy `3-wp-application` as needed. The infrastructure should be able to fit up to 100 stacks
5. Deploy `4-bastion-host` as needed (for SSH into VPC)

## Rails on ECS

This project uses Amazon RDS for Postgres and AWS EC2 for running the ECS Cluster.

First deploy the `1-shared-vpc-iam` template on Cloudformation, then deploy as many `2-rails-on-ecs` applications as desired. Each application will have its own RDS and ElastiCache instance.

For local development, make sure `docker` and `docker-compose` are installed. Then, simply go into the folder and run `docker-compose up`. Rails should be up at `localhost`.

It's advisable for any users to create their own `master.key` and `credentials.yml.enc` file in the `config` folder, as the repository does not contain a valid pair. You can then run `docker-compose build` to build your own Docker image and tag it for upload to a repository.

## Creating an EC2 Key Pair

The use of these AWS CloudFormation templates will require you to specify an Amazon EC2 key pair for configuring SSH access to your instances.

Amazon EC2 key pairs can be created with the AWS Management Console. For more information, see Amazon EC2 Key Pairs in the Amazon EC2 User Guide for Linux Instances.
