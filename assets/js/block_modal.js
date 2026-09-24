import { withProperties } from "./properties.js";

/**
 * Role: Mounts the file block modal frontend asset.
 * File Name: block_modal.js
 * Author: Alexandre EL
 * Email: alex@hackinvent.com
 * Created Date: 2026-06-10
 */

import { mountFileEditor } from "./common.js";

/**
 * Mount the File Path modal bindings using the modal update action.
 *
 * @param {HTMLElement} root - Mounted File Path modal root.
 * @param {object} api - Generic block UI API exposing block actions.
 * @returns {void}
 */
function mountOwned(root, api) {
  mountFileEditor(root, api, {
    actionName: "modal_update_file",
    successMessage: "[file] Configuration modale appliquee.",
  });
}

/** Keep the block behavior and add properties-only accessibility. */
export function mount(root, ...args) {
  return withProperties(mountOwned).call(this, root, ...args);
}
