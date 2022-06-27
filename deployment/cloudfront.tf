locals {
  origin_id = "wltdo"
}

resource aws_cloudfront_distribution distribution {
  enabled = true
  aliases = ["api.releasethehoundsapp.com"]
  default_cache_behavior {
    allowed_methods          = ["GET", "HEAD"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = local.origin_id
    viewer_protocol_policy   = "https-only"
    cache_policy_id          = aws_cloudfront_cache_policy.cache_policy.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.request_policy.id
  }
  origin {
    domain_name = replace(module.websocket_api.api_endpoint, "wss://", "")
    origin_id   = local.origin_id
    origin_path = "/${module.websocket_api.stage}"
    custom_header {
      name  = "cloudfront-secret"
      value = var.cloudfront_secret
    }

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }
  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US"]
    }
  }
  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.certificate.arn
    ssl_support_method             = "sni-only"
  }
}

resource aws_cloudfront_cache_policy cache_policy {
  name        = "CachingDisabled"
  min_ttl     = 0
  max_ttl     = 0
  default_ttl = 0
  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
  }
}

resource aws_cloudfront_origin_request_policy request_policy {
  name = "websockets"
  headers_config {
    header_behavior = "whitelist"
    headers {
      items = [
        "Sec-WebSocket-Key",
        "Sec-WebSocket-Version",
        "Sec-WebSocket-Protocol",
        "Sec-WebSocket-Accept",
        "neighbor-group",
        "username"
      ]
    }
  }
  query_strings_config {
    query_string_behavior = "none"
  }
  cookies_config {
    cookie_behavior = "none"
  }
}