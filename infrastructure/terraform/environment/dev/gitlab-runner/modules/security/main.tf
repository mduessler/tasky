resource "aws_iam_role" "gitlab_runner" {
  name = "tasky-gitlab-runner-role-${var.environment}-${var.runner_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Environment = var.environment
    Project     = "tasky"
    ManagedBy   = "terraform"
  }
}

resource "aws_iam_instance_profile" "gitlab_runner" {
  name = "tasky-gitlab-runner-profile-${var.environment}-${var.runner_name}"
  role = aws_iam_role.gitlab_runner.name
}

locals {
  runner_policies = [
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
  ]
}

resource "aws_iam_role_policy_attachment" "runner" {
  for_each   = toset(local.runner_policies)
  role       = aws_iam_role.gitlab_runner.name
  policy_arn = each.value
}

data "aws_iam_policy_document" "ssm_bucket_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
      "s3:GetBucketLocation",
    ]
    resources = [
      var.ssm_bucket_arn,
      "${var.ssm_bucket_arn}/*",
    ]
  }
}

resource "aws_iam_role_policy" "ssm_bucket_access" {
  name   = "ssm-bucket-access"
  role   = aws_iam_role.gitlab_runner.id
  policy = data.aws_iam_policy_document.ssm_bucket_access.json
}
