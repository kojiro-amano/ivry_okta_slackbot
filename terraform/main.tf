terraform {
  required_version = ">=1.2.6"
  backend "s3" {
    bucket         = "stg-okta-slackbot-terraform-state"
    key            = "terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "stg-okta-slackbot-terraform-lock"
  }
}

provider "aws" {
  region  = "ap-northeast-1"
  version = "~>5.17.0"
}

# resource "aws_ecr_repogitory" "slackbot-repo" {
#   name                 = var.basename
#   iamge_tag_mutability = "MUTABLE"
# }


################################################################################
# Lambda                                                                       #
################################################################################

resource "aws_lambda_function" "slackbot-lambda" {
  function_name = var.basename
  image_uri     = "${var.ecrImageUri}:${var.ImageTag}"
  role          = aws_iam_role.slackbot-lambda.arn
  package_type  = "Image"
  publish       = true

  memory_size = 128

}

resource "aws_lambda_function_url" "slackbot-lambda-url" {
  function_name = aws_lambda_function.slackbot-lambda.function_name

  # slackのchallenge認証(https://api.slack.com/events/url_verification)にて認証するため、不要
  authorization_type = "NONE"
}

# resource "aws_lambda_alias" "slackbot-lambda" {
#   name             = "STG"
#   function_name    = aws_lambda_function.slackbot-lambda.arn
#   function_version = aws_lambda_function.slackbot-lambda.version

#   lifecycle {
#     ignore_changes = [function_version]
#   }
# }


################################################################################
# IAM Role for Lambda                                                          #
################################################################################


resource "aws_iam_role" "slackbot-lambda" {
  name               = var.basename
  assume_role_policy = data.aws_iam_policy_document.slackbot-lambda-assume-role.json
}

data "aws_iam_policy_document" "slackbot-lambda-assume-role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role_policy_attachment" "slackbot-lambda" {
  role       = aws_iam_role.slackbot-lambda.name
  policy_arn = aws_iam_policy.slackbot-lambda.arn
}

resource "aws_iam_policy" "slackbot-lambda" {
  name   = var.basename
  policy = data.aws_iam_policy_document.slackbot-lambda.json
}

data "aws_iam_policy_document" "slackbot-lambda" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "*",
    ]
  }
}

################################################################################
# CloudWatch Logs                                                              #
################################################################################
resource "aws_cloudwatch_log_group" "lambda_getemployee" {
  name              = "/aws/lambda/${aws_lambda_function.slackbot-lambda.function_name}"
  retention_in_days = 30
}
