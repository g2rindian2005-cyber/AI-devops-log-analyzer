variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"   # Mumbai — closest to India
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "ai-devops-chatops"
}

variable "node_instance_type" {
  description = "EC2 instance type for EKS nodes"
  type        = string
  default     = "t3.medium"
}
