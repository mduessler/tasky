module "ssm_transfer" {
  source = "../../../modules/ssm_transfer"

  environment = var.environment
  owner_id    = var.owner_id
}
