module "tf_state_dev" {
  source = "./modules/tf_state"

  environment = "dev"
  account_id    = var.account_id
}

module "tf_state_prod" {
  source = "./modules/tf_state"

  backend_location  = var.backend_location
  environment = "prod"
  account_id    = var.account_id
}

module "tasky_dev_user" {
  source      = "./modules/iam-user"

  backend_location = var.backend_location
  account_id = var.account_id
  user_name   = var.user_dev
  policies = "./policies/tasky-dev"
}
