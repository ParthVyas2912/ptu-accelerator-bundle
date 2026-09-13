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
  const sections = [...document.querySelectorAll("[data-page]")];
  const navigation = [...document.querySelectorAll("[data-view-link]")];
  let currentView = "overview";

  function activateView(hash, { focus = false, scroll = false } = {}) {
    let id;
    try { id = decodeURIComponent(hash.replace(/^#/, "")); } catch { id = "top"; }
    const target = document.getElementById(id || "top") || $("#top");
    currentView = target?.closest("[data-page]")?.dataset.page
      || (id === "main" ? currentView : "overview");
    for (const section of sections) section.hidden = section.dataset.page !== currentView;
    for (const link of navigation) {
      if (link.dataset.viewLink === currentView) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    }
    document.documentElement.dataset.view = currentView;
    const title = { overview: "Overview", catalog: "Solution library", guide: "PTU guide", roadmap: "Next steps" };
    document.title = `${title[currentView]} · PTU portfolio`;
    if (target && scroll) target.scrollIntoView({ block: "start", behavior: "instant" });
    if (target && focus) {
      const heading = id === "main" || target.matches("h1, h2, h3")
        ? target : target.querySelector("h1, h2") || target;
      heading.setAttribute("tabindex", "-1");
      heading.focus({ preventScroll: true });
    }
  }

  function navigateTo(hash, focus = true) {
    if (hash !== location.hash) history.pushState(null, "", hash);
    activateView(hash, { focus, scroll: true });
  }
  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.defaultPrevented || event.button !== 0
      || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const isBundle = link.hasAttribute("data-bundle-link");
    navigateTo(link.getAttribute("href"), !isBundle);
    if (isBundle) search.focus({ preventScroll: true });
  });
  for (const event of ["popstate", "hashchange"]) {
    window.addEventListener(event, () => activateView(location.hash, { focus: true, scroll: true }));
  }
  document.documentElement.classList.add("has-navigation");
  activateView(location.hash);

  const chips = $("#bundle-chips");
  for (const option of bundle.options) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.dataset.bundleChoice = option.value;
    chip.textContent = option.value === "all" ? "All solutions"
      : { knowledge: "Knowledge & staff work", procurement: "Procurement & documents", engineering: "Engineering" }[option.value] || option.textContent;
    chip.setAttribute("aria-controls", "catalog-grid");
    chip.addEventListener("click", () => {
      bundle.value = option.value;
      filterCards();
    });
    chips.append(chip);
  }
  chips.hidden = false;

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
    for (const chip of chips.children) {
      chip.setAttribute("aria-pressed", String(chip.dataset.bundleChoice === bundle.value));
    }
  }

  form.hidden = false;
  form.addEventListener("submit", (event) => event.preventDefault());
  search.addEventListener("input", filterCards);
  bundle.addEventListener("change", filterCards);
  status.addEventListener("change", filterCards);
  function resetFilters() {
    form.reset();
    filterCards();
    search.focus({ preventScroll: true });
  }
  $("#reset-filters").addEventListener("click", resetFilters);
  $("#clear-empty").addEventListener("click", resetFilters);
  document.querySelectorAll("[data-bundle-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      form.reset();
      bundle.value = link.dataset.bundleLink;
      filterCards();
    });
  });
  filterCards();

  const layouts = [...document.querySelectorAll("#view-switch button")];
  $("#view-switch").hidden = false;
  for (const button of layouts) {
    button.addEventListener("click", () => {
      $("#catalog-grid").dataset.layout = button.dataset.layout;
      for (const item of layouts) item.setAttribute("aria-pressed", String(item === button));
    });
  }
  document.addEventListener("keydown", (event) => {
    if (event.key !== "/" || event.ctrlKey || event.metaKey || event.altKey
      || event.target.closest("input, textarea, select, [contenteditable]")
      || $("#candidate-dialog").open) return;
    event.preventDefault();
    navigateTo("#catalog", false);
    search.focus({ preventScroll: true });
  });
  search.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && search.value) {
      event.preventDefault();
      search.value = "";
      filterCards();
    }
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
    document.documentElement.classList.add("has-dialogs");
    for (const card of cards) {
      const fallback = card.querySelector(".candidate-fallback");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "detail-button";
      const name = card.querySelector("h3").textContent;
      button.textContent = "View details";
      const arrow = document.createElement("span");
      arrow.textContent = "→";
      arrow.setAttribute("aria-hidden", "true");
      button.append(arrow);
      button.setAttribute("aria-label", `View details: ${name}`);
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
