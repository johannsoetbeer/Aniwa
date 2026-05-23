import json
import os
import pathlib
import re
import sys
from typing import Any, cast

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

def load_config(
    file_path: str,
    env: str | None = None,
    expand_env_vars: bool = True,
) -> dict[str, Any]:
    path = pathlib.Path(file_path)

    if not path.exists():
        print(
            f"Warning: Configuration file '{file_path}' not found. Using defaults.",
            file=sys.stderr,
        )
        return {}

    suffix = path.suffix.lower()

    try:
        config_data = _read_config(path, suffix)

        return config_data

    except ValueError as exc:
        raise ValueError(f"Error parsing config file '{file_path}': {exc}")

    except Exception as exc:
        raise ValueError(f"Error parsing config file '{file_path}': {exc}")


def _read_config(path: pathlib.Path, suffix: str) -> dict[str, Any]:
    if suffix == ".json":
        with path.open(encoding="utf-8") as file:
            return cast(dict[str, Any], json.load(file) or {})

    if suffix == ".toml":
        if tomllib:
            with path.open("rb") as file:
                return cast(dict[str, Any], tomllib.load(file) or {})

        print("Error: Install 'tomli' to use TOML configs.", file=sys.stderr)
        return {}

    if suffix in [".yaml", ".yml"]:
        try:
            import yaml

            with path.open(encoding="utf-8") as file:
                return cast(dict[str, Any], yaml.safe_load(file) or {})

        except ImportError:
            print("Error: Install 'PyYAML' to use YAML configs.", file=sys.stderr)
            return {}

    return {}

def get_flattened_config(file_path: str) -> dict[str, Any]:
    raw = load_config(file_path)
    if not raw:
        return {}
        
    flattened = {}
    
    if "mode" in raw:
        if raw["mode"] not in ["fast", "deep"]:
            raise ValueError(f"Invalid mode in config: {raw['mode']}. Use 'fast' or 'deep'.")
        flattened["mode"] = raw["mode"]
        
    if "report" in raw and isinstance(raw["report"], dict):
        report = raw["report"]
        if "format" in report: flattened["report"] = report["format"]
        if "template" in report: flattened["template"] = report["template"]
        if "output_dir" in report: flattened["output"] = report["output_dir"]
        
    if "sections" in raw and isinstance(raw["sections"], dict):
        sections = raw["sections"]
        if isinstance(sections.get("include"), list):
            flattened["include"] = ",".join(sections["include"])
        if isinstance(sections.get("exclude"), list):
            flattened["exclude"] = ",".join(sections["exclude"])
            
    return flattened