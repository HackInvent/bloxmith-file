#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies file block inspector panel API behavior.
# File Name: F8.09_file_block_inspector_panel_api.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-03-30
# -----------------------------------------------------------------------------

"""F8.09 - UI modulaire des panneaux inspecteur File et File Content.

Le test démarre un serveur isolé, demande le rendu des panneaux inspecteur
`file` et `file_content` depuis leurs `block.py`, vérifie les assets exposés,
puis teste l'action structurée de mise à jour du chemin. Aucune donnée
utilisateur n'est modifiée hors du serveur de test.
"""

# Test cases:
# - File/FileContent UI - Render File and FileContent inspector panels through the block API.
# - File/FileContent UI - Apply structured path/create-if-missing updates and verify node patches.
# - File/FileContent UI - Verify inspector assets are served by the block packages.

from __future__ import annotations

from urllib.parse import quote
from urllib.request import urlopen

from ui_smoke_common import expect, http_json, isolated_server


def assert_file_panel(server, kind: str, expected_hint: str) -> None:
    node = {
        "id": f"{kind}-1",
        "kind": kind,
        "type": kind,
        "title": kind,
        "config": {"path": "exports/source.txt", "create_if_missing": True},
    }
    rendered = http_json(server.base_url, f"/api/blocks/{kind}/inspector-panel", method="POST", payload={"node": node})
    html = str(rendered.get("html") or "")
    expect("data-file-inspector-root" in html, f"Le HTML inspecteur {kind} doit venir du bloc.")
    expect("data-file-path" in html, f"Le panneau inspecteur {kind} doit contenir le champ chemin.")
    expect("data-file-apply" in html, f"Le panneau inspecteur {kind} doit exposer le bouton Appliquer.")
    expect("data-path-browser" in html, f"Le panneau inspecteur {kind} doit utiliser le path browser commun.")
    expect("data-path-browser-panel" in html, f"Le panneau inspecteur {kind} doit exposer le navigateur fichier owned par le bloc.")
    expect("exports/source.txt" in html, f"Le panneau inspecteur {kind} doit lire node.config.path.")
    expect("checked" in html, f"Le panneau inspecteur {kind} doit lire node.config.create_if_missing.")
    expect(expected_hint in html, f"Le panneau inspecteur {kind} doit afficher le hint adapté.")
    assets = rendered.get("assets") or []
    expect(
        {"kind": "css", "path": "assets/css/inspector_panel.css"} in assets,
        f"Le CSS inspecteur {kind} doit être déclaré par le bloc.",
    )
    if kind == "file":
        expect(
            {"kind": "js", "path": "assets/js/common.js"} in assets,
            f"Le JS commun inspecteur {kind} doit être déclaré par le bloc.",
        )
        inspector_asset_paths = ("assets/css/inspector_panel.css", "assets/js/common.js", "assets/js/inspector_panel.js")
    else:
        inspector_asset_paths = ("assets/css/inspector_panel.css", "assets/js/inspector_panel.js")
    expect(
        {"kind": "js", "path": "assets/js/inspector_panel.js"} in assets,
        f"Le JS inspecteur {kind} doit être déclaré par le bloc.",
    )

    for asset_path in inspector_asset_paths:
        with urlopen(f"{server.base_url}/api/blocks/{kind}/assets/{asset_path}", timeout=5) as response:
            body = response.read().decode("utf-8")
        expect("file" in body.lower(), f"Asset inspecteur {kind} non servi: {asset_path}")

    modal = http_json(server.base_url, f"/api/blocks/{kind}/modal", method="POST", payload={"node": node, "runtime": {}})
    modal_html = str(modal.get("html") or "")
    expect("data-file-modal-root" in modal_html, f"Le modal {kind} doit venir du bloc.")
    if kind == "file":
        expect("data-block-runtime-refresh=\"autonomous\"" in modal_html, f"Le modal {kind} doit gérer son refresh runtime.")
    expect("data-path-browser" in modal_html, f"Le modal {kind} doit utiliser le path browser commun.")
    expect("data-path-browser-panel" in modal_html, f"Le modal {kind} doit exposer le navigateur fichier.")
    expect("data-file-apply" in modal_html, f"Le modal {kind} doit exposer l'action fichier.")
    expect("exports/source.txt" in modal_html, f"Le modal {kind} doit lire node.config.path.")
    modal_assets = modal.get("assets") or []
    expect(
        {"kind": "css", "path": "assets/css/inspector_panel.css"} in modal_assets,
        f"Le CSS modal {kind} doit être déclaré par le bloc.",
    )
    if kind == "file":
        expect(
            {"kind": "js", "path": "assets/js/common.js"} in modal_assets,
            f"Le JS commun modal {kind} doit être déclaré par le bloc.",
        )
        expect(
            {"kind": "js", "path": "assets/js/block_modal.js"} in modal_assets,
            f"Le JS modal {kind} doit être déclaré par le bloc.",
        )
        expect(
            {"kind": "js", "path": "assets/js/inspector_panel.js"} not in modal_assets,
            f"Le modal {kind} ne doit pas charger le JS inspecteur.",
        )
    else:
        expect(
            {"kind": "js", "path": "assets/js/inspector_panel.js"} in modal_assets,
            f"Le JS modal {kind} doit être déclaré par le bloc.",
        )

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
        f"La mise à jour {kind} doit renvoyer le patch file attendu.",
    )
    expect(applied.get("rerender_inspector") is False, f"La saisie {kind} ne doit pas forcer un rerender.")

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
        f"La mise à jour modale {kind} doit renvoyer le patch file attendu.",
    )

    card = http_json(server.base_url, f"/api/blocks/{kind}/node-card", method="POST", payload={"node": node})
    card_html = str(card.get("html") or "")
    expect("source.txt" in card_html, f"La node_card {kind} doit afficher uniquement le nom du fichier.")
    expect(">exports/source.txt<" not in card_html, f"La node_card {kind} ne doit pas afficher le chemin complet.")
    expect('title="exports/source.txt"' in card_html, f"La node_card {kind} doit conserver le chemin complet en tooltip.")


def main() -> None:
    with isolated_server() as server:
        assert_file_panel(server, "file", "Le bloc transmet uniquement le chemin")
        assert_file_panel(server, "file_content", "Le bloc lit le fichier comme du texte")
    print("[ok] F8.09_file_block_inspector_panel_api")


if __name__ == "__main__":
    main()
