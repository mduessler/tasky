module "networking" {
  source      = "./modules/networking"
  aws_region  = var.aws_region
  environment = var.environment
}

module "security" {
  source      = "./modules/security"
  environment = var.environment
}
