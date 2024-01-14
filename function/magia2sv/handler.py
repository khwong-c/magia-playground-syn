import base64
import json

from magia import Elaborator


def handler(event, context):
    try:
        base64_encoded = event.get("isBase64Encoded", False)
        body = event.get("body", None)
        if not body:
            return {
                "statusCode": 400,
                "body": "Missing JSON request body",
            }
        if base64_encoded:
            body = base64.b64decode(body).decode("utf-8")
        body = json.loads(body)
    except Exception:
        return {
            "statusCode": 400,
            "body": "Invalid JSON request body",
        }

    code = body.get("code", None)
    top = body.get("top", None)
    if not code or not top:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "err": "Missing code or top module name",
                "sv_code": None,
            })
        }
    if not top.isidentifier():
        return {
            "statusCode": 400,
            "body": json.dumps({
                "err": "Invalid top module name",
                "sv_code": None,
            })
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

        compile(code, "<string>", "exec")
        exec(code, exec_global)

        code_elaborate = compile(f"__top_module__ = {top}(name='{top}')", "<string>", "exec")
        exec(code_elaborate, exec_global)
        top_module = exec_global["__top_module__"]
        sv_code = Elaborator.to_string(top_module)
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "err": f"Error: {e}",
                "sv_code": None,
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
                "err": None,
                "sv_code": sv_code,
            })
    }
