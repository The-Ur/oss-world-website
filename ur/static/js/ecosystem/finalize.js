/*
 *
 * Copyright (c) Ur LLC and its affiliates
 *
 * This source code is licensed under the Apache 2.0 license found
 * in the LICENSE file in the root directory of this source tree.
 *
 */

(function() {
  const finalizeButton = document.getElementById("finalize-application-button");
  if (!finalizeButton) return;
  finalizeButton.textContent = finalizeButton.dataset.text;
  finalizeButton.addEventListener("click", async function(e) {
    finalizeButton.textContent = "";
    finalizeButton.insertAdjacentHTML("beforeend", `
    <div class="spinner-border" role="status" id="finalize-button-spinner">
      <span class="visually-hidden">Loading...</span>
    </div>`);
    finalizeButton.setAttribute("disabled", "disabled");
    try {
      const resp = await fetch(finalizeButton.dataset.link, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: JSON.stringify({
          organization_id: finalizeButton.dataset.id,
          organization_slug: finalizeButton.dataset.slug
        }),
      });
      if (resp.ok) {
        window.location.reload();
        return;
      } else {
        document.getElementById("finalize-button-spinner")?.remove();
        finalizeButton.textContent = await resp.text() ?? finalizeButton.dataset.text;
      }
    } catch (e) {
      document.getElementById("finalize-button-spinner")?.remove();
      finalizeButton.textContent = e.toString() ?? finalizeButton.dataset.text;
    }
    finalizeButton.removeAttribute("disabled");
  });
})();
