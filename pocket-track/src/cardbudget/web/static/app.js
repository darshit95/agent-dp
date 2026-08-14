(() => {
  const money = (cents) => `$${(Number(cents || 0) / 100).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

  document.querySelectorAll("[data-auto-submit]").forEach((input) => {
    /*
     * Plaid credit-card Track controls are AJAX-managed by plaid.js.
     * Never perform a normal form submission for them because that
     * reloads Settings and collapses the open bank accordion.
     */
    if (input.closest(".track-card-form")) return;

    input.addEventListener("change", () => {
      input.form?.requestSubmit();
    });
  });

  document.querySelectorAll('form[data-confirm-delete="transaction"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm("Delete this transaction from PocketTrack? It will stay deleted after future Plaid syncs.")) event.preventDefault();
    });
  });
  document.querySelectorAll('form[data-confirm-delete="bucket"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
      const name = form.dataset.bucketName || "this bucket";
      if (!window.confirm(`Delete ${name}? Its transactions stay in PocketTrack and move back to Unknown.`)) event.preventDefault();
    });
  });
  document.querySelectorAll('form[data-confirm-delete="asset"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm("Delete this asset from PocketTrack?")) event.preventDefault();
    });
  });
  document.querySelectorAll('form[data-confirm-delete="liability"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm("Delete this liability from PocketTrack?")) event.preventDefault();
    });
  });

  const nwConfig = document.getElementById("networth-config");
  if (nwConfig) {
    const csrf = nwConfig.dataset.csrfToken;
    const updateTotals = (payload) => {
      const totals = payload.totals || {};
      const net = document.querySelector("[data-net-worth-total]");
      const assets = document.querySelector("[data-assets-total]");
      const liabilities = document.querySelector("[data-liabilities-total]");
      const allocationTotal = document.querySelector("[data-allocation-total]");
      if (net) net.textContent = money(totals.net_worth);
      if (assets) assets.textContent = money(totals.assets);
      if (liabilities) liabilities.textContent = money(totals.liabilities);
      if (allocationTotal) allocationTotal.textContent = `$${(Number(totals.assets || 0) / 100).toLocaleString(undefined, {maximumFractionDigits: 0})}`;

      (payload.allocation || []).forEach((segment) => {
        const circle = document.querySelector(`[data-allocation-bucket="${CSS.escape(segment.bucket)}"]`);
        if (circle) {
          circle.setAttribute("stroke-dasharray", segment.dash);
          circle.setAttribute("stroke-dashoffset", segment.offset);
        }
        const legend = document.querySelector(`[data-legend-bucket="${CSS.escape(segment.bucket)}"]`);
        if (legend) {
          const value = legend.querySelector("[data-legend-value]");
          const percent = legend.querySelector("[data-legend-percent]");
          if (value) value.textContent = money(segment.value_cents);
          if (percent) percent.textContent = `${Number(segment.percent).toFixed(1)}%`;
        }
      });
    };

    const saveInline = async (input) => {
      const original = input.dataset.original ?? "";
      const current = input.value.trim();
      if (current === original) return;
      const assetId = input.dataset.assetId;
      const state = document.querySelector(`[data-save-state="${CSS.escape(assetId)}"]`);
      if (state) state.textContent = "Saving…";
      input.classList.add("saving");
      try {
        const response = await fetch(`/net-worth/assets/${encodeURIComponent(assetId)}/inline`, {
          method: "POST",
          credentials: "same-origin",
          headers: {"Content-Type": "application/json", "X-CSRF-Token": csrf},
          body: JSON.stringify({field: input.dataset.inlineAssetField, value: current}),
        });
        if (!response.ok) {
          let message = "Unable to save asset.";
          try { message = (await response.json()).detail || message; } catch (_) {}
          throw new Error(message);
        }
        const payload = await response.json();
        const field = input.dataset.inlineAssetField;
        const normalized = field === "current_value" ? payload.asset.current_value : (payload.asset[field] ?? "");
        input.value = normalized;
        input.dataset.original = normalized;

        /*
         * Keep the existing asset-options form synchronized with
         * inline edits. Otherwise saving category/include options
         * later could overwrite the newly edited inline values.
         */
        const assetRow = input.closest("[data-asset-row]");

        if (assetRow) {
          const optionForm = assetRow.querySelector(
            ".asset-option-form"
          );

          if (optionForm) {
            const nameField = optionForm.querySelector(
              'input[name="name"]'
            );

            const institutionField = optionForm.querySelector(
              'input[name="institution"]'
            );

            const valueField = optionForm.querySelector(
              'input[name="current_value"]'
            );

            const assetPayload = payload.asset || {};

            if (nameField) {
              nameField.value = assetPayload.name ?? "";
            }

            if (institutionField) {
              institutionField.value =
                assetPayload.institution ?? "";
            }

            if (valueField) {
              valueField.value =
                assetPayload.current_value ?? "";
            }
          }
        }

        updateTotals(payload);
        if (state) {
          state.textContent = "Saved";
          state.classList.add("saved");
          window.setTimeout(() => { state.textContent = ""; state.classList.remove("saved"); }, 1200);
        }
      } catch (error) {
        input.value = original;
        if (state) state.textContent = "Not saved";
        window.alert(error.message);
      } finally {
        input.classList.remove("saving");
      }
    };

    document.querySelectorAll("[data-inline-asset-field]").forEach((input) => {
      input.addEventListener("focus", () => input.select());
      input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") { event.preventDefault(); input.blur(); }
        if (event.key === "Escape") { input.value = input.dataset.original ?? ""; input.blur(); }
      });
      input.addEventListener("blur", () => saveInline(input));
    });


    const saveInlineLiability = async (input) => {
      const original = input.dataset.original ?? "";
      const current = input.value.trim();

      if (current === original) return;

      const liabilityId = input.dataset.liabilityId;

      const state = document.querySelector(
        `[data-liability-save-state="${CSS.escape(liabilityId)}"]`
      );

      if (state) {
        state.textContent = "Saving…";
      }

      input.classList.add("saving");

      try {
        const response = await fetch(
          `/net-worth/liabilities/${encodeURIComponent(liabilityId)}/inline`,
          {
            method: "POST",
            credentials: "same-origin",
            headers: {
              "Content-Type": "application/json",
              "X-CSRF-Token": csrf,
            },
            body: JSON.stringify({
              field: input.dataset.inlineLiabilityField,
              value: current,
            }),
          }
        );

        if (!response.ok) {
          let message = "Unable to save liability.";

          try {
            message =
              (await response.json()).detail || message;
          } catch (_) {}

          throw new Error(message);
        }

        const payload = await response.json();
        const field = input.dataset.inlineLiabilityField;

        const normalized =
          field === "current_balance"
            ? payload.liability.current_balance
            : (payload.liability[field] ?? "");

        input.value = normalized;
        input.dataset.original = normalized;

        /*
         * Keep the old Save Options workflow synchronized with
         * inline edits so toggling "Include in net worth" later
         * cannot overwrite an inline edit with stale values.
         */
        const row = input.closest("[data-liability-row]");

        if (row) {
          const optionForm = row.querySelector(
            "[data-liability-options]"
          );

          if (optionForm) {
            const hiddenName =
              optionForm.querySelector(
                "[data-liability-hidden-name]"
              );

            const hiddenInstitution =
              optionForm.querySelector(
                "[data-liability-hidden-institution]"
              );

            const hiddenBalance =
              optionForm.querySelector(
                "[data-liability-hidden-balance]"
              );

            if (hiddenName) {
              hiddenName.value =
                payload.liability.name ?? "";
            }

            if (hiddenInstitution) {
              hiddenInstitution.value =
                payload.liability.institution ?? "";
            }

            if (hiddenBalance) {
              hiddenBalance.value =
                payload.liability.current_balance ?? "";
            }
          }
        }

        updateTotals(payload);

        if (state) {
          state.textContent = "Saved";
          state.classList.add("saved");

          window.setTimeout(() => {
            state.textContent = "";
            state.classList.remove("saved");
          }, 1200);
        }

      } catch (error) {

        input.value = original;

        if (state) {
          state.textContent = "Not saved";
        }

        window.alert(error.message);

      } finally {
        input.classList.remove("saving");
      }
    };


    document
      .querySelectorAll("[data-inline-liability-field]")
      .forEach((input) => {

        input.addEventListener(
          "focus",
          () => input.select()
        );

        input.addEventListener(
          "keydown",
          (event) => {

            if (event.key === "Enter") {
              event.preventDefault();
              input.blur();
            }

            if (event.key === "Escape") {
              input.value =
                input.dataset.original ?? "";

              input.blur();
            }
          }
        );

        input.addEventListener(
          "blur",
          () => saveInlineLiability(input)
        );
      });
  }
})();
