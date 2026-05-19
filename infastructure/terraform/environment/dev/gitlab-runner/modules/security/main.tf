resource "aws_iam_role" "gitlab_runner" {
  name = "gitlab-runner-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_instance_profile" "gitlab_runner" {
  name = "gitlab-runner-profile-${var.environment}"
  role = aws_iam_role.gitlab_runner.name
}
