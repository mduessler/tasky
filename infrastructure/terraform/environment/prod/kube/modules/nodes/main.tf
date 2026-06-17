data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.owner_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.aws_region
  }
}

module "iam" {
  source = "./modules/iam"
}

module "controller" {
  source               = "../../../modules/compute"
  ami_owners           = ["self"]
  ami_filter_values    = ["kube-node-*"]
  instance_type        = var.instance_type
  subnet_id            = data.terraform_remote_state.network.outputs.private_subnets[var.vpc_id]
  security_groups      = [data.terraform_remote_state.network.outputs.controller_sgs[var.vpc_id]]
  iam_instance_profile = module.iam.controller_profile_name
  http_hops            = 2
  root_volume_size     = 20
  tags = {
    Name                                       = "kube-controller"
    "kubernetes.io/cluster/${var.clustername}" = "owned"

  }
}

module "workers" {
  for_each = var.workers

  source               = "../../../modules/compute"
  ami_owners           = ["self"]
  ami_filter_values    = ["kube-node-*"]
  instance_type        = var.instance_type
  subnet_id            = data.terraform_remote_state.network.outputs.private_subnets[var.vpc_id]
  security_groups      = [data.terraform_remote_state.network.outputs.controller_sgs[var.vpc_id]]
  iam_instance_profile = module.iam.worker_profile_name
  http_hops            = 2
  root_volume_size     = 50
  tags = {
    Name                                       = "kube-worker-${each.value}"
    "kubernetes.io/cluster/${var.clustername}" = "owned"
  }
}
