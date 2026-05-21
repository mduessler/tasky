# Bootstrap Documentation

This document gives and overview, usage, and an explanation about design choices
done in the backend of this project. The backend has to be initialized only once.
A backend was implemented, to store the *Terraform state (TFstate)* of the
infrastructure remote. Like this all developers can use the same *TFstate*. The
backend also stored its own *TFstate* remote.

## Initialization

To initialize the backend simple run from the root of the project the command
`make terraform-init-bootstrap`. This command does multiple things:

1. **Change Working directory** — At first the command changes the working directory
   to the directory [infrastructure/terraform/bootstrap](../../infrastructure/terraform/bootstrap).
   In this directory is the configuration of the backend stored.
2. **Initialize Working directory** to prepare the configuration files.
3. **Apply the infrastructure** to create the backend on the remote system.
4. **Add state of the backend** — To add the *TFstate* of the backend itself.
   The backend has to call `terraform init -migrate-state` to upload the created
   *TFstate*.

## File structure

The next graph represents the file structure of the backend. It also displays modules
not located in the backend, which are needed for the configuration.

```shell
├── bootstrap
│   ├── main.tf
│   ├── modules
│   │   ├── dynamo_db
│   │   │   ├── main.tf
│   │   │   ├── output.tf
│   │   │   └── variables.tf
│   │   └── logging
│   │       ├── main.tf
│   │       ├── output.tf
│   │       └── variables.tf
│   ├── output.tf
│   ├── provider.tf
│   └── variables.tf
└── modules
    ├── s3_bucket
    │   ├── main.tf
    │   ├── output.tf
    │   └── variables.tf
    └── s3_security
        ├── main.tf
        └── variables.tf
```

## Overview

The backend consists of two [*Simple Storage Service *S3**](https://aws.amazon.com/s3/)
buckets. The purpose of the two buckets is:

1. **State-Bucket-Dev** — Store the *TFState* for the dev environment
2. **Log-Bucket** — Log the access on the bucket of *State-Bucket-Dev* storage.

Furthermore a [*DynamoDB*](https://aws.amazon.com/dynamodb/) is used, to store locks.
A *DynamoDB* is a fully manged, NoSQL database. The locks ensure that no two developers
can write to a TFState at the same time
