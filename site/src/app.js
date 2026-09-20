(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const cards = [...document.querySelectorAll(".candidate")];
  const search = $("#catalog-search");
  const bundle = $("#bundle-filter");
  const problem = $("#problem-filter");
  const form = $("#catalog-filters");
  const normalize = (value) => value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  const index = cards.map((card) => ({
    card,
    text: normalize(`${card.textContent} ${$(`#solution-${card.dataset.id}`).textContent}`),
  }));
  const sections = [...document.querySelectorAll("[data-page]")];
  const navigation = [...document.querySelectorAll("[data-view-link]")];
  let currentView = "overview";
  let activeSolution = null;

  function activateView(hash, { focus = false, scroll = false } = {}) {
    let id;
    try { id = decodeURIComponent(hash.replace(/^#/, "")); } catch { id = "top"; }
    const target = document.getElementById(id || "top") || $("#top");
    if (id !== "main") {
      activeSolution = target.closest(".solution-page");
      currentView = target.closest("[data-page]")?.dataset.page || "overview";
    }
    for (const section of sections) {
      section.hidden = section.dataset.page !== currentView
        || (currentView === "solution" && section !== activeSolution);
      section.classList.toggle("active-solution", section === activeSolution);
    }
    for (const link of navigation) {
      if (link.dataset.viewLink === (currentView === "solution" ? "catalog" : currentView)) {
        link.setAttribute("aria-current", "page");
      } else link.removeAttribute("aria-current");
    }
    for (const link of document.querySelectorAll(".solution-nav a")) {
      const selected = link.hash === hash
        || (activeSolution?.id === id && link.hash === `#${id}-workflow`);
      if (selected) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
    const disclosure = target.closest("details");
    if (disclosure) disclosure.open = true;
    document.documentElement.dataset.view = currentView;
    const title = { overview: "Overview", catalog: "Solution library", guide: "Get started", roadmap: "Planned workflows" };
    document.title = `${activeSolution?.querySelector("h2").textContent || title[currentView]} · AI Solutions Hub`;
    if (scroll) target.scrollIntoView({ block: "start", behavior: "instant" });
    if (focus) {
      const heading = id === "main" || target.matches("h1, h2, h3, summary")
        ? target : target.querySelector("h1, h2, h3, summary") || target;
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
    const discovery = link.hasAttribute("data-bundle-link") || link.hasAttribute("data-problem-link");
    navigateTo(link.getAttribute("href"), !discovery);
    if (discovery) search.focus({ preventScroll: true });
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
    chip.textContent = option.value === "all" ? "All solutions" : option.textContent;
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
        && (problem.value === "all" || entry.card.dataset.problems.split(" ").includes(problem.value));
      entry.card.hidden = !matches;
      if (matches) count += 1;
    }
    $("#result-count").textContent = `Showing ${count} of ${cards.length} solutions`;
    $("#empty-state").hidden = count !== 0;
    for (const chip of chips.children) chip.setAttribute("aria-pressed", String(chip.dataset.bundleChoice === bundle.value));
  }
  form.hidden = false;
  form.addEventListener("submit", (event) => event.preventDefault());
  search.addEventListener("input", filterCards);
  bundle.addEventListener("change", filterCards);
  problem.addEventListener("change", filterCards);
  function resetFilters() {
    form.reset();
    filterCards();
    search.focus({ preventScroll: true });
  }
  $("#reset-filters").addEventListener("click", resetFilters);
  $("#clear-empty").addEventListener("click", resetFilters);
  for (const attribute of ["bundle", "problem"]) {
    document.querySelectorAll(`[data-${attribute}-link]`).forEach((link) => {
      link.addEventListener("click", (event) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        form.reset();
        (attribute === "bundle" ? bundle : problem).value = link.dataset[`${attribute}Link`];
        filterCards();
      });
    });
  }
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
      || event.target.closest("input, textarea, select, [contenteditable]")) return;
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
    if (announce) $("#capacity-announcement").textContent = selected === "existing"
      ? "Existing capacity guidance shown: focus on useful adoption and renewal."
      : "New capacity guidance shown: prove quality and actual demand before purchase.";
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
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
    const override = new URLSearchParams(window.location.search).get("scoutTheme");
    if (!manualTheme && override !== "dark" && override !== "light") setTheme(event.matches ? "dark" : "light");
  });

  const selected = new Set();
  const toggles = [...document.querySelectorAll("[data-select]")];
  let activePathway = null;
  function renderPilotBrief() {
    const brief = $("#pilot-brief");
    brief.replaceChildren();
    if (activePathway && !selected.has(activePathway.dataset.primary)) {
      activePathway = null;
      $("#pilot-plan-status").textContent = "Pilot brief cleared because its starting candidate was removed. Other selections are unchanged.";
    }
    brief.hidden = !activePathway;
    if (!activePathway) return;
    const title = document.createElement("h3");
    title.textContent = `${activePathway.querySelector("h3").textContent}: pilot brief`;
    const note = document.createElement("p");
    note.textContent = "Planning only. Agree the baseline, target, named owners, time box and budget before deployment. Other shortlisted solutions are not automatically part of this pilot.";
    brief.append(title, note, activePathway.querySelector(".pathway-brief").cloneNode(true));
  }
  function cloneGuide(id) {
    const clone = $(`#solution-${id} .solution-body`).cloneNode(true);
    // Shortlist copies need their own anchor and accessible-label namespace.
    const ids = new Set([...clone.querySelectorAll("[id]")].map((node) => node.id));
    for (const node of clone.querySelectorAll("[id]")) node.id = `plan-${node.id}`;
    for (const node of clone.querySelectorAll("[aria-labelledby]")) {
      node.setAttribute("aria-labelledby", node.getAttribute("aria-labelledby").split(" ")
        .map((id) => ids.has(id) ? `plan-${id}` : id).join(" "));
    }
    for (const node of clone.querySelectorAll('a[href^="#"]')) {
      const target = node.getAttribute("href").slice(1);
      if (ids.has(target)) node.setAttribute("href", `#plan-${target}`);
    }
    return clone;
  }
  function renderShortlist() {
    $("#shortlist-count").textContent = selected.size
      ? `${selected.size} solution${selected.size === 1 ? "" : "s"} selected for planning.`
      : "No solutions selected. Open a solution and add it to your shortlist.";
    $("#shortlist .shortlist-actions").hidden = selected.size === 0;
    $("#shortlist-items").replaceChildren();
    for (const card of cards.filter((item) => selected.has(item.dataset.id))) {
      const article = document.createElement("article");
      article.className = "shortlist-item";
      const title = document.createElement("h4");
      const name = card.querySelector("h3").textContent;
      title.textContent = name;
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "text-button";
      remove.textContent = "Remove";
      remove.setAttribute("aria-label", `Remove ${name} from shortlist`);
      remove.addEventListener("click", () => {
        selected.delete(card.dataset.id);
        renderShortlist();
        $("#shortlist-title").setAttribute("tabindex", "-1");
        $("#shortlist-title").focus({ preventScroll: true });
      });
      const detail = document.createElement("details");
      detail.className = "selected-guide";
      const summary = document.createElement("summary");
      summary.textContent = "Workflow, architecture, deployment and specialist plan";
      detail.append(summary, cloneGuide(card.dataset.id));
      article.append(title, remove, detail);
      $("#shortlist-items").append(article);
    }
    for (const toggle of toggles) {
      const added = selected.has(toggle.dataset.select);
      toggle.textContent = added ? "Remove from shortlist" : "Add to shortlist";
      toggle.setAttribute("aria-pressed", String(added));
    }
    renderPilotBrief();
  }
  for (const button of document.querySelectorAll("[data-plan-pathway]")) {
    button.hidden = false;
    button.addEventListener("click", () => {
      activePathway = $(`#pathway-${button.dataset.planPathway}`);
      selected.add(activePathway.dataset.primary);
      renderShortlist();
      $("#pilot-plan-status").textContent = `${activePathway.querySelector("h3").textContent} pilot brief selected. Existing shortlist entries retained; optional extensions were not added.`;
      navigateTo("#shortlist");
    });
  }
  for (const toggle of toggles) {
    toggle.hidden = false;
    toggle.addEventListener("click", () => {
      const id = toggle.dataset.select;
      if (selected.has(id)) selected.delete(id);
      else selected.add(id);
      renderShortlist();
    });
  }
  $("#clear-shortlist").addEventListener("click", () => {
    selected.clear();
    activePathway = null;
    $("#pilot-plan-status").textContent = "Shortlist and pilot brief cleared.";
    renderShortlist();
    $("#shortlist-title").setAttribute("tabindex", "-1");
    $("#shortlist-title").focus();
  });
  $("#print-plan").addEventListener("click", () => {
    document.documentElement.dataset.printPlan = "selected";
    window.print();
  });
  let prePrintTheme;
  let prePrintDisclosures;
  window.addEventListener("beforeprint", () => {
    if (prePrintTheme === undefined) prePrintTheme = document.documentElement.dataset.theme;
    if (!document.documentElement.dataset.printPlan && currentView === "solution") {
      document.documentElement.dataset.printPlan = "solution";
    }
    if (prePrintDisclosures === undefined) {
      prePrintDisclosures = [...document.querySelectorAll(".bundle-inventory, .selected-guide, .deployment-notes, .connection-details, .catalog-review")]
        .map((detail) => ({ detail, open: detail.open }));
      for (const { detail } of prePrintDisclosures) detail.open = true;
    }
    document.documentElement.dataset.theme = "light";
  });
  window.addEventListener("afterprint", () => {
    if (prePrintTheme !== undefined) setTheme(prePrintTheme);
    prePrintTheme = undefined;
    for (const { detail, open } of prePrintDisclosures || []) detail.open = open;
    prePrintDisclosures = undefined;
    delete document.documentElement.dataset.printPlan;
  });
  $("#print-summary").hidden = false;
  $("#print-summary").addEventListener("click", () => window.print());
})();
