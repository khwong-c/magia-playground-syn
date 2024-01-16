import base64
import json
import random
import subprocess

from datetime import datetime
from tempfile import NamedTemporaryFile
from pathlib import Path

DEFAULT_SYNTHESIS_SCRIPT = "proc; opt -full; fsm -expand; memory -nomap; wreduce -memx optimize;"
CORS_HEADERS = {
    "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
    },
}


def handler(event, context):
    try:
        base64_encoded = event.get("isBase64Encoded", False)
        body = event.get("body", None)
        if not body:
            return {
                'statusCode': 400,
                'body': "Missing JSON request body",
                **CORS_HEADERS,
            }
        if base64_encoded:
            body = base64.b64decode(body).decode("utf-8")
        body = json.loads(body)
    except Exception:
        return {
            'statusCode': 400,
            'body': "Invalid JSON request body",
            **CORS_HEADERS,
        }

    code = body.get("code", "")
    top = body.get("top", None)

    synthesis_script = body.get("syn_script", DEFAULT_SYNTHESIS_SCRIPT)
    if "hierarchy " not in synthesis_script:
        synthesis_script = (f"hierarchy -top {top}; " if top else "hierarchy -auto-top; ") + synthesis_script
    output_file = Path("/tmp", f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(0, 1000000)}.json")

    with NamedTemporaryFile(mode="w", suffix=".sv") as f_code:
        f_code.write(code)
        f_code.flush()
        subprocess.check_output(["yosys", "-p", synthesis_script, "-o", str(output_file), f_code.name])

    return {
        'statusCode': 200,
        'body': output_file.read_text(),
        **CORS_HEADERS,
    }
