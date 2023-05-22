############################################
# Local Variables
############################################

locals {
  name   = "ml-api-handson"

}

################################################################################
# IAM Role
################################################################################

resource "aws_iam_instance_profile" "codebuild" {
  name = aws_iam_role.codebuild.name
  role = aws_iam_role.codebuild.name
}

data "aws_iam_policy_document" "codebuild" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "codebuild" {
  name               = "${local.name}-codebuild"
  assume_role_policy = data.aws_iam_policy_document.codebuild.json
}

resource "aws_iam_policy" "codebuild" {
  name   = "${local.name}-codebuild"
  policy = file("./policy/codebuild_execution_policy.json")
}

resource "aws_iam_role_policy_attachment" "codebuild" {
  role       = aws_iam_role.codebuild.name
  policy_arn = aws_iam_policy.codebuild.arn
}




