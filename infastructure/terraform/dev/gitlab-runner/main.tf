module "networking" {
  source      = "./modules/networking"
  aws_region  = var.aws_region
  environment = var.environment
}

module "iam" {
  source      = "./modules/iam"
  environment = var.environment
}
