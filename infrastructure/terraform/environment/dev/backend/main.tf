terraform {
  backend "s3" {
    for_each = toset(var.availability_zones)

    bucket       = "${var.environment}-${each.value}-${var.owner_id}"
    key          = "network/terraform.tfstate"
    region       = each.value
    encrypt      = true
    use_lockfile = true
  }
}
