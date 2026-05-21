module "network" {
  source      = "./modules/network"
  aws_region  = var.aws_region
  runner_name = var.runner_name
}

module "security" {
  source      = "./modules/security"
  environment = var.environment
  runner_name = var.runner_name
}

module "compute" {
  source                = "./modules/compute"
  environment           = var.environment
  runner_name           = var.runner_name
  instance_type         = var.instance_type
  subnet_id             = module.network.private_subnet_id
  runner_security_group = module.network.security_group_id
  permission_profile    = module.security.instance_profile_name
}

module "ssm_transfer_bucket" {
  source = "../../../modules/s3_bucket"
  name = "tasky-ssm-bucket-${var.owner_id}-dev"

  tags = {
    Component = "ansible-ssm-transfer"
  }
}
