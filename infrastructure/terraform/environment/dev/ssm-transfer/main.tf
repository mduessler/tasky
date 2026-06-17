module "ssm_transfer" {
  source = "../../../modules/ssm_transfer"

  environment = var.environment
  account_id  = var.account_id
}
