import json
import sys
from pathlib import Path

file_path = Path(sys.argv[1])
openapi_content = json.loads(file_path.read_text(encoding="utf-8"))

if "/healthz" in openapi_content["paths"]:
    del openapi_content["paths"]["/healthz"]

for component_name, component_desc in openapi_content["components"]["schemas"].items():
    # Remove "events" field across the board.
    if "required" in component_desc:
        component_desc["required"] = [f for f in component_desc["required"] if f != "events"]
    if "properties" in component_desc:
        component_desc["properties"] = {fk: fv for fk, fv in component_desc["properties"].items() if fk != "events"}

file_path.write_text(json.dumps(openapi_content), encoding="utf-8")
