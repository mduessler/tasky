module "tf_state_dev" {
  source = "./modules/tf_state"

  aws_region  = var.aws_region
  environment = "dev"
  owner_id    = var.owner_id
}

module "tf_state_prod" {
  source = "./modules/tf_state"

  aws_region  = var.aws_region
  environment = "prod"
  owner_id    = var.owner_id
}

module "tasky_dev_user" {
  source      = "./modules/iam-user"

  user_name   = var.user_dev
  policies = "./policies/tasky-dev"
}
