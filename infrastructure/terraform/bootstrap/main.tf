module "tf_state_dev" {
  source = "./modules/tf_state"

  environment = "dev"
  owner_id    = var.owner_id
}

module "tf_state_prod" {
  source = "./modules/tf_state"

  backend_location  = var.backend_location
  environment = "prod"
  owner_id    = var.owner_id
}

module "tasky_dev_user" {
  source      = "./modules/iam-user"

  backend_location = var.backend_location
  owner_id = var.owner_id
  user_name   = var.user_dev
  policies = "./policies/tasky-dev"
}
