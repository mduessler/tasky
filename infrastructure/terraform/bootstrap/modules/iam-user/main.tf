resource "aws_iam_user" "this" {
  name = var.user_name
}

resource "aws_iam_policy" "this" {
  for_each = fileset(var.policies, "*.json")
  name     = var.user_name
  policy = templatefile("${var.policies}/${each.value}", {
    account_id = var.owner_id
    region     = var.aws_region
  })
}

# Jede Policy an den Nutzer haengen
resource "aws_iam_user_policy_attachment" "this" {
  for_each   = aws_iam_policy.this
  user       = aws_iam_user.this.name
  policy_arn = each.value.arn
}
