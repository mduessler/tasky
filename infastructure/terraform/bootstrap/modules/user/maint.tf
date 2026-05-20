resource "aws_iam_user" "gitlab_runner" {
  name = var.username
}

resource "aws_iam_access_key" "gitlab_runner" {
  user = aws_iam_user.gitlab_runner.name
}
