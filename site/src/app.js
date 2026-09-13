(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const cards = [...document.querySelectorAll(".candidate")];
  const search = $("#catalog-search");
  const bundle = $("#bundle-filter");
  const status = $("#status-filter");
  const form = $("#catalog-filters");
  const result = $("#result-count");
  const empty = $("#empty-state");
  const normalize = (value) => value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  const index = cards.map((card) => ({
    card,
    text: normalize(card.textContent),
  }));

  function filterCards() {
    const words = normalize(search.value).split(/\s+/).filter(Boolean);
    let count = 0;
    for (const entry of index) {
      const matches = words.every((word) => entry.text.includes(word))
        && (bundle.value === "all" || entry.card.dataset.bundle === bundle.value)
        && (status.value === "all" || entry.card.dataset.status === status.value);
      entry.card.hidden = !matches;
      if (matches) count += 1;
    }
    result.textContent = `Showing ${count} of ${cards.length} candidates`;
    empty.hidden = count !== 0;
  }

  form.hidden = false;
  form.addEventListener("submit", (event) => event.preventDefault());
  search.addEventListener("input", filterCards);
  bundle.addEventListener("change", filterCards);
  status.addEventListener("change", filterCards);
  $("#reset-filters").addEventListener("click", () => {
    form.reset();
    filterCards();
    search.focus({ preventScroll: true });
  });
  document.querySelectorAll("[data-bundle-link]").forEach((link) => {
    link.addEventListener("click", () => {
      form.reset();
      bundle.value = link.dataset.bundleLink;
      filterCards();
      search.focus({ preventScroll: true });
    });
  });

  const capacityInputs = [...document.querySelectorAll('input[name="capacity"]')];
  function updateCapacity(announce = true) {
    const selected = capacityInputs.find((input) => input.checked).value;
    $("#capacity-existing").hidden = selected !== "existing";
    $("#capacity-new").hidden = selected !== "new";
    if (announce) {
      $("#capacity-announcement").textContent = selected === "existing"
        ? "Existing capacity guidance shown: focus on useful adoption and renewal."
        : "New capacity guidance shown: prove quality and actual demand before purchase.";
    }
  }
  capacityInputs.forEach((input) => input.addEventListener("change", () => updateCapacity()));
  updateCapacity(false);

  const themeButton = $("#theme-toggle");
  function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    themeButton.textContent = theme === "light" ? "Dark theme" : "Light theme";
    themeButton.setAttribute("aria-label", `Switch to ${theme === "light" ? "dark" : "light"} theme`);
  }
  let manualTheme = false;
  setTheme(document.documentElement.dataset.theme);
  themeButton.hidden = false;
  themeButton.addEventListener("click", () => {
    manualTheme = true;
    setTheme(document.documentElement.dataset.theme === "light" ? "dark" : "light");
  });
  const preference = window.matchMedia("(prefers-color-scheme: dark)");
  preference.addEventListener("change", (event) => {
    const override = new URLSearchParams(window.location.search).get("scoutTheme");
    if (!manualTheme && override !== "dark" && override !== "light") setTheme(event.matches ? "dark" : "light");
  });

  const dialog = $("#candidate-dialog");
  let opener = null;
  if (typeof dialog.showModal === "function") {
    for (const card of cards) {
      const fallback = card.querySelector(".candidate-fallback");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "detail-button";
      const name = card.querySelector("h3").textContent;
      button.textContent = "Evidence & next step";
      const arrow = document.createElement("span");
      arrow.textContent = "↗";
      arrow.setAttribute("aria-hidden", "true");
      button.append(arrow);
      button.setAttribute("aria-label", `Evidence and next step: ${name}`);
      button.setAttribute("aria-haspopup", "dialog");
      button.setAttribute("aria-controls", "candidate-dialog");
      button.addEventListener("click", () => {
        opener = button;
        $("#dialog-title").textContent = name;
        $("#dialog-kicker").textContent = `Candidate ${card.dataset.id.padStart(2, "0")} / Evaluation boundary`;
        $("#dialog-content").replaceChildren(fallback.querySelector(".detail-body").cloneNode(true));
        dialog.showModal();
        dialog.scrollTop = 0;
        $("#close-dialog").focus({ preventScroll: true });
      });
      fallback.hidden = true;
      card.append(button);
    }
    $("#close-dialog").addEventListener("click", () => dialog.close());
    // Native modal semantics handle inert background and Escape-to-close.
    // Explicit Tab wrapping also keeps focus in the dialog instead of browser chrome.
    dialog.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") return;
      const controls = [...dialog.querySelectorAll('button, a[href], input, select, textarea, [tabindex="0"]')]
        .filter((node) => !node.disabled && node.getClientRects().length);
      const first = controls[0];
      const last = controls[controls.length - 1];
      if ((!event.shiftKey && document.activeElement === last)
        || (event.shiftKey && document.activeElement === first)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
      }
    });
    dialog.addEventListener("close", () => {
      $("#dialog-content").replaceChildren();
      if (opener?.isConnected) opener.focus({ preventScroll: true });
    });
  }

  // Printing includes all candidates and both capacity options without changing filters.
  let prePrintTheme;
  window.addEventListener("beforeprint", () => {
    if (prePrintTheme === undefined) prePrintTheme = document.documentElement.dataset.theme;
    document.documentElement.dataset.theme = "light";
  });
  window.addEventListener("afterprint", () => {
    if (prePrintTheme !== undefined) setTheme(prePrintTheme);
    prePrintTheme = undefined;
  });
  const print = $("#print-summary");
  print.hidden = false;
  print.addEventListener("click", () => window.print());
})();
