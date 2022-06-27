resource aws_acm_certificate certificate {
  domain_name               = "releasethehoundsapp.com"
  subject_alternative_names = [
    "*.releasethehoundsapp.com"
  ]
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

data aws_route53_zone zone {
  name = "releasethehoundsapp.com"
}

resource aws_route53_record acm_validation_cname {
  zone_id = data.aws_route53_zone.zone.id
  name    = "_f98aa493ff4e01989ee0e7213ac87494.releasethehoundsapp.com."
  type    = "CNAME"
  ttl     = 300
  records = ["_d562ee9e238e39aa7ee550a5663fd245.hqkbcmchgw.acm-validations.aws."]
}

resource aws_route53_record api_cloudfront {
  name    = "api.releasethehoundsapp.com"
  type    = "A"
  zone_id = data.aws_route53_zone.zone.id

  alias {
    evaluate_target_health = false
    name                   = aws_cloudfront_distribution.distribution.domain_name
    zone_id                = aws_cloudfront_distribution.distribution.hosted_zone_id
  }
}