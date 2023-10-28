variable "basename" {
  type    = string
  default = "stg-okta-slackbot"
}

variable "ImageTag" {
  type    = string
  default = "latest"
}

variable "ecrImageUri" {
  type    = string
  default = "895663540920.dkr.ecr.ap-northeast-1.amazonaws.com/stg-okta-slackbot"
}
