resource "aws_iam_role" "runner" {
  name = "gitlab-runner-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_instance_profile" "runner" {
  name = "gitlab-runner-profile"
  role = aws_iam_role.runner.name
}
