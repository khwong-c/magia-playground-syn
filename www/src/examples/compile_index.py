#!/usr/bin/env python3
import json
from pathlib import Path

if __name__ == "__main__":
    # Get current directory
    current_dir = Path(__file__).parent
    compile_index_name = Path(__file__).name

    # Read all examples, excluding current file
    examples = {
        path.stem: path.read_text()
        for path in current_dir.glob("*.py")
        if path.name != compile_index_name
    }

    # Write to json
    Path(current_dir, "magiaExamples.json").write_text(
        json.dumps(examples, indent=2, sort_keys=True)
    )
