module "vpcs" {
  for_each = toset(var.availability_zones)

  source            = "../../../modules/network"
  availability_zone = each.value
  environment       = var.environment
}
