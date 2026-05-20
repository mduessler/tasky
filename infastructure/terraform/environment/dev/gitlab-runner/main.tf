module "network" {
  source     = "./modules/network"
  aws_region = var.aws_region
}

module "security" {
  source      = "./modules/security"
  environment = var.environment
  project_name = var.project_name
}

module "compute" {
  source                = "./modules/compute"
  environment           = var.environment
  instance_type         = var.instance_type
  subnet_id             = module.network.private_subnet_id
  runner_security_group = module.network.security_group_id
  permission_profile    = module.security.instance_profile_name
}
