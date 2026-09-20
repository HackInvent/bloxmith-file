/**
 * Role: Mounts the file block inspector panel frontend asset.
 * File Name: inspector_panel.js
 * Author: Alexandre EL
 * Email: alex@hackinvent.com
 * Created Date: 2024-12-10
 */

import { mountFileEditor } from "./common.js";

/**
 * Mount the File Path inspector panel bindings.
 *
 * @param {HTMLElement} root - Mounted File Path inspector root.
 * @param {object} api - Generic block UI API exposing block actions.
 * @returns {void}
 */
export function mount(root, api) {
  mountFileEditor(root, api, {
    actionName: "inspector_update_file",
    successMessage: "[file] Configuration appliquee.",
  });
}
