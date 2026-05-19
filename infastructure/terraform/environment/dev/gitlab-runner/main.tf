module "networking" {
  source      = "./modules/networking"
  aws_region  = var.aws_region
  environment = var.environment
}

module "security" {
  source      = "./modules/security"
  environment = var.environment
}

module "compute" {
  source                = "./modules/compute"
  environment           = var.environment
  instance_type         = var.instance_type
  subnet_id             = module.networking.private_subnet_id
  runner_security_group = module.networking.security_group_id
  permission_profile = module.security.instance_profile_name
}
