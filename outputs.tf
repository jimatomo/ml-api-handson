output "eks_vpc_id" {
  value = module.vpc.vpc_id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.ecr.repository_url
}

output "ec2_instance_arn" {
  value = module.taurus_ec2.ec2_instance_arn
}
