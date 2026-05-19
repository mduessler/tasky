module "networking" {
  source      = "./modules/networking"
  aws_region  = var.aws_region
  environment = var.environment
}

module "iam" {
  source      = "./modules/iam"
  environment = var.environment
}

module "compute" {
  source                   = "./modules/compute"
  environment              = var.environment
  instance_type            = var.instance_type
  private_subnet_id        = module.networking.private_subnet_id
  runner_security_group_id = module.networking.runner_security_group_id
  instance_profile_name    = module.iam.instance_profile_name
  gitlab_runner_token      = var.gitlab_runner_token
}
