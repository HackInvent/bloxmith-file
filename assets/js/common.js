/**
 * Role: Provides shared File block UI helpers for modal and inspector surfaces.
 * File Name: common.js
 * Author: Alexandre EL
 * Email: alex@hackinvent.com
 * Created Date: 2026-06-10
 */

/**
 * Bind File Path controls that are specific to the block while the shared
 * CWPathBrowser owns directory browsing and path selection.
 *
 * @param {HTMLElement} root - Mounted modal or inspector root.
 * @param {object} api - Generic block UI API exposing block actions.
 * @param {object} options - Action and log message used by the surface.
 * @returns {void}
 */
export function mountFileEditor(root, api, { actionName, successMessage }) {
  const pathInput = root.querySelector("[data-file-path]");
  const createInput = root.querySelector("[data-file-create-if-missing]");
  const applyButton = root.querySelector("[data-file-apply]");
  let dirty = false;

  /**
   * Toggle pending-change state and keep the Apply button in sync.
   *
   * @param {boolean} value - Whether unsaved file settings exist.
   */
  const setDirty = (value) => {
    dirty = Boolean(value);
    if (applyButton) {
      applyButton.disabled = !dirty;
    }
  };

  /**
   * Persist the File Path config for the current UI surface.
   *
   * @returns {Promise<void>} Completes after the block action finishes.
   */
  const apply = async () => {
    if (!pathInput || !dirty) {
      return;
    }
    if (applyButton) {
      applyButton.disabled = true;
    }
    try {
      await api.applyAction(actionName, {
        path: pathInput.value || "",
        create_if_missing: Boolean(createInput?.checked),
      });
      setDirty(false);
      api.log?.(successMessage);
    } catch (error) {
      setDirty(true);
      api.log?.(`[error] File Path update failed: ${error.message}`);
    }
  };

  const markEdited = () => setDirty(true);

  pathInput?.addEventListener("input", markEdited);
  pathInput?.addEventListener("change", markEdited);
  pathInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      void apply();
    }
  });
  createInput?.addEventListener("change", markEdited);
  applyButton?.addEventListener("click", () => {
    void apply();
  });
};
