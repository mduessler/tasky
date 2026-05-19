module "networking" {
  source      = "./modules/networking"
  aws_region  = var.aws_region
  environment = var.environment
}
