module "tf_state_dev" {
  source = "./modules/tf_state"

  environment = "dev"
  account_id    = var.account_id
}

module "tf_state_prod" {
  source = "./modules/tf_state"

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

module "tasky_prod_network_user" {
  source           = "./modules/iam-user"
  backend_location = var.backend_location
  account_id       = var.account_id
  user_name        = var.user_prod_network
  policies         = "./policies/tasky-prod-network"
}

module "tasky_prod_kube_user" {
  source           = "./modules/iam-user"
  backend_location = var.backend_location
  account_id       = var.account_id
  user_name        = var.user_prod_kube
  policies         = "./policies/tasky-prod-kube"
}

module "tasky_prod_packer_user" {
  source           = "./modules/iam-user"
  backend_location = var.backend_location
  account_id       = var.account_id
  user_name        = var.user_prod_packer
  policies         = "./policies/tasky-prod-packer"
}
