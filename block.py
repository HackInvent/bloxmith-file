# -----------------------------------------------------------------------------
# Role: Implements the file block runtime and UI contract.
# File Name: block.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-01-16
# -----------------------------------------------------------------------------

from __future__ import annotations

from html import escape
from typing import Any

from bloxsmith_app.block_api import (
    BlockDefinition,
    BlockRuntimeContext,
    BlockRuntimeOutput,
    BlockRuntimeResult,
    FileBlockError,
    FilePathBlockMixin,
    FILE_PATH,
    render_node_card_template,
)


# Functional behavior:
# FB1 - Resolve a configured workspace-relative or absolute file path at runtime.
# FB2 - Optionally create a missing file when configured.
# FB3 - Emit the resolved path as a file/path capability.
# FB4 - Fail with explicit diagnostics for unsafe, missing, directory, or invalid paths.
class FileBlock(FilePathBlockMixin, BlockDefinition):
    """Autonomous block implementation for `FileBlock`."""
    kind = "file"

    def render_modal(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the File Path modal with the shared path browser control."""

        config = self._ui_file_config(node)
        template = (self.directory / "block_modal.html").read_text(encoding="utf-8")
        html = self._render_generic_modal_template(
            template=(
                template
                .replace("{{ path_browser_html }}", self._render_file_path_browser(config, input_id="fileModalPathInput"))
                .replace("{{ checked }}", "checked" if config.get("create_if_missing") else "")
                .replace("{{ hint }}", escape(self._ui_hint()))
                .replace("{{ config_fields_html }}", self._render_modal_technical_config_fields(node))
            ),
            node=node,
            payload=payload or {},
        )
        return {
            "html": html,
            "context": {
                "node_id": str(node.get("id") or ""),
                "node_kind": self.kind,
                "path": str(config.get("path") or ""),
                "create_if_missing": bool(config.get("create_if_missing")),
            },
        }

    def render_node_card(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the File canvas card body from the block-owned template.

        Args:
            node: Serialized file node whose config contains the source path.
            payload: Optional server/UI rendering payload.

        Returns:
            Block UI payload used by the generic canvas shell.
        """

        if self.kind != "file":
            raise NotImplementedError(f"Block '{self.kind}' does not implement render_node_card().")
        config = self._ui_file_config(node)
        path = str(config.get("path") or self.translate("block.file.no_path", fallback="No path"))
        display_name = self._file_display_name(path)
        # The card states one of two modes, so the marker carries the matching key.
        mode_key = ("block.file.mode_created_if_missing" if config.get("create_if_missing")
                    else "block.file.mode_must_exist")
        mode = self.translate(mode_key, fallback="created if missing" if config.get("create_if_missing") else "must exist")
        return render_node_card_template(
            block=self,
            node=node,
            node_classes=["file-node"],
            replacements={
                "title": node.get("title") or self.default_title(),
                "path": escape(path),
                "path_label": escape(display_name),
                "mode": mode,
                "mode_key": mode_key,
            },
        )

    def handle_ui_action(
        self,
        *,
        node: dict[str, Any],
        action: str,
        values: dict[str, Any],
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle a block-owned UI action and return the updated node payload.

        Args:
            node: Serialized graph node handled by the block.
            action: Block-owned action name requested by the frontend.
            values: Values value used by this block helper.
            payload: Optional UI or runtime payload provided by the framework.
        """
        if action not in {"inspector_update_file", "modal_update_file"}:
            return super().handle_ui_action(node=node, action=action, values=values, payload=payload)
        return self._apply_file_ui_update(values)

    def _ui_hint(self) -> str:
        """Provide internal FileBlock behavior for `_ui_hint`."""
        return self.translate(
            "block.file.hint",
            fallback=("The block only passes the path to the Codex block. "
                      "When the option is checked, a missing file is created empty."),
        )

    def preview_received(self, *, node: Any, **runtime_services: Any) -> str:
        """Return a compact preview value for runtime display surfaces.

        Args:
            node: Serialized graph node handled by the block.
            runtime_services: Runtime services value used by this block helper.
        """
        config = getattr(node, "config", {}) if isinstance(getattr(node, "config", {}), dict) else {}
        return self.configured_path_label(config)

    def execute_runtime(self, context: BlockRuntimeContext) -> BlockRuntimeResult:
        """Execute the block through the generic runtime context and return runtime outputs.

        Args:
            context: Generic runtime context injected by the execution engine.
        """
        metadata = self.resolve(root_dir=context.root_dir, config=context.config)
        absolute_path = str(metadata.get("absolute_path") or metadata.get("path") or "")
        display_path = str(metadata.get("path") or absolute_path)
        exists = bool(metadata.get("exists"))
        created = bool(metadata.get("created"))
        status = "success" if exists else "failed"
        exit_code = 0 if exists else 1
        outputs = [
            BlockRuntimeOutput(
                port_id=int(getattr(port, "id", 0) or 0),
                port_name=str(getattr(port, "name", "") or ""),
                value=absolute_path,
                content_type=FILE_PATH,
                status="success" if exists else "missing",
                exit_code=exit_code,
            )
            for port in context.output_ports
        ]
        log = (
            f"{'[file-created]' if created else '[file]'} {context.node_id} -> {display_path}"
            if exists
            else f"[file-warn] {context.node_id}: fichier introuvable {display_path}"
        )
        return BlockRuntimeResult(
            status=status,
            outputs=outputs,
            logs=[log],
            exit_code=exit_code,
            last_message=absolute_path,
            content_type=FILE_PATH,
            worker_received=display_path or "-",
            metadata={"file": metadata},
        )
