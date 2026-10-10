import json
from datetime import datetime, timezone

import pytest
from typer.testing import CliRunner

from cli.main import app
from core.ai import runtime
from core.ai.prompts.prompt_engine import build_prompt, load_prompt
from core.drift import detector
from core.pmm.models import ProjectMeaningModel
from core.runtime.config import load_config
from core.structure.parsers.python_parser import PythonParser
from core.structure.scanner import scan_repository
from core.vision.loader import load_vision
from core.vision.models import VisionStatus


def test_cli_help_needs_no_model_or_credentials(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Help must not install or call a model")
    monkeypatch.setattr(runtime, "run_local_prompt", forbidden)
    monkeypatch.setattr(runtime, "run_cloud_prompt", forbidden)
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert all(command in result.output for command in ["init", "check", "clarify", "finalize", "install-hook"])


def test_prompt_resources_and_payload_are_available():
    for name in ["reconcile_pmm", "populate_vision", "module_pmm", "drift_compare", "clarify_vision", "apply_clarifications"]:
        assert load_prompt(name).strip()
    prompt = build_prompt("drift_compare", {"vision": "synthetic test vision"})
    assert json.loads(prompt.split("INPUT DATA:\n", 1)[1])["vision"] == "synthetic test vision"


def test_async_functions_are_in_the_structural_graph(tmp_path):
    source = tmp_path / "service.py"
    source.write_text("import asyncio\nasync def fetch(value):\n    return await asyncio.sleep(value)\n", encoding="utf-8")
    graph = PythonParser().parse_file(source)
    symbol = next(s for s in graph.symbols if s.name == "fetch")
    assert symbol.type == "function" and symbol.parameters == ["value"]
    assert any(d.type == "calls" and d.target_id == "sleep" for d in graph.dependencies)


def test_invalid_python_does_not_crash_parser(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("def unfinished(", encoding="utf-8")
    assert PythonParser().parse_file(source).symbols == []


def test_scanner_excludes_runtime_and_environment_files_without_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    for name in [".git/hooks/hidden.py", ".driftline/cache/hidden.py", "nested/node_modules/hidden.py",
                 "nested/.venv/hidden.py", "nested/__pycache__/hidden.py", ".env", "nested/.env.local"]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def excluded(): pass\n", encoding="utf-8")
    (tmp_path / "visible.py").write_text("def visible(): pass\n", encoding="utf-8")
    graph = scan_repository()
    assert {s.name for s in graph.symbols} == {"visible.py", "visible"}


def test_custom_ignore_and_corrupt_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".driftline").mkdir()
    config = tmp_path / ".driftline/config.json"
    config.write_text('{"ignore_paths": ["generated"]}', encoding="utf-8")
    (tmp_path / "generated").mkdir()
    (tmp_path / "generated/code.py").write_text("def excluded(): pass\n", encoding="utf-8")
    assert scan_repository().symbols == []
    config.write_text('{"ignore_paths": "invalid"}', encoding="utf-8")
    assert load_config().ignore_paths == []


@pytest.mark.parametrize("content", ["", " \n\t"])
def test_blank_vision_is_not_reported_found(tmp_path, monkeypatch, content):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vision.md").write_text(content, encoding="utf-8")
    result = load_vision()
    assert result.status == VisionStatus.EMPTY and result.needs_clarification


@pytest.mark.parametrize("text", ['{"ok":true}', '```json\n{"ok":true}\n```', 'Result: {"ok":true}'])
def test_model_json_normalization(text):
    assert runtime.normalize_json_output(text) == {"ok": True}


def valid_response():
    return {"status": "aligned", "missing_vision_items": [], "new_pmm_items": [],
            "contradictions": [], "summary": "Synthetic response", "proposed_vision": "model rewrite"}


@pytest.mark.parametrize("field,value", [("status", []), ("status", "unknown"),
    ("missing_vision_items", {}), ("contradictions", None), ("summary", 7), ("proposed_vision", [])])
def test_malformed_model_fields_fail_closed(field, value):
    response = valid_response()
    response[field] = value
    checked = detector._validate_response(response, "original vision")
    assert checked["status"] == "drifted" and checked["proposed_vision"] == "original vision"


def test_alignment_preserves_vision_without_mutating_response():
    response = valid_response()
    assert detector._validate_response(response, "original")["proposed_vision"] == "original"
    assert response["proposed_vision"] == "model rewrite"


@pytest.mark.parametrize("response", [None, ["aligned"], {"status": "aligned"}])
def test_detector_rejects_missing_or_nonobject_model_output(monkeypatch, response):
    monkeypatch.setattr(detector, "run_reasoning", lambda prompt: {"text": response})
    result = detector.detect_drift("original", ProjectMeaningModel("synthetic", datetime.now(timezone.utc)))
    assert result["status"] == "drifted" and result["proposed_vision"] == "original"


def test_invalid_model_output_is_not_dumped_in_errors(monkeypatch):
    monkeypatch.setattr(runtime, "run_local_prompt", lambda prompt: ("private-output-marker", "synthetic-model"))
    with pytest.raises(RuntimeError) as error:
        runtime.run_reasoning("synthetic prompt")
    assert "private-output-marker" not in str(error.value)
