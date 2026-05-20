resource "aws_iam_user" "gitlab_runner" {
  name = var.username

  tags = {
    Environment = var.environment
    Project     = "tasky"
    ManagedBy   = "terraform"
  }

}

resource "aws_iam_access_key" "gitlab_runner" {
  user = aws_iam_user.gitlab_runner.name
}

resource "aws_iam_user_policy_attachment" "s3_access" {
  user       = aws_iam_user.gitlab_runner.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_user_policy_attachment" "dynamodb_access" {
  user       = aws_iam_user.gitlab_runner.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}
