data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "tasky-tf-state-${var.account_id}-${var.environment}"
    key    = "network/terraform.tfstate"
    region = var.backend_location
  }
}

module "iam" {
  source = "../iam"
}

data "aws_ami" "kube_node" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "name"
    values = ["kube-node-*"]
  }
}

module "controller" {
  source                  = "./modules/controller"
  availability_zone       = var.availability_zone
  vpc_id                  = var.vpc_id
  subnet_id               = data.terraform_remote_state.network.outputs.private_subnets[var.vpc_id]
  instance_type           = var.controller_instance_type
  controller_profile_name = module.iam.controller_profile_name
  image_id                = data.aws_ami.kube_node.id
  controller_sg_id        = data.terraform_remote_state.network.outputs.controller_sgs[var.vpc_id]
  worker_sg_id            = data.terraform_remote_state.network.outputs.worker_sgs[var.vpc_id]
  clustername             = var.clustername
}

module "workers" {
  for_each = var.workers

  source               = "../../../../../modules/compute"
  instance_type        = var.worker_instance_type
  instance_profile     = module.iam.worker_profile_name
  image_owner          = ["self"]
  image_filter_values  = ["kube-node-*"]
  subnet_id            = data.terraform_remote_state.network.outputs.private_subnets[var.vpc_id]
  security_group_ids   = [data.terraform_remote_state.network.outputs.worker_sgs[var.vpc_id]]
  metadata_hop_limit   = 2
  root_volume_size     = 50
  tags = {
    Name                                       = "kube-worker-${each.value}"
    "kubernetes.io/cluster/${var.clustername}" = "owned"
  }
}
