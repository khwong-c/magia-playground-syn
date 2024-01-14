import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway
import pulumi_awsx as awsx

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
)

fn_yosys = aws.lambda_.Function(
    "yosys-func",
    package_type="Image",
    role=role.arn,
    image_uri=image.image_uri,
    timeout=20,
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
)

# A REST API to route requests to HTML content and the Lambda function
api = apigateway.RestAPI(
    "api",
    stage_name=stack_name,
    routes=[
        # apigateway.RouteArgs(path="/", local_path="www"),
        apigateway.RouteArgs(path="/magia2sv", method=apigateway.Method.POST, event_handler=fn_magia2sv),
        apigateway.RouteArgs(path="/yosys", method=apigateway.Method.POST, event_handler=fn_yosys),
        apigateway.RouteArgs(path="/yosys2js", method=apigateway.Method.POST, event_handler=fn_yosys2js),
        apigateway.RouteArgs(path="/yosys2svg", method=apigateway.Method.POST, event_handler=fn_yosys2svg),
    ])


api_throttle = aws.apigateway.MethodSettings("api-throttle-settings",
    rest_api=api.api.id,
    stage_name=stack_name,
    method_path="*/*",
    settings={
        "throttling_burst_limit": 3, # Maximum number of requests that can occur in a burst
        "throttling_rate_limit": 1.0, # Steady-state rate of requests
    }
)


# The URL at which the REST API will be served.
pulumi.export("url", api.url)
