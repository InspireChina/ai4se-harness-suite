"""读取预设图与覆盖文件。"""

from __future__ import annotations

import os
from typing import Any
from typing import Optional

from .errors import GraphError
from .yaml_lite import YamlError
from .yaml_lite import loads

PRESET_NAME = "iteration-to-test.yaml"


def package_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def preset_path() -> str:
    return os.path.join(package_root(), "presets", PRESET_NAME)


def load_yaml(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        raise GraphError("读不到图文件 %s：%s" % (path, exc)) from exc
    try:
        data = loads(text)
    except YamlError as exc:
        raise GraphError("图文件 %s 不是合法 YAML：%s" % (path, exc)) from exc
    if not isinstance(data, dict):
        raise GraphError("图文件 %s 的根必须是映射" % path)
    return data


def load_preset() -> dict:
    return load_yaml(preset_path())


def load_overlay(project: str) -> Optional[dict]:
    path = os.path.join(project, ".agents", "workflow", "overlay.yaml")
    if not os.path.isfile(path):
        return None
    return load_yaml(path)
