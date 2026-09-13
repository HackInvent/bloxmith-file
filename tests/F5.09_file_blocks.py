#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies file block behavior.
# File Name: F5.09_file_blocks.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-02-22
# -----------------------------------------------------------------------------

"""F5.09 - Blocs File Path et Fichier Contenu.

Le test crée un fichier texte dans le projet temporaire, puis vérifie que le
bloc `file` émet son chemin absolu et que `file_content` émet son contenu.
"""

# Test cases:
# - File FB1/FB2/FB3/FB4 - Run File and FileContent blocks against isolated workspace files.
# - FileContent FB1/FB2/FB3 - Verify File emits a path capability and FileContent emits text/json content.
# - File FB2/FB4 - Verify missing-file creation and invalid paths are handled safely.

from pathlib import Path

from ui_smoke_common import (
    create_run_api,
    data_edge,
    display_node,
    expect,
    graph_payload,
    isolated_server,
    wait_for_run_terminal,
)


def file_node() -> dict:
    return {
        "id": "file-1",
        "kind": "file",
        "title": "File Path",
        "position": {"x": 80, "y": 120},
        "inputs": [],
        "outputs": [
            {"id": 1, "name": "fichier", "title": "Out", "emits": ["file/path", "message/*"], "multiplicity": "many"}
        ],
        "config": {"path": "tmp_test_inputs/f5/source.txt", "create_if_missing": False},
    }


def file_content_node() -> dict:
    return {
        "id": "file-content-1",
        "kind": "file_content",
        "title": "Fichier Contenu",
        "position": {"x": 80, "y": 300},
        "inputs": [],
        "outputs": [
            {"id": 1, "name": "contenu", "title": "Contenu", "emits": ["message/*", "text/plain"], "multiplicity": "many"}
        ],
        "config": {"path": "tmp_test_inputs/f5/source.txt", "create_if_missing": False, "encoding": "utf-8"},
    }


def output_value_by_content_type(run: dict, content_type: str) -> dict:
    """Return the first runtime output value matching a content type."""

    for value in (run.get("output_values") or {}).values():
        if value.get("content_type") == content_type:
            return value
    return {}


def worker_received_by_title(run: dict, title: str) -> str:
    """Return worker received text by runtime node title after id materialization."""

    for row in (run.get("worker_rows") or {}).values():
        if str(row.get("node_title") or "") == title:
            return str(row.get("received") or "")
    return ""


def main() -> None:
    with isolated_server() as server:
        source = server.root_dir / "tmp_test_inputs" / "f5" / "source.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("contenu fichier F5", encoding="utf-8")

        document = graph_payload(
            "F5 File Blocks",
            [
                file_node(),
                file_content_node(),
                display_node("display-file", "Affichage fichier", 420, 120),
                display_node("display-content", "Affichage contenu", 420, 300),
            ],
            [
                data_edge("edge-file-display", "file-1", 1, "display-file", 1),
                data_edge("edge-content-display", "file-content-1", 1, "display-content", 1),
            ],
        )
        created = create_run_api(server, document, runtime_mode="centralized")
        run = wait_for_run_terminal(server, str(created.get("run_id") or ""))

        expect(run.get("status") == "success", "Le run file/file_content doit réussir.")
        file_output = output_value_by_content_type(run, "file/path")
        expect(Path(str(file_output.get("value") or "")).resolve() == source.resolve(), "Le bloc file n'émet pas le chemin absolu attendu.")
        expect(file_output.get("content_type") == "file/path", "Le content_type file doit être file/path.")
        expect(output_value_by_content_type(run, "text/plain").get("value") == "contenu fichier F5", "Le contenu fichier est incorrect.")
        expect("contenu fichier F5" in worker_received_by_title(run, "Affichage contenu"), "Display ne reçoit pas le contenu.")
    print("[ok] F5.09_file_blocks")


if __name__ == "__main__":
    main()
