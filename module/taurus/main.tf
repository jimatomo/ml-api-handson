############################################
# Local Variables
############################################

locals {
  name   = "ml-api-handson"
  
  private_key_file = "~/${local.name}.pem"

  tags = {
    terraform_project = local.name
  }
}

################################################################################
# IAM Role
################################################################################

resource "aws_iam_instance_profile" "ec2_dev" {
  name = aws_iam_role.ec2_dev.name
  role = aws_iam_role.ec2_dev.name
}

data "aws_iam_policy_document" "ec2_dev" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ec2_dev" {
  name               = "${local.name}-ec2-dev"
  assume_role_policy = data.aws_iam_policy_document.ec2_dev.json
}

resource "aws_iam_role_policy_attachment" "ec2_dev" {
  role       = aws_iam_role.ec2_dev.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}


################################################################################
# Key Pair
################################################################################

# 秘密鍵のアルゴリズム設定
resource "tls_private_key" "ec2_key" {
  algorithm = "ED25519"
}


# store private key
resource "local_file" "ec2_key_pem" {
  filename = "${local.private_key_file}"
  content  = "${tls_private_key.ec2_key.private_key_pem}"
}

# Import public key to AWS EC2 Key Pair
resource "aws_key_pair" "ec2_key_keypair" {
  key_name   = local.name
  public_key = "${tls_private_key.ec2_key.public_key_openssh}"
}


################################################################################
# Key Pair
################################################################################

resource "aws_security_group" "dev_ec2" {
  name        = local.name
  description = "Dev EC2 SG"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.tags,
    {
      Name = local.name
    }
  )
}


################################################################################
# EC2 Instance
################################################################################

# Ubuntu 20.04 AMI Latest
data "aws_ami" "ubuntu_20_04" {
  most_recent = true
  owners = ["099720109477"]

  filter {
    name = "architecture"
    values = ["x86_64"]
  }

  filter {
    name = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name = "block-device-mapping.volume-type"
    values = ["gp2"]
  }

  filter {
    name = "state"
    values = ["available"]
  }
}

# EC2作成
resource "aws_instance" "dev_ec2"{
  ami                    = data.aws_ami.ubuntu_20_04.id
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.dev_ec2.id]
  subnet_id              = var.ec2_subnet_id
  key_name               = aws_key_pair.ec2_key_keypair.key_name
  iam_instance_profile   = aws_iam_instance_profile.ec2_dev.name
  
  tags = merge(
    local.tags,
    {
      Name = local.name
    }
  )
}
