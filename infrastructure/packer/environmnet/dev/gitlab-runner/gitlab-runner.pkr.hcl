packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.8"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  ami_name = "gitlab-runner-${formatdate("YYYYMMDD-HHmmss", timestamp())}"
  instance_type = "t3.micro"
  region        = "eu-central-1"
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
}

build {
  name = "learn-packer"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "file" {
    sources     = ["scripts/init-file-structure", "scripts/install-docker", "scripts/install-gitlab-runner", "scripts/cleanup"]
    destination = "/tmp/"
  }


  provisioner "shell" {
    inline = [
      "chmod +x /tmp/init-file-structure /tmp/install-docker /tmp/install-gitlab-runner",
      "sudo /tmp/init-file-structure",
      "sudo /tmp/install-docker",
      "sudo /tmp/install-gitlab-runner"
    ]
  }

}
