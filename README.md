# File Path Block

<!-- block-metadata:start -->
[![Block version: unversioned](https://img.shields.io/badge/block-unversioned-lightgrey)](model.json)
[![BloxSmith compatibility: 1.0.9](https://img.shields.io/badge/BloxSmith-1.0.9-brightgreen)](compatibility.json)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Verified BloxSmith versions: **1.0.9** (bundled-block tests; see [test evidence](compatibility.json)).
<!-- block-metadata:end -->


## Role

`file` is the File Path source block. It resolves a filesystem path and emits it as a runtime value when downstream blocks need a file reference instead of file contents.

Use it when a later block knows how to read or process a file path itself, for example a transcription block, image block, CLI command, or custom Python block.

## Files

- `block.py`: path resolution, optional creation, runtime emission, modal rendering, and inspector logic.
- `model.json`: default path config and output port declaration.
- `block_modal.html`, `inspector_panel.html`, `assets/`: block-owned modal and inspector UI.
- `node_card.html`: block-owned canvas card body.

## Ports

- Outputs:
  - `fichier` (`id: 1`): emits `file/path` and `message/*`.

The block has no inputs.

## Configuration

- `path`: relative or absolute path to resolve. Relative paths are resolved from the project root.
- `create_if_missing`: when true, creates the file and parent directories if the file does not exist.

## Runtime Behavior

`execute_runtime()` resolves the configured path, optionally creates the file, then emits the absolute path on every output. The content type is `file/path`.

Path resolution rejects directories and reports missing files unless `create_if_missing` is enabled.

## Example

Set `path` to `./media/audio.mp3` and connect the output to an audio transcription block. The example path is relative to the project root. At runtime, this block emits the resolved absolute file path with content type `file/path`.

## UI Behavior

The inspector panel and modal hydrate path values only from canonical `node.config`. It edits the path and `create_if_missing` flag through
`inspector_update_file` or `modal_update_file` only when the user clicks the file-specific
**Apply** button. The **Browse** button uses the shared `CWPathBrowser` control and calls
`/api/blocks/file/browse-files` directly to list files without adding file-specific behavior to the
shared frontend shell.

## Editor Display

The canvas card is rendered by this block through `node_card.html`. It shows only the file name to
avoid overflowing the fixed node card; the full configured path remains available as the preview
tooltip. The shared editor shell keeps ports, dragging, status, and graph links generic.

## Limits

This block does not read file contents and does not validate that the target file type matches downstream expectations. Use `file_content` when the workflow needs the text content instead of the path.

## Modal

`block_modal.html` is owned by this block. It keeps the generic title binding, and uses the same
shared file path browser and create-if-missing controls as the inspector.

## Maintenance Notes

Keep path validation in the block. The orchestrator must not learn file-block-specific rules.

## UI surface migration

- The modal declares `data-block-runtime-refresh="autonomous"` so path browsing and draft path edits survive runtime polling.
- Shared File Path UI helpers live in `assets/js/common.js`.
- Modal behavior is mounted by `assets/js/block_modal.js`; inspector behavior is mounted by `assets/js/inspector_panel.js`.
- Durable file path edits continue to go through block-owned UI actions.

## Compatibility policy

[compatibility.json](compatibility.json) records HackInvent's verified BloxSmith versions and test evidence. Only the versions listed above have been verified, using the block-owned suites in a **bundled-block test installation**. This is not a certification of managed-package installation, every browser/OS, or live provider availability. Other framework versions are unverified, not necessarily incompatible.

The block-version badge follows `model.json`, not a published Git tag. `unversioned` means that no block release version is declared; no number is inferred from the framework version. The framework still uses `model.json` for its runtime/install contract; the tester-owned JSON does not replace it. Official integration tests run in the private `bloxmith-blocs` workspace. Test helpers and the proprietary framework are not bundled in this public block repository.
