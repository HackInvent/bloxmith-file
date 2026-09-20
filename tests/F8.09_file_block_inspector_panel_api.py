#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies file block inspector panel API behavior.
# File Name: F8.09_file_block_inspector_panel_api.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-03-30
# -----------------------------------------------------------------------------

"""F8.09 - Modular inspector panels of the File and File Content blocks.

The test starts an isolated server, renders the `file` and `file_content`
inspector panels from their own `block.py`, checks the assets they expose, then
exercises the structured path update action. No user data is modified outside
the test server.
"""

# Test cases:
# - File/FileContent UI - Render File and FileContent inspector panels through the block API.
# - File/FileContent UI - Apply structured path/create-if-missing updates and verify node patches.
# - File/FileContent UI - Verify inspector assets are served by the block packages.

from __future__ import annotations

from urllib.parse import quote
from urllib.request import urlopen

from ui_smoke_common import expect, http_json, isolated_server
from block_test_packages import install_test_package, release_key, surface_payload


def assert_file_panel(server, kind: str, expected_hint: str) -> None:
    """Check one file block's surfaces through the installed release contract."""
    # Surfaces are release assets: a bundled kind serves none of them.
    model = install_test_package(server, kind)
    key = quote(release_key(model), safe="")
    served = lambda payload, suffix: next(
        asset["path"] for asset in payload["assets"] if asset["path"].endswith(suffix))
    node = {
        "id": f"{kind}-1",
        "kind": kind,
        "type": kind,
        "title": kind,
        "config": {"path": "exports/source.txt", "create_if_missing": True},
    }
    rendered = surface_payload(server, model, node, "inspector_panel")
    html = str(rendered.get("html") or "")
    expect("data-file-inspector-root" in html, f"Le HTML inspecteur {kind} doit venir du bloc.")
    expect("data-file-path" in html, f"Le panneau inspecteur {kind} doit contenir le champ chemin.")
    expect("data-file-apply" in html, f"Le panneau inspecteur {kind} doit exposer le bouton Appliquer.")
    expect("data-path-browser" in html, f"Le panneau inspecteur {kind} doit utiliser le path browser commun.")
    expect("data-path-browser-panel" in html, f"Le panneau inspecteur {kind} doit exposer le navigateur fichier owned par le bloc.")
    expect("exports/source.txt" in html, f"Le panneau inspecteur {kind} doit lire node.config.path.")
    expect("checked" in html, f"Le panneau inspecteur {kind} doit lire node.config.create_if_missing.")
    expect(expected_hint in html, f"Le panneau inspecteur {kind} doit afficher le hint adapté.")
    if kind == "file":
        inspector_asset_paths = ("assets/css/inspector_panel.css", "assets/js/common.js", "assets/js/inspector_panel.js")
    else:
        inspector_asset_paths = ("assets/css/inspector_panel.css", "assets/js/inspector_panel.js")

    for asset_path in inspector_asset_paths:
        with urlopen(f"{server.base_url}/api/blocks/{key}/assets/{served(rendered, asset_path)}", timeout=5) as response:
            body = response.read().decode("utf-8")
        expect("file" in body.lower(), f"Asset inspecteur {kind} non servi: {asset_path}")

    modal = surface_payload(server, model, node, "modal")
    modal_html = str(modal.get("html") or "")
    expect("data-file-modal-root" in modal_html, f"Le modal {kind} doit venir du bloc.")
    if kind == "file":
        expect("data-block-runtime-refresh=\"autonomous\"" in modal_html, f"Le modal {kind} doit gérer son refresh runtime.")
    expect("data-path-browser" in modal_html, f"Le modal {kind} doit utiliser le path browser commun.")
    expect("data-path-browser-panel" in modal_html, f"Le modal {kind} doit exposer le navigateur fichier.")
    expect("data-file-apply" in modal_html, f"Le modal {kind} doit exposer l'action fichier.")
    expect("exports/source.txt" in modal_html, f"The {kind} modal must read node.config.path.")
    # surface_payload checks that the modal serves exactly the declared assets,
    # so that it does not load the JS of another surface.
    source = server.root_dir / "exports" / "source.txt"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("source", encoding="utf-8")
    browser = http_json(server.base_url, f"/api/blocks/{kind}/browse-files?path={quote('exports/source.txt')}")
    entries = browser.get("entries") or []
    expect(
        any(entry.get("name") == "source.txt" for entry in entries),
        f"Le navigateur fichier {kind} doit etre servi par /api/blocks/{kind}/browse-files.",
    )

    applied = http_json(
        server.base_url,
        f"/api/blocks/{kind}/ui-action",
        method="POST",
        payload={
            "node": node,
            "action": "inspector_update_file",
            "values": {"path": "exports/updated.txt", "create_if_missing": False},
        },
    )
    file_patch = applied.get("node_patch", {}).get("config")
    expect(
        file_patch == {"path": "exports/updated.txt", "create_if_missing": False},
        f"The {kind} update must return the expected file patch.",
    )
    expect(applied.get("rerender_inspector") is False, f"Typing in {kind} must not force a rerender.")

    modal_applied = http_json(
        server.base_url,
        f"/api/blocks/{kind}/ui-action",
        method="POST",
        payload={
            "node": node,
            "action": "modal_update_file",
            "values": {"path": "exports/modal.txt", "create_if_missing": True},
        },
    )
    expect(
        modal_applied.get("node_patch", {}).get("config")
        == {"path": "exports/modal.txt", "create_if_missing": True},
        f"The {kind} modal update must return the expected file patch.",
    )

    card = surface_payload(server, model, node, "node_card")
    card_html = str(card.get("html") or "")
    expect("source.txt" in card_html, f"La node_card {kind} doit afficher uniquement le nom du fichier.")
    expect(">exports/source.txt<" not in card_html, f"La node_card {kind} ne doit pas afficher le chemin complet.")
    expect('title="exports/source.txt"' in card_html, f"La node_card {kind} doit conserver le chemin complet en tooltip.")


def main() -> None:
    with isolated_server() as server:
        assert_file_panel(server, "file", "The block only passes the path")
        assert_file_panel(server, "file_content", "The block reads the file as text")
    print("[ok] F8.09_file_block_inspector_panel_api")


if __name__ == "__main__":
    main()
