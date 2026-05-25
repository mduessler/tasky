# Infrastructure Documentation

This document gives an overview, usage, and an explanation about design choices
done in the infrastructure of this project. The infrastructure is split into two
parts: the *Backend* which has to be initialized once, and the *GitLab Runner*
which can be created, replaced, or destroyed on demand. The next chapters describe
both parts in detail. The last section explains how to run all together.

## Backend

The *Backend* provides a centralized remote *TFState* storage, enabling all
developers to share and synchronize the same infrastructure state.

### Initialization

To initialize the backend simply run from the root of the project the command
`make terraform-init-bootstrap`. The initializing has to be done once. Only the
admin user, called **tasky-admin**, is allowed to perform the operation. This
command does multiple things:

1. **Change Working directory** — At first the command changes the working directory
   to the directory [infrastructure/terraform/bootstrap](../../infrastructure/terraform/bootstrap).
   In this directory is the configuration of the backend stored.
2. **Initialize Working directory** to prepare the configuration files.
3. **Apply the infrastructure** to create the backend on the remote system.

### File structure

The next graph represents the file structure of the backend. It also displays modules
not located in the backend, which are needed for the configuration.

```shell
├── bootstrap
│   ├── main.tf
│   ├── modules
│   │   ├── dynamo_db
│   │   │   ├── main.tf
│   │   │   ├── output.tf
│   │   │   └── variables.tf
│   │   └── logging
│   │       ├── main.tf
│   │       ├── output.tf
│   │       └── variables.tf
│   ├── output.tf
│   ├── provider.tf
│   └── variables.tf
└── modules
    ├── s3_bucket
    │   ├── main.tf
    │   ├── output.tf
    │   └── variables.tf
    └── s3_security
        ├── main.tf
        └── variables.tf
```

### Overview

