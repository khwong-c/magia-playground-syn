import base64
import json
import random
import subprocess

from datetime import datetime
from tempfile import NamedTemporaryFile
from pathlib import Path

DEFAULT_SYNTHESIS_SCRIPT = "hierarchy -auto-top; proc; opt -full; fsm -expand; memory -nomap; wreduce -memx optimize;"


def handler(event, context):
    try:
        base64_encoded = event.get("isBase64Encoded", False)
        body = event.get("body", None)
        if not body:
            return {
                'statusCode': 400,
                'body': "Missing JSON request body",
            }
        if base64_encoded:
            body = base64.b64decode(body).decode("utf-8")
        body = json.loads(body)
    except Exception:
        return {
            'statusCode': 400,
            'body': "Invalid JSON request body",
        }

    code = body.get("code", "")
    synthesis_script = body.get("syn_script", DEFAULT_SYNTHESIS_SCRIPT)
    output_file = Path("/tmp", f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(0, 1000000)}.json")

    with NamedTemporaryFile(mode="w", suffix=".sv") as f_code:
        f_code.write(code)
        f_code.flush()
        subprocess.check_output(["yosys", "-p", synthesis_script, "-o", str(output_file), f_code.name])

    return {
        'statusCode': 200,
        'body': output_file.read_text(),
    }
