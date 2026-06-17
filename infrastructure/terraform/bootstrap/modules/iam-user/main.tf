resource "aws_iam_user" "this" {
  name = var.user_name
}

resource "aws_iam_policy" "this" {
  for_each = fileset(var.policies, "*.json")
  name     = "permission-${trimsuffix(each.value, ".json")}"
  policy = templatefile("${var.policies}/${each.value}", {
    account_id = var.owner_id
    region     = var.backend_location
    aws-user   = var.user_name
  })
}

# Jede Policy an den Nutzer haengen
resource "aws_iam_user_policy_attachment" "this" {
  for_each   = aws_iam_policy.this
  user       = aws_iam_user.this.name
  policy_arn = each.value.arn
}
