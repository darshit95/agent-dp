(() => {
  const config = document.getElementById("plaid-config");
  if (!config) return;
  const csrf = config.dataset.csrfToken;

  async function postJson(url, body) {
    const response = await fetch(url, {method:"POST", credentials:"same-origin", headers:{"Content-Type":"application/json","X-CSRF-Token":csrf}, body:JSON.stringify(body || {})});
    if (!response.ok) throw new Error((await response.text()) || `HTTP ${response.status}`);
    return response.json();
  }

  async function openLink(token, onSuccess) {
    const handler = Plaid.create({
      token,
      onSuccess: async (publicToken, metadata) => {
        try { await onSuccess(publicToken, metadata); window.location.reload(); }
        catch (e) { window.alert(`Plaid connection failed: ${e.message}`); }
      },
      onExit: (err) => { if (err) console.error(err); },
    });
    handler.open();
  }

  const connect = document.getElementById("plaid-connect");
  if (connect) connect.addEventListener("click", async () => {
    try {
      const response = await fetch("/plaid/link-token", {method:"POST", credentials:"same-origin", headers:{"X-CSRF-Token":csrf}});
      if (!response.ok) throw new Error(await response.text());
      const data = await response.json();
      await openLink(data.link_token, (publicToken, metadata) => postJson("/plaid/exchange", {public_token:publicToken, institution_id:metadata?.institution?.institution_id || null, institution_name:metadata?.institution?.name || null}));
    } catch (e) { window.alert(`Unable to start Plaid: ${e.message}`); }
  });

  document.querySelectorAll(".plaid-update").forEach((button) => {
    button.addEventListener("click", async () => {
      const itemId = button.dataset.itemId;
      try {
        const response = await fetch(`/plaid/items/${encodeURIComponent(itemId)}/update-link-token`, {method:"POST", credentials:"same-origin", headers:{"X-CSRF-Token":csrf}});
        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        await openLink(data.link_token, async () => {
          const done = await fetch(`/plaid/items/${encodeURIComponent(itemId)}/update-complete`, {method:"POST", credentials:"same-origin", headers:{"X-CSRF-Token":csrf}});
          if (!done.ok) throw new Error(await done.text());
        });
      } catch (e) { window.alert(`Unable to refresh access: ${e.message}`); }
    });
  });

  document.querySelectorAll(".track-card-form").forEach((form) => {
    const checkbox = form.querySelector('input[name="enabled"]');
    const status = form.querySelector(".track-status");

    if (!checkbox) return;

    // Track changes are AJAX-only. Never allow a native form submit.
    form.addEventListener("submit", (event) => {
      event.preventDefault();
    });

    checkbox.addEventListener("change", async (event) => {
      event.preventDefault();
      event.stopPropagation();

      const requestedState = checkbox.checked;
      const previousState = !requestedState;

      if (status) {
        status.textContent = "Saving…";
      }

      checkbox.disabled = true;

      try {
        const body = new FormData(form);

        /*
         * Unchecked checkboxes are omitted from FormData.
         * Make the desired state explicit so the backend always
         * receives an unambiguous value.
         */
        body.delete("enabled");

        if (requestedState) {
          body.append("enabled", "on");
        }

        const response = await fetch(form.action, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "fetch",
          },
          body,
        });

        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || `HTTP ${response.status}`);
        }

        const data = await response.json();

        checkbox.checked = Boolean(data.enabled);

        /*
         * Update the institution count in place without refreshing
         * or collapsing the <details> element.
         */
        const bank = form.closest(".bank-card");

        if (bank) {
          const allCards = bank.querySelectorAll(".track-card-form").length;
          const trackedCards = bank.querySelectorAll(
            '.track-card-form input[name="enabled"]:checked'
          ).length;

          const summary = bank.querySelector(".bank-summary small");

          if (summary) {
            const existing = summary.textContent;
            const suffixMatch = existing.match(/(\s·\ssynced.*)$/);
            const suffix = suffixMatch ? suffixMatch[1] : "";

            summary.textContent =
              `${trackedCards} of ${allCards} credit card` +
              `${allCards === 1 ? "" : "s"} tracked` +
              suffix;
          }
        }

        if (status) {
          status.textContent = "Saved";

          window.setTimeout(() => {
            status.textContent = "";
          }, 1000);
        }

      } catch (error) {
        checkbox.checked = previousState;

        if (status) {
          status.textContent = "Failed";
        }

        window.alert(
          `Unable to update card: ${error.message}`
        );

      } finally {
        checkbox.disabled = false;
      }
    });
  });
})();
