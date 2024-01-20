import base64
import json
import traceback
import sys


CORS_HEADERS = {
    "headers": {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
    },
}

original_modules = set(sys.modules.keys())


def handler(event, context):
    try:
        base64_encoded = event.get("isBase64Encoded", False)
        body = event.get("body", None)
        if not body:
            return {
                "statusCode": 400,
                "body": "Missing JSON request body",
                **CORS_HEADERS,
            }
        if base64_encoded:
            body = base64.b64decode(body).decode("utf-8")
        body = json.loads(body)
    except Exception:
        return {
            "statusCode": 400,
            "body": "Invalid JSON request body",
            **CORS_HEADERS,
        }

    code = body.get("code", None)
    top = body.get("top", None)
    if not code or not top:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "err": "Missing code or top module name",
                "sv_code": None,
            }),
            **CORS_HEADERS,
        }
    if not top.isidentifier():
        return {
            "statusCode": 400,
            "body": json.dumps({
                "err": "Invalid top module name",
                "sv_code": None,
            }),
            **CORS_HEADERS,
        }

    try:
        # Restrict importing high risk modules
        exec_global = {k: v for k, v in globals().items()}
        exec_builtins = {k: v for k, v in globals()["__builtins__"].items()}

        org_import = __import__

        def wrapped_import(*args, **kwargs):
            if args[0] in ("time", "os", "boto3", "subprocess", "sh", "awscli", "awscli.clidriver"):
                raise ImportError(f"No module named {args[0]}")
            return org_import(*args, **kwargs)

        exec_builtins["__import__"] = wrapped_import
        exec_global["__builtins__"] = exec_builtins

        compile(code, "<code>", "exec")
        exec(code, exec_global)

        code_elaborate = compile(f"__top_module__ = {top}(name='{top}')", "<elaborator>", "exec")
        exec(code_elaborate, exec_global)
        top_module = exec_global["__top_module__"]

        from magia import Elaborator
        sv_code = Elaborator.to_string(top_module)
        new_modules = [m for m in sys.modules.keys() if m not in original_modules]
        for m in new_modules:
            sys.modules.pop(m)

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "err": "\n".join(["Error during Elaboration", str(e), *traceback.format_tb(e.__traceback__)]),
                "sv_code": None,
            }),
            **CORS_HEADERS,
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "err": None,
            "sv_code": sv_code,
        }),
        **CORS_HEADERS,
    }
