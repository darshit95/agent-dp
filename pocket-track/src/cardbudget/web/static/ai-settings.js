(() => {
  const provider = document.getElementById("categorization-provider");
  if (!provider) return;

  function showProviderFields() {
    const value = provider.value;
    const shown = {
      model: value !== "rules",
      endpoint: value === "local",
      cloud: ["chatgpt", "openai", "anthropic"].includes(value),
    };
    for (const field of document.querySelectorAll("[data-ai-field]")) {
      field.hidden = !shown[field.dataset.aiField];
      const input = field.querySelector("input");
      if (input) input.disabled = field.hidden;
    }
  }

  provider.addEventListener("change", showProviderFields);
  showProviderFields();

  const status = document.getElementById("categorization-status");
  const isBusy = () => ["queued", "running"].includes(status.dataset.status);
  let failures = 0;
  async function updateStatus() {
    if (!isBusy()) return;
    if (!document.hidden) {
      try {
        const response = await fetch("/settings/ai/status");
        if (!response.ok) return;
        const data = await response.json();
        status.dataset.status = data.status;
        status.textContent = data.message;
        status.hidden = !data.message;
        failures = 0;
      } catch {
        failures += 1;
      }
    }
    if (isBusy() && failures < 3) window.setTimeout(updateStatus, 3000);
  }
  if (isBusy()) window.setTimeout(updateStatus, 3000);
})();