The backend consists of two [*Simple Storage Service *S3**](https://aws.amazon.com/s3/)
buckets. The purpose of the two buckets is:

1. **State-Bucket-Dev** — Store the *TFState* for the dev environment
2. **Log-Bucket** — Log the access on the bucket of *State-Bucket-Dev* storage.

Furthermore a [*DynamoDB*](https://aws.amazon.com/dynamodb/) is used, to store locks.
A *DynamoDB* is a fully managed, NoSQL database. The locks ensure that no two developers
can write to a TFState at the same time.

The *State-Bucket-Dev* is hardened with a bucket policy that denies any non-TLS
traffic, and with a lifecycle rule that expires non-current state versions after
*90 days*. Incomplete multipart uploads are aborted after *7 days*.

## GitLab Runner

The *GitLab Runner* is a self-hosted CI/CD runner, deployed on AWS. Its purpose
is to execute pipeline jobs from GitLab inside a controlled, private network.
The runner is **not reachable from the public internet** — all access happens via
[*AWS Systems Manager (SSM) Session Manager*](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).
The runner is build, deployed, and configured in three layers:

1. **Packer** — Build a hardened *Amazon Machine Image (AMI)* with all required
   software pre-installed.
   > This step needs to be done at least one time before the gitlab-runner will
   > be initialized.
2. **Terraform** — Provision the network, the *EC2* instance, and the
   *IAM* permissions on AWS.
3. **Ansible** — Register the runner against the GitLab instance and apply the
   runtime configuration.

> With this configuration, you can create multiple runners. However, each GitLab
> Runner must have a unique name.

### Naming convention

Each runner is identified by a unique *runner name*. The name is used as a suffix
for the AWS resources (*EC2* tag, *IAM* role, *Terraform* state key) and as the
display name in the GitLab UI. To keep the naming consistent, the *runner name*
must be a zero-padded, incrementing number — `01`, `02`, `03`, and so on. New
runners pick the next free number.

### State isolation

Each runner has its own *TFState* file, stored in the *State-Bucket-Dev* under
the key `runner/dev/${runner_name}/terraform.tfstate`. This isolation has two
consequences:

1. **Independent lifecycle** — Runners can be created, updated, or destroyed
   without affecting other runners. A `terraform apply` for runner `01` never
   touches the state of runner `02`.
2. **Backend reconfiguration per runner** — The state key is passed in at
   *Terraform init* time via `-backend-config="key=..."`. The
   [gitlab-runner script](../../infrastructure/scripts/gitlab-runner) handles
   this transparently — every `install` or `destroy` re-initializes the backend
   with the correct key for the selected runner.

The *SSM transfer bucket* is the only shared resource across runners. The script
imports it into each runner state if it already exists, and removes it from the
state on destroy so the bucket itself is not deleted.

### File structure

The next graph represents the file structure of the GitLab Runner. The structure
is split between the three tools mentioned above. The shared *s3_bucket* and
*s3_security* modules from the backend are reused.

```shell
├── packer
│   └── environmnet
│       └── dev
│           └── gitlab-runner
│               ├── gitlab-runner.pkr.hcl
│               └── scripts
│                   ├── cleanup
│                   ├── init-file-structure
│                   ├── install-docker
│                   ├── install-gitlab-runner
│                   └── prune-docker
├── terraform
│   ├── environment
│   │   └── dev
│   │       └── gitlab-runner
│   │           ├── main.tf
│   │           ├── modules
│   │           │   ├── compute
│   │           │   │   ├── main.tf
│   │           │   │   ├── output.tf
│   │           │   │   └── variables.tf
│   │           │   ├── network
│   │           │   │   ├── main.tf
│   │           │   │   ├── output.tf
│   │           │   │   └── variables.tf
│   │           │   └── security
│   │           │       ├── main.tf
│   │           │       ├── output.tf
│   │           │       └── variables.tf
│   │           ├── output.tf
│   │           ├── provider.tf
│   │           └── variables.tf
│   └── modules
│       ├── s3_bucket
│       └── s3_security
└── ansible
    └── environment
        └── dev
            └── gitlab-runner
                ├── ansible.cfg
                ├── group_vars
                │   └── all.yaml
                ├── inventory
                │   └── aws_ec2.yaml
                ├── playbook.yaml
                ├── requirements.yaml
                └── roles
                    └── gitlab_runner
                        ├── defaults
                        ├── handlers
                        └── tasks
```

### Image (Packer)

[*Packer*](https://www.packer.io/) builds a custom *AMI* based on *Ubuntu 24.04
LTS*. The image is build once and reused for every runner instance. Like this the
startup time of a new runner is reduced and the runtime environment stays
reproducible. The build is configured in
[gitlab-runner.pkr.hcl](../../infrastructure/packer/environmnet/dev/gitlab-runner/gitlab-runner.pkr.hcl)
and runs the following provisioning scripts in order:

1. **init-file-structure** — Prepare the keyring and apt source directories.
2. **install-docker** — Install a pinned version of *Docker CE* (`5:29.5.2`) and
   *containerd.io* (`1.7.27`) from the official Docker repository.
3. **install-gitlab-runner** — Install a pinned version of *gitlab-runner*
   (`18.11.3-1`) from the official GitLab APT repository.
4. **prune-docker** — A small script that is installed as a cron job. It runs
   nightly at *02:00* and removes unused Docker images, containers, and volumes
   to keep the disk usage low.

The resulting image is tagged with the timestamp of the build, in the format
`gitlab-runner-YYYYMMDD-HHmmss`. The Terraform compute module always picks the
most recent image owned by the account.

> **Note** — Old AMIs and their EBS snapshots are not removed automatically. They
> accumulate over time and incur storage costs. Old images have to be deregistered
> manually (or via a separate cleanup job).

### Provisioning (Terraform)

The Terraform configuration in
[terraform/environment/dev/gitlab-runner](../../infrastructure/terraform/environment/dev/gitlab-runner)
is split into three local modules and one shared *SSM transfer bucket*.

#### Network module

The *network* module creates a dedicated [*Virtual Private Cloud (VPC)*](https://aws.amazon.com/vpc/)
with the CIDR block `10.0.0.0/16`. The VPC contains two subnets:

1. **Public subnet** (`10.0.0.0/24`) — Hosts the *NAT Gateway* and is attached to
   an *Internet Gateway*. No workload runs here.
2. **Private subnet** (`10.0.1.0/24`) — Hosts the runner *EC2* instance. Outbound
   traffic is routed through the *NAT Gateway*.

The security group of the runner allows **outbound traffic only** on ports
*80* and *443*. No inbound rules are defined, the runner can not be reached
directly. To reduce traffic over the *NAT Gateway*, a *VPC Gateway Endpoint*
for *S3* is attached to the private route table.

#### Compute module

The *compute* module launches a single *EC2* instance from the Packer AMI. The
default instance type is `t3.small`. The following hardening is applied:

1. **Encrypted root volume** — A *20 GB* `gp3` volume with EBS encryption.
2. **IMDSv2 required** — The Instance Metadata Service only accepts token-based
   requests (`http_tokens = "required"`).
3. **No public IP** — The instance is placed in the private subnet without a
   public address.

#### Security module

The *security* module creates the *IAM* role and instance profile of the runner.
Two permission sets are attached:

1. **AmazonSSMManagedInstanceCore** — The AWS-managed policy that allows the
   instance to register with *Systems Manager*. This is what enables the
   SSM-based connection.
2. **ssm-bucket-access** — A custom inline policy that allows the runner to read
   and write objects in the *SSM transfer bucket* (see next section).

#### SSM transfer bucket

The *SSM transfer bucket* is a dedicated *S3* bucket named
`ansible-ssm-${owner_id}-dev`. It is used by Ansible to transfer files to the
runner during the SSM session, since the SSM connection plugin needs a shared
location to exchange data. The bucket has:

1. **TLS-only policy** — All non-TLS requests are denied.
2. **Lifecycle rule** — All objects are expired after *1 day*. The bucket only
   holds transient data, no state has to be kept.

### Configuration (Ansible)

Once the runner is provisioned, the Ansible playbook in
[ansible/environment/dev/gitlab-runner](../../infrastructure/ansible/environment/dev/gitlab-runner)
takes over. The connection is build using the [*community.aws.aws_ssm*](https://docs.ansible.com/ansible/latest/collections/community/aws/aws_ssm_connection.html)
connection plugin, which tunnels the playbook through *SSM Session Manager*.
The dynamic inventory `aws_ec2.yaml` discovers all runners tagged with
`Project=tasky`, `Role=gitlab-runner`, and `Environment=dev`.

The `gitlab_runner` role performs three tasks:

1. **Register gitlab-runner** — Run `gitlab-runner register` with the runner
   token, the *docker* executor, and the *alpine:latest* default image. The
   Docker socket is mounted into each job so jobs can themself spawn containers.
2. **Set concurrent jobs** — Pin `concurrent = 1` in `/etc/gitlab-runner/config.toml`
   so the *t3.small* instance is not overloaded.
3. **Verify gitlab-runner is running** — Make sure the systemd service is started
   and enabled.

The runner token is passed in as an extra variable at runtime, it is never
stored in the repository.

### Connection

Since no SSH port is open and no public IP is assigned, the only way to reach
the runner is via *SSM Session Manager*. The exact command is part of the
Terraform output:

```shell
aws ssm start-session \
    --target <runner_instance_id> \
    --region eu-central-1 \
    --profile tasky-dev
```

> The correct connection information is printed during the GitLab Runner
> infrastructure initialization. After the AWS resource initialized with
> Terraform.

## How to run all

The next sections describe how to set up the complete infrastructure from scratch.
All commands are exposed through the [Makefile](../../Makefile) at the project
root.

### Prerequisites

The following environment variables must be set before running any command:

1. **`TF_VAR_owner_id`** — The *AWS account ID* of the target account. Terraform
   reads this as the `owner_id` input variable.
2. **`AWS_PROFILE`** — The local AWS profile used for authentication. Two profiles
   are used in this project:
   - **`aws-user-admin`** — Permission to create the backend and build the AMI.
     Used for one-time setup steps.
   - **`aws-user-dev`** — Limited permission to manage the runner lifecycle. Used
     for the day-to-day operations.

The split between *admin* and *dev* profiles follows the principle of *least
privilege*: regular development work never requires admin credentials. Both
variables are exported by the *Makefile* targets, so they only have to be
available in the shell environment (e.g. via `~/.aws/credentials`).

### 1. Create the backend

Run once per environment. Requires the *admin* profile.

```shell
make bootstrap-create
```

### 2. Build the GitLab Runner AMI

Run once initially, and again whenever the image scripts or pinned versions
change. Requires the *admin* profile.

```shell
make create-runner-img
```

### 3. Install a GitLab Runner

For each runner to be deployed. The script will prompt for a *runner name* and
a *runner token* (obtained from the GitLab project or group settings). Requires
the *dev* profile.

```shell
make install-gitlab-runner
```

### 4. Destroy a GitLab Runner

Removes a single runner by name. Requires the *dev* profile.

```shell
make destroy-gitlab-runner
```

### 5. Destroy the backend

The backend can not be destroyed through the *Makefile*. This is intentional —
destroying it would orphan all *TFState* files. An administrator has to remove
it manually.

### Prerequisites

The following tools must be installed locally:

- **[Terraform](https://developer.hashicorp.com/terraform/install)** (`>=1.15.3`)\
  Infrastructure-as-code tool used to provision the backend and the GitLab Runner on AWS.
- **[Packer](https://developer.hashicorp.com/packer/install)** (`>=1.10`)\
  Image builder used to create the hardened GitLab Runner AMI.
- **[Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)** (`>=2.16`)\
  Configuration management tool used to register and configure the GitLab Runner.
  Installed together with [*boto3*](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
  and [*botocore*](https://botocore.amazonaws.com/v1/documentation/api/latest/index.html),
  which are required by the `amazon.aws` and `community.aws` collections.
- **[AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)**\
  Command-line interface used to authenticate against AWS and to open SSM sessions.
- **[Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)**\
  AWS CLI plugin required by the Ansible SSM connection and for manual access to the runner.
