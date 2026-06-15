data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}


# Controller role
resource "aws_iam_role" "controller" {
  name               = "kube-controller-role"
  assume_role_policy = data.data.aws_iam_policy_document.assume_role.json.assume_role.json
}

resource "aws_iam_role_policy_attachment" "controller_ssm" {
  role       = aws_iam_role.controller.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "controller_ccm" {
  name   = "control-plane-policy"
  role   = aws_iam_role.controller.id
  policy = file("${path.module}/control-plane-policy.json")
}

resource "aws_iam_instance_profile" "controller" {
  name = "kube-controller-profile"
  role = aws_iam_role.controller.name
}

# Worker role
resource "aws_iam_role" "worker" {
  name               = "kube-worker-role"
  assume_role_policy = data.data.aws_iam_policy_document.assume_role.json.assume_role.json
}

resource "aws_iam_role_policy_attachment" "worker_ssm" {
  role       = aws_iam_role.worker.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "worker_node" {
  name   = "node-policy"
  role   = aws_iam_role.worker.id
  policy = file("${path.module}/node-policy.json")
}

resource "aws_iam_instance_profile" "worker" {
  name = "kube-worker-profile"
  role = aws_iam_role.worker.name
}
