resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${local.environment}-alb"
  vpc_id      = module.vpc.id

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-alb"
    Environment = local.environment
  })
}

resource "aws_lb" "main" {
  name               = "${var.project_name}-${local.environment}-alb"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for subnet in flatten(values(module.vpc.subnets_routable_by_az)) : subnet.id]
  idle_timeout       = 1800

  enable_deletion_protection = false

  access_logs {
    bucket  = aws_s3_bucket.alb_access_logs.bucket
    prefix  = "alb"
    enabled = var.alb_access_logs_enabled
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-alb"
    Environment = local.environment
  })

  depends_on = [aws_s3_bucket_policy.alb_access_logs]
}


resource "aws_lb_target_group" "ui" {
  name        = "${var.project_name}-${local.environment}-ui-tg"
  port        = var.ui_port
  protocol    = "HTTP"
  vpc_id      = module.vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200,307"
    path                = "/api/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-ui-tg"
    Environment = local.environment
  })
}

resource "aws_lb_target_group" "platform" {
  name        = "${var.project_name}-${local.environment}-platform-tg"
  port        = var.platform_port
  protocol    = "HTTP"
  vpc_id      = module.vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200,307"
    path                = "/api/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-platform-tg"
    Environment = local.environment
  })
}

resource "aws_lb_target_group" "agent" {
  name        = "${var.project_name}-${local.environment}-agent-tg"
  port        = var.agent_port
  protocol    = "HTTP"
  vpc_id      = module.vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-agent-tg"
    Environment = local.environment
  })
}

resource "aws_lb_target_group" "test_executor" {
  name        = "${var.project_name}-${local.environment}-test-exec-tg"
  port        = var.test_executor_port
  protocol    = "HTTP"
  vpc_id      = module.vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(var.cigna_tags, {
    Name        = "${var.project_name}-${local.environment}-test-exec-tg"
    Environment = local.environment
  })
}

# Add ACM Certificate and Route53 entry for ALB
resource "aws_acm_certificate" "alb_cert" {
  count = local.create_acm_cert ? 1 : 0

  domain_name               = local.acm_name
  validation_method         = "DNS"
  subject_alternative_names = local.acm_alternatives
  tags                      = merge(local.merged_tags, { "Purpose" = "Cert for ECS cluster ALB" })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "alb_cert" {
  for_each = {
    for dvo in local.domain_validation_options_set : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  zone_id         = data.aws_route53_zone.private_hosted_zone_evernorth.zone_id
  ttl             = 60
  allow_overwrite = true
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
}

resource "aws_acm_certificate_validation" "alb_cert_validation" {
  count                   = local.create_acm_cert ? 1 : 0
  certificate_arn         = aws_acm_certificate.alb_cert[0].arn
  validation_record_fqdns = [for record in aws_route53_record.alb_cert : record.fqdn]
}

resource "aws_lb_listener" "web_https" {
  count = local.create_acm_cert ? 1 : 0
  
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate_validation.alb_cert_validation[0].certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }

  depends_on = [aws_acm_certificate_validation.alb_cert_validation]
}


resource "aws_lb_listener_rule" "agent" {
  count = local.create_acm_cert ? 1 : 0
  
  listener_arn = aws_lb_listener.web_https[0].arn
  priority     = 130

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.agent.arn
  }

  condition {
    host_header {
      values = ["agent.${var.project_name}-${var.environment}.${trim(data.aws_route53_zone.private_hosted_zone_evernorth.name, ".")}"]
    }
  }

  lifecycle {
    create_before_destroy = false
  }
}

resource "aws_lb_listener_rule" "test_executor" {
  count = local.create_acm_cert ? 1 : 0
  
  listener_arn = aws_lb_listener.web_https[0].arn
  priority     = 175

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.test_executor.arn
  }

  condition {
    host_header {
      values = ["test-executor.${var.project_name}-${var.environment}.${trim(data.aws_route53_zone.private_hosted_zone_evernorth.name, ".")}"]
    }
  }
}



resource "aws_lb_listener_rule" "ui" {
  count = local.create_acm_cert ? 1 : 0
  
  listener_arn = aws_lb_listener.web_https[0].arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }

  condition {
    host_header {
      # UI served at root of the project-env domain (no subdomain)
      values = ["${var.project_name}-${var.environment}.${trim(data.aws_route53_zone.private_hosted_zone_evernorth.name, ".")}"]
    }
  }
}

resource "aws_lb_listener_rule" "platform" {
  count = local.create_acm_cert ? 1 : 0

  listener_arn = aws_lb_listener.web_https[0].arn
  priority     = 150

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.platform.arn
  }

  condition {
    host_header {
      values = ["platform.${var.project_name}-${var.environment}.${trim(data.aws_route53_zone.private_hosted_zone_evernorth.name, ".")}"]
    }
  }
}
