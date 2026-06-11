module "controller" {
  source             = "../../../modules/compute"
  ami_owners         = ["self"]
  ami_filter_values  = ["kube-node-*"]
  instance_type      = var.instance_type
  subnet_id          = module.network.private_subnet_id
  security_groups    = [module.network.security_group_id]
  permission_profile = module.security.instance_profile_name
  http_hops          = 2
  root_volume_size   = 20
  namespace          = var.environment
  name               = "kube-controller"
}

module "worker" {
  for_each = var.workers

  source             = "../../../modules/compute"
  ami_owners         = ["self"]
  ami_filter_values  = ["kube-node-*"]
  instance_type      = var.instance_type
  subnet_id          = module.network.private_subnet_id
  security_groups    = [module.network.security_group_id]
  permission_profile = module.security.instance_profile_name
  http_hops          = 2
  root_volume_size   = 50
  namespace          = var.environment
  name               = each.value
}

module "network" {
  source             = "../../../modules/network"
  aws_region  = var.aws_region
}
