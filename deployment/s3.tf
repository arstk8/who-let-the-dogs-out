locals {
  dist_file_name = "dist.zip"
}

resource aws_s3_bucket dist_bucket {
  bucket = "releasethehounds-lambdas-dist"
}

resource aws_s3_object dist_object {
  key                    = local.dist_file_name
  bucket                 = aws_s3_bucket.dist_bucket.id
  source                 = local.dist_file_name
  server_side_encryption = "aws:kms"
  acl                    = "private"
  source_hash            = filemd5(local.dist_file_name)
}