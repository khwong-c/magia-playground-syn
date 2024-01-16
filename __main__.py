import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway
import pulumi_awsx as awsx

from pulumi.resource import ResourceOptions

stack_name = pulumi.get_stack()

# An ECR repository to store our application's container image
repo = awsx.ecr.Repository("yosys-repo", awsx.ecr.RepositoryArgs(
    force_delete=True,
))

# Build and publish our application's container image from ./app to the ECR repository
image = awsx.ecr.Image(
    "yosys-image",
    repository_url=repo.url,
    context="./function/yosys-online",
    platform="linux/amd64",
)

# An execution role to use for the Lambda function
role = aws.iam.Role(
    "role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
        }],
    }),
    managed_policy_arns=[aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE]
)

# Lambda functions to invoke
fn_magia2sv = aws.lambda_.Function(
    "magia2sv-func",
    runtime="python3.10",
    role=role.arn,
    code=pulumi.FileArchive("./function/magia2sv"),
    handler="handler.handler",
    timeout=5,
    memory_size=256,
)

fn_yosys = aws.lambda_.Function(
    "yosys-func",
    package_type="Image",
    role=role.arn,
    image_uri=image.image_uri,
    memory_size=512,
    timeout=10,
)

fn_yosys2js = aws.lambda_.Function(
    "yosys2js-func",
    runtime="nodejs18.x",
    role=role.arn,
    code=pulumi.FileArchive("./function/yosys2digital/dist"),
    handler="index.handler",
)

fn_yosys2svg = aws.lambda_.Function(
    "yosys2svg-func",
    runtime="nodejs20.x",
    role=role.arn,
    code=pulumi.FileArchive("./function/yosys2svg/dist"),
    handler="index.handler",
    timeout=5,
    memory_size=1536,
)

cors_integration = {
    "summary": "CORS support",
    "description": "Enable CORS by returning correct headers",
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "x-amazon-apigateway-integration": {
        "httpMethod": "OPTIONS",
        "type": "mock",
        "requestTemplates": {
            "application/json": "{\"statusCode\": 200}}",
        },
        "responses": {
            "default": {
                "statusCode": "200",
                "responseTemplates": "{}",
                "responseParameters": {
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD'",
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
                }
            }
        }
    },
    "responses": {
        "200": {
            "description": "Default response for CORS method",
            "headers": {
                "Access-Control-Allow-Origin": {"type": "string", },
                "Access-Control-Allow-Methods": {"type": "string", },
                "Access-Control-Allow-Headers": {"type": "string", },
            },
        }
    }
}

# A REST API to route requests to HTML content and the Lambda function
api = apigateway.RestAPI(
    "api",
    stage_name=stack_name,
    routes=[
        apigateway.RouteArgs(path="/", local_path="www/build"),
        apigateway.RouteArgs(path="/magia2sv", method=apigateway.Method.POST, event_handler=fn_magia2sv),
        apigateway.RouteArgs(path="/yosys", method=apigateway.Method.POST, event_handler=fn_yosys),
        apigateway.RouteArgs(path="/yosys2js", method=apigateway.Method.POST, event_handler=fn_yosys2js),
        apigateway.RouteArgs(path="/yosys2svg", method=apigateway.Method.POST, event_handler=fn_yosys2svg),
        # apigateway.RouteArgs(path="/", method=apigateway.Method.OPTIONS, event_handler=fn_cors),
        apigateway.RouteArgs(path="/", method=apigateway.Method.OPTIONS, data=cors_integration),
        *[
            apigateway.RouteArgs(path=p, method=apigateway.Method.OPTIONS, data=cors_integration)
            for p in ("/magia2sv", "/yosys", "/yosys2js", "/yosys2svg",)
        ],
    ],
)

api_throttle = aws.apigateway.MethodSettings(
    "api-throttle-settings",
    rest_api=api.api.id,
    stage_name=stack_name,
    method_path="*/*",
    settings={
        "throttling_burst_limit": 3,
        # Maximum number of requests that can occur in a burst
        "throttling_rate_limit": 1.0,  # Steady-state rate of requests
    }
)

# The URL at which the REST API will be served.
pulumi.export("url", api.url)


# DNS Part
# Create SSL certificate as well
def configure_dns(domain: str, zone_id: pulumi.Input):
    # SSL Cert must be created in us-east-1 unrelated to where the API is deployed.
    aws_us_east_1 = aws.Provider("aws-provider-us-east-1", region="us-east-1")
    # Request ACM certificate
    ssl_cert = aws.acm.Certificate("ssl-cert",
                                   domain_name=domain,
                                   validation_method="DNS",
                                   opts=ResourceOptions(provider=aws_us_east_1))
    # Create DNS record to prove to ACM that we own the domain
    ssl_cert_validation_dns_record = aws.route53.Record("ssl-cert-validation-dns-record",
                                                        zone_id=zone_id,
                                                        name=ssl_cert.domain_validation_options.apply(
                                                            lambda options: options[0].resource_record_name),
                                                        type=ssl_cert.domain_validation_options.apply(
                                                            lambda options: options[0].resource_record_type),
                                                        records=[ssl_cert.domain_validation_options.apply(
                                                            lambda options: options[0].resource_record_value)],
                                                        ttl=10 * 60)
    # Wait for the certificate validation to succeed
    validated_ssl_certificate = aws.acm.CertificateValidation("ssl-cert-validation",
                                                              certificate_arn=ssl_cert.arn,
                                                              validation_record_fqdns=[
                                                                  ssl_cert_validation_dns_record.fqdn],
                                                              opts=ResourceOptions(provider=aws_us_east_1))
    # Configure API Gateway to be able to use domain name & certificate
    api_domain_name = aws.apigateway.DomainName("api-domain-name",
                                                certificate_arn=validated_ssl_certificate.certificate_arn,
                                                domain_name=domain)
    # Create DNS record
    aws.route53.Record("api-dns",
                       zone_id=zone_id,
                       type="A",
                       name=domain,
                       aliases=[aws.route53.RecordAliasArgs(
                           name=api_domain_name.cloudfront_domain_name,
                           evaluate_target_health=False,
                           zone_id=api_domain_name.cloudfront_zone_id)])
    return api_domain_name


config = pulumi.Config()
domain = config.get("domain")
if domain is not None:
    # Load DNS zone for the domain
    zone = aws.route53.get_zone_output(name=config.require("dns-zone"))
    api_domain_name = configure_dns(domain, zone.zone_id)
    base_path_mapping = aws.apigateway.BasePathMapping(
        "api-domain-mapping",
        rest_api=api.api.id,
        stage_name=api.stage.stage_name,
        domain_name=api_domain_name.domain_name)

    pulumi.export(
        "public-url", base_path_mapping.domain_name.apply(lambda domain: f'https://{domain}/'))
