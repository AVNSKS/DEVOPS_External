variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type for Jenkins"
  type        = string
  default     = "c7i-flex.large"
}

variable "key_name" {
  description = "Name of the existing EC2 key pair to use for SSH"
  type        = string
}

variable "jenkins_ami_id" {
  description = "AMI ID for Jenkins EC2 (Ubuntu in ap-south-1)"
  type        = string
}