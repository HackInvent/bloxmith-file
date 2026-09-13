/**
 * Role: Mounts the file block modal frontend asset.
 * File Name: block_modal.js
 * Author: Alexandre EL
 * Email: alex@hackinvent.com
 * Created Date: 2026-06-10
 */

(function () {
  "use strict";

  const registry = (window.CWBlockUiBlocks = window.CWBlockUiBlocks || {});

  registry.file = {
    /**
     * Mount the File Path modal bindings using the modal update action.
     *
     * @param {HTMLElement} root - Mounted File Path modal root.
     * @param {object} api - Generic block UI API exposing block actions.
     * @returns {void}
     */
    mount(root, api) {
      window.CWFileBlockUi?.mountFileEditor?.(root, api, {
        actionName: "modal_update_file",
        successMessage: "[file] Configuration modale appliquee.",
      });
    },
  };
})();
