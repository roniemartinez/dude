import json
from pathlib import Path
from typing import Dict
from unittest import mock

import yaml
from playwright.sync_api import ElementHandle

from dude import run, select


@select(selector="li")
def feature_list(element: ElementHandle) -> Dict:
    return {"feature": element.text_content()}


@select(selector="li", url=r"example\.com")
def url_dont_match(element: ElementHandle) -> Dict:
    return {"feature": element.text_content()}


@mock.patch.object(json, "dump")
def test_json(mock_dump: mock.MagicMock):
    html = (Path(__file__).resolve().parent / "dude.html").absolute()
    run(urls=[f"file://{html}"])

    mock_dump.assert_called()


@mock.patch.object(yaml, "safe_dump")
def test_yaml(mock_safe_dump: mock.MagicMock):
    html = (Path(__file__).resolve().parent / "dude.html").absolute()
    run(urls=[f"file://{html}"], format="yaml")

    mock_safe_dump.assert_called()


@mock.patch.object(json, "dump")
def test_csv(mock_dump: mock.MagicMock):
    html = (Path(__file__).resolve().parent / "dude.html").absolute()
    run(urls=[f"file://{html}"], format="csv")  # csv is not supported in stdout, defaults to json

    mock_dump.assert_called()
