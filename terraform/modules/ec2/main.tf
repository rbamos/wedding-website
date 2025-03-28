resource "aws_security_group" "ec2_sg" {
  name        = var.security_group_name
  description = "Allow HTTPS and SSH inbound traffic"
  vpc_id      = var.vpc_id

  # Allow HTTPS inbound traffic
  ingress {
    description = "Allow HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP inbound traffic
  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP inbound traffic
  ingress {
    description = "Allow django HTTP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH inbound traffic
  ingress {
    description = "Allow SSH from home IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.access_ip] # Dynamically assign your home IP
  }

  # Allow ICMP (Ping) inbound traffic
  ingress {
    description = "Allow ICMP (Ping)"
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "django_server" {
  ami           = var.ami_id
  instance_type = var.instance_type

  # Use the security group ID instead of VPC ID
  vpc_security_group_ids = [
    aws_security_group.ec2_sg.id
  ]

  key_name = "aws_access_key"

  subnet_id = var.subnet_id

  tags = {
    Name = var.instance_name
  }

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  user_data = templatefile("${path.module}/user_data.sh.tftpl", { environment_secrets = var.environment_secrets })
}

# IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name               = "ec2-role"
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect : "Allow",
        Principal : {
          Service : "ec2.amazonaws.com"
        },
        Action : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_policy" "secrets_manager_read_policy" {
  name        = "SecretsManagerReadPolicy"
  description = "Policy to allow EC2 instance to read specific Secrets Manager secret"
  policy      = jsonencode({
    Version   = "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : "secretsmanager:GetSecretValue",
        Resource : var.environment_secrets_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets_manager" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.secrets_manager_read_policy.arn
}

resource "aws_iam_policy" "gallery_bucket_policy" {
  name        = "GalleryBucketAccessPolicy"
  description = "Policy to allow EC2 instance read/write access to gallery bucket"
  policy      = jsonencode({
    Version   = "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource : [
          "arn:aws:s3:::${var.gallery_bucket}",
          "arn:aws:s3:::${var.gallery_bucket}/*",
          "arn:aws:s3:::${var.sqlite_backup_bucket}",
          "arn:aws:s3:::${var.sqlite_backup_bucket}/*"
        ]
      },
      {
        Effect   : "Allow",
        Action   : [
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource : [
          "arn:aws:s3:::${var.gallery_bucket}/*",
          "arn:aws:s3:::${var.sqlite_backup_bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_gallery_bucket" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.gallery_bucket_policy.arn
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.ec2_role.name
}

# Even if it's not needed, we still make the SQLite backup bucket anyways
# Since S3 buckets don't cost anything to own
resource "aws_s3_bucket" "sqlite_backup_bucket" {
  bucket = var.sqlite_backup_bucket
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.sqlite_backup_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  bucket = aws_s3_bucket.sqlite_backup_bucket.id

  rule {
    id     = "expire-older-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}