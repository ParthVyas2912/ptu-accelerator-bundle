const pptxgen = require('pptxgenjs');
const fs = require('node:fs');
const path = require('node:path');

const out = __dirname;
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'PTU Accelerator working team';
pptx.subject = 'Internal Microsoft discussion: customer outcomes, Azure adoption and evidence-led PTU decisions';
pptx.title = 'PTU Accelerator | From useful AI to justified capacity';
pptx.company = 'Internal working material - not an official commercial SKU';
pptx.lang = 'en-CA';
pptx.theme = {
  headFontFace: 'Segoe UI Semibold',
  bodyFontFace: 'Segoe UI',
  lang: 'en-CA',
};

const C = {
  bg: 'F7F4EF', paper: 'FFFFFF', ink: '242424', muted: '5C5C5C',
  rose: 'B11F4B', pale: 'F5E5E9', dark: '292929', pink: 'FD8EA1',
  border: 'DEDEDE', soft: 'F5F5F5', light: 'DEDEDE',
};
const W = 13.333333, H = 7.5;
const sections = [];
const sources = {
  recommendation: 'Basis: Commercial recommendation, 12 Sep 2026, sections 1-5.',
  evidence: 'Basis: First-pass evaluation, 12 Sep 2026, sections 1-3. Recorded results, not a fresh health check.',
  motion: 'Basis: Commercial recommendation, 12 Sep 2026, sections 3, 7 and 9.',
  planned: 'Proposed delivery plan; not an approved commitment, implemented workflow or customer result.',
};

function text(s, value, x, y, w, h, size = 18, options = {}) {
  s.addText(value, {
    x, y, w, h, fontFace: 'Segoe UI', fontSize: size, color: C.ink,
    margin: 0, breakLine: false, valign: 'mid', ...options,
  });
}
function box(s, x, y, w, h, fill = C.paper, line = fill, radius = false) {
  s.addShape(radius ? pptx.ShapeType.roundRect : pptx.ShapeType.rect, {
    x, y, w, h, rectRadius: 0.12,
    fill: { color: fill }, line: { color: line, width: 0.8 },
    radius: 0.12,
  });
}
function pill(s, value, x, y, w, dark = false) {
  box(s, x, y, w, 0.34, dark ? C.dark : C.pale, dark ? C.dark : C.pale, true);
  text(s, value, x + 0.11, y + 0.025, w - 0.22, 0.28, 10, {
    color: dark ? C.pink : C.rose, bold: true, charSpacing: 0.5,
  });
}
function circle(s, label, x, y, dark = false) {
  s.addShape(pptx.ShapeType.ellipse, {
    x, y, w: 0.48, h: 0.48,
    line: { color: dark ? C.pink : C.rose, transparency: 100 },
    fill: { color: dark ? C.pink : C.rose },
  });
  text(s, label, x, y + 0.02, 0.48, 0.42, 15, {
    bold: true, color: dark ? C.dark : C.paper, align: 'center',
  });
}
function arrow(s, x, y, w = 0.38, dark = false) {
  s.addShape(pptx.ShapeType.chevron, {
    x, y, w, h: 0.30,
    line: { color: dark ? C.pink : C.rose, transparency: 100 },
    fill: { color: dark ? C.pink : C.rose },
  });
}
function base(kicker, title, subtitle, source, dark = false) {
  const s = pptx.addSlide();
  s.background = { color: dark ? C.dark : C.bg };
  text(s, kicker.toUpperCase(), 0.6, 0.45, 11.9, 0.25, 10, {
    bold: true, charSpacing: 1.8, color: dark ? C.pink : C.rose,
  });
  text(s, title, 0.6, 0.85, 12.05, 1.23, 36, {
    fontFace: 'Segoe UI Semibold', bold: true, color: dark ? C.paper : C.ink,
  });
  if (subtitle) text(s, subtitle, 0.62, 2.22, 11.95, 0.50, 17, {
    color: dark ? C.light : C.muted,
  });
  text(s, source || '', 0.62, 6.78, 11.75, 0.23, 9, {
    color: dark ? C.light : C.muted,
  });
  text(s, 'MICROSOFT INTERNAL DISCUSSION  /  14 SEP 2026  /  NOT A COMMERCIAL SKU', 0.62, 7.08, 11.65, 0.2, 8, {
    color: dark ? C.light : C.muted, charSpacing: 0.3,
  });
  text(s, String(pptx._slides.length).padStart(2, '0'), 12.14, 7.03, 0.55, 0.28, 11, {
    align: 'right', color: dark ? C.pink : C.rose,
  });
  return s;
}
function notes(s, title, time, body, transition, refs = '') {
  const value = `${title}\nSuggested time: ${time}\n\n${body}\n\nTransition: ${transition}${refs ? `\n\nSources / qualifications: ${refs}` : ''}`;
  s.addNotes(value);
  sections.push({ number: sections.length + 1, title, time, body, transition, refs });
}
function card(s, x, y, w, h, number, title, body, footer) {
  box(s, x, y, w, h, C.paper, C.border, true);
  circle(s, number, x + 0.25, y + 0.25);
  text(s, title, x + 0.25, y + 0.94, w - 0.5, 0.9, 20, { bold: true });
  text(s, body, x + 0.25, y + 1.96, w - 0.5, 0.85, 16, { valign: 'top', color: C.muted });
  if (footer) text(s, footer, x + 0.25, y + h - 0.5, w - 0.5, 0.26, 11, { bold: true, color: C.rose });
}

// 01 - Opening thesis
{
  const s = base('PTU Accelerator / Internal strategy briefing', '', '', '', true);
  text(s, 'Useful AI first.\nCapacity that earns\nits place.', 0.62, 1.4, 8.25, 2.65, 49, {
    fontFace: 'Segoe UI Semibold', bold: true, color: C.paper, breakLine: false,
  });
  text(s, 'A focused solution portfolio to turn customer problems into\nadopted Azure workloads and defensible PTU decisions.', 0.65, 4.47, 8.0, 0.95, 21, {
    color: C.light,
  });
  pill(s, '14 SEPTEMBER 2026  /  2:00 PM', 0.65, 5.87, 3.53);
  const nodes = [
    ['01', 'CUSTOMER VALUE', 'A task worth repeating'],
    ['02', 'AZURE ADOPTION', 'A workflow people use'],
    ['03', 'CAPACITY DECISION', 'Renew, expand or rightsize'],
  ];
  nodes.forEach((n, i) => {
    const y = 1.66 + i * 1.52;
    box(s, 9.25, y, 3.42, 1.18, '343231', '474747', true);
    text(s, n[0], 9.48, y + 0.19, 0.46, 0.33, 17, { color: C.pink, bold: true });
    text(s, n[1], 10.06, y + 0.18, 2.36, 0.3, 11, { color: C.pink, bold: true });
    text(s, n[2], 10.06, y + 0.53, 2.3, 0.59, 16, { color: C.paper });
    if (i < 2) arrow(s, 10.7, y + 1.24, 0.32, true);
  });
  notes(s, 'Useful AI first. Capacity that earns its place.', '1 minute',
    'Opening: We are not proposing that customers buy PTUs and receive twenty production-ready applications. We are proposing a repeatable way to solve a few important business problems, get those workflows adopted on Azure, and then attach the model capacity the evidence supports.\n\nThe engineering exercise gave us useful building blocks and, just as importantly, a clear view of what is not ready. Today I want alignment on the focused offer, two candidate-account motions, and the delivery owners needed to turn this into a credible customer engagement.\n\nThis is internal working material, not an official Microsoft SKU, support promise or approved customer case study.',
    'Start with the customer friction, not the technology list.',
    'PTU-Bundle-Commercial-Recommendation.md, sections 1 and 10; evidence snapshot 12 September 2026.');
}

// 02 - Customer pain translated to outcomes
{
  const s = base('Customer problem', 'Customers need finished work, not another AI demo.',
    'Lead discovery with a recurring task, an accountable buyer and a measurable outcome.', sources.recommendation);
  const rows = [
    ['Knowledge & policy teams', 'Answers are scattered across documents.', 'Find, compare and draft with sources.'],
    ['Procurement & records teams', 'Evidence preparation slows review.', 'Prepare traceable review packages.'],
    ['Engineering & application owners', 'Legacy changes are hard to trust.', 'Understand, change and verify code.'],
  ];
  rows.forEach((r, i) => {
    const y = 2.98 + i * 1.05;
    box(s, 0.62, y, 12.04, 0.87, C.paper, C.border, true);
    circle(s, String(i + 1), 0.85, y + 0.2);
    text(s, r[0], 1.52, y + 0.16, 2.65, 0.56, 16, { bold: true });
    text(s, r[1], 4.43, y + 0.16, 3.52, 0.56, 16, { color: C.muted });
    arrow(s, 8.1, y + 0.29);
    text(s, r[2], 8.75, y + 0.16, 3.56, 0.56, 17, { bold: true });
  });
  pill(s, 'DISCOVERY GATE', 0.64, 6.32, 1.75);
  text(s, 'Confirm the gap beyond the customer\'s existing licensed products.', 2.59, 6.29, 9.63, 0.38, 16);
  notes(s, 'Customers need finished work, not another AI demo.', '1 minute',
    'The entry point is an unfinished business task. A policy analyst needs a trustworthy comparison and briefing. A procurement reviewer needs a defensible evidence package. An application owner needs a change that survives execution tests.\n\nAsk who owns the task, how often it happens, what the current process costs, what makes an output acceptable, and why existing Microsoft 365 Copilot, Copilot Studio, GitHub Copilot or conventional search does not already meet the requirement. These are target problems, not verified customer savings claims.\n\nA high-value task does not automatically have enough sustained traffic to justify PTUs.',
    'Package those needs into three understandable outcomes, not twenty separate products.');
}

// 03 - Portfolio architecture
{
  const s = base('The proposed offer', 'Three outcome bundles. One governed foundation.',
    'A field-and-partner delivery offer assembled from selected building blocks.', sources.recommendation);
  card(s, 0.62, 2.92, 3.85, 3.36, '1', 'Knowledge &\nStaff Work',
    'Trusted answers, document comparison and controlled source-backed drafts.', 'ANCHORS: CWYD + DKM');
  card(s, 4.74, 2.92, 3.85, 3.36, '2', 'Procurement &\nDocument Operations',
    'Intake, missing-evidence checks and human-reviewed contract / RFP evidence.', 'BUILDING BLOCK: CONTENT PROCESSING');
  card(s, 8.86, 2.92, 3.85, 3.36, '3', 'Engineering\nModernization',
    'Code understanding, specifications and execution-verified modernization.', 'MODERNIZE + OWNER-APPROVED SPECSUITE');
  text(s, 'SHARED FOUNDATION   Identity  /  approved data  /  model routing  /  evaluation  /  cost and capacity operations',
    0.65, 6.43, 12.0, 0.23, 11, { bold: true, color: C.rose });
  notes(s, 'Three outcome bundles. One governed foundation.', '1 minute',
    'Knowledge and Staff Work is the broad adoption anchor. Procurement and Document Operations turns document intelligence into reviewer-ready evidence. Engineering Modernization is a strong program-led motion when there is an engineering sponsor.\n\nCWYD means Chat With Your Data; DKM means Document Knowledge Mining. These are building blocks, not a promise that the entire bundle is already implemented. Controlled drafting and contract/RFP review need implementation and acceptance. SpecSuite remains conditional on its owner, licensing and delivery/support agreement; we did not retest it.\n\nThe common foundation should reuse the customer\'s approved platform where practical. We should not create twenty disconnected frontends or a large new landing zone for every small use case.',
    'The lab has given us a useful starting point, with a very specific evidence boundary.');
}

// 04 - What was actually done
{
  const s = base('What we did', 'We turned a broad catalog into an evidence-led shortlist.',
    'Recorded lab work used synthetic data and Standard / GlobalStandard models, not provisioned capacity.', sources.evidence);
  const counts = [
    ['20', 'candidates assessed', 'Across the combined portfolio review'],
    ['7', 'first-pass app tracks', 'Selected functional evaluation scopes'],
    ['0', 'PTU benchmarks', 'No PTUs or reservations purchased'],
  ];
  counts.forEach((c, i) => {
    const x = 0.62 + i * 4.12;
    box(s, x, 2.98, 3.81, 2.30, i === 2 ? C.pale : C.paper, i === 2 ? C.pale : C.border, true);
    text(s, c[0], x + 0.25, 3.05, 3.3, 1.13, 66, { bold: true, color: C.rose });
    text(s, c[1], x + 0.25, 4.17, 3.3, 0.4, 21, { bold: true });
    text(s, c[2], x + 0.25, 4.68, 3.3, 0.42, 13, { color: C.muted });
  });
  box(s, 0.62, 5.62, 12.04, 0.84, C.dark, C.dark, true);
  text(s, 'Reusable outputs', 0.9, 5.87, 2.2, 0.3, 18, { bold: true, color: C.pink });
  text(s, 'Pinned adaptations  /  bounded-test evidence  /  runbooks  /  curated public website', 3.1, 5.82, 9.12, 0.42, 17, { color: C.paper });
  notes(s, 'We turned a broad catalog into an evidence-led shortlist.', '1 minute',
    'The combined review assessed all twenty original candidates, but that is not twenty successful deployments. Seven accelerator repositories were assigned to first-pass implementation tracks. Existing SpecSuite and Planetary Explorer applications were protected and inventoried rather than retested.\n\nWe exercised selected native workflows, retained reusable adaptations and evaluation evidence, and separated customer-safe messaging into a static website. The strongest first-pass results were selected CWYD, DKM and Modernize workflows; Content had a limited missing-document success.\n\nNo provisioned throughput or reservations were purchased. Standard and GlobalStandard results tell us about selected functionality and model demand, not provisioned utilization, customer economics or production scale. Historical inference allowances are closed.',
    'That gives us enough to focus delivery, not enough to promise a turnkey bundle.',
    'reports/ptu-bundle-evaluation.md sections 1-3; PTU-Bundle-Commercial-Recommendation.md section 4; adaptations/README.md and root README.md.');
}

// 05 - Evidence maturity
{
  const s = base('Readiness, honestly', 'Show the selected passes. Fund the gaps.',
    'A successful request or deployed resource is not the same as a successful business journey.', sources.evidence);
  const bands = [
    ['SELECTED TEST PASSES', 'CWYD, DKM, Modernize', 'Guided evidence walkthroughs; hosted, scale and quality limits remain.'],
    ['LIMITED / PARTIAL', 'Content, MACAE, Chatbot, Conversation', 'Content: missing-document path only. Other central failures remain.'],
    ['CONDITIONAL / PLANNED', 'SpecSuite, controlled drafts, contract review', 'Owner gates or implementation required; not customer-ready claims.'],
  ];
  bands.forEach((r, i) => {
    const y = 2.96 + i * 1.05;
    box(s, 0.62, y, 12.04, 0.9, C.paper, C.border, true);
    pill(s, r[0], 0.86, y + 0.26, 2.66);
    text(s, r[1], 3.8, y + 0.16, 3.5, 0.6, 17, { bold: true });
    text(s, r[2], 7.61, y + 0.13, 4.76, 0.63, 15, { color: C.muted });
  });
  text(s, 'Meeting-safe demo: use the static portfolio and the evidence story. Do not restart the lab.', 0.66, 6.29, 12.0, 0.36, 16, { bold: true, color: C.rose });
  notes(s, 'Show the selected passes. Fund the gaps.', '1 minute',
    'Be explicit if anyone asks what can be demonstrated today. CWYD passed eight selected criteria in an adapted local runtime; it was not a hosted production acceptance. DKM demonstrated ingestion, cited QA and comparison on two of ten fixtures, with no full browser journey. Modernize passed a selected upload/process/download API flow, not actual source-to-target database equivalence.\n\nContent correctly flagged missing evidence but its full happy path did not pass. MACAE final synthesis, the chatbot grounded answer, and Conversation semantics still had important failures. We should not demonstrate those as ready-to-run customer solutions.\n\nToday use the static website and an honest evidence walkthrough. The lab is paused/disarmed and no new inference has been authorized. A future live demo needs a separately approved run, a fixed scenario and a verified starting state.',
    'Here is the business workflow we should build next.');
}

// 06 - Customer storyboard
{
  const s = base('Priority build / illustrative workflow', 'From approved sources to a reviewer-ready briefing.',
    'Proposed Knowledge & Staff Work journey. This end-to-end drafting workbench is not yet implemented.', sources.planned);
  const steps = [
    ['Select', 'Approved sources\n+ briefing template'],
    ['Ground', 'Retrieve evidence\n+ show uncertainty'],
    ['Draft', 'Cited first draft\n+ version comparison'],
    ['Approve', 'Human review\n+ controlled export'],
  ];
  steps.forEach((r, i) => {
    const x = 0.62 + i * 3.13;
    box(s, x, 3.18, 2.64, 2.44, C.paper, C.border, true);
    circle(s, String(i + 1), x + 0.25, 3.44);
    text(s, r[0], x + 0.25, 4.11, 2.14, 0.43, 24, { bold: true });
    text(s, r[1], x + 0.25, 4.73, 2.14, 0.62, 15, { color: C.muted });
    if (i < 3) arrow(s, x + 2.74, 4.24, 0.27);
  });
  text(s, 'Acceptance', 0.66, 6.03, 1.67, 0.38, 18, { bold: true, color: C.rose });
  text(s, 'Correct citations  /  safe no-answer behavior  /  permission boundaries  /  reviewer acceptance', 2.39, 6.03, 10.0, 0.42, 17);
  notes(s, 'From approved sources to a reviewer-ready briefing.', '1 minute',
    'Tell a simple hypothetical story: a policy analyst needs to compare two approved policy versions and prepare an options briefing. Instead of searching several systems and pasting into a blank chat, they select approved sources and a governed template. The application retrieves the relevant evidence, produces a cited draft, exposes uncertainties and changes, and routes it for human approval.\n\nThe business outcome is the approved work product, not the generated text. Measure accepted drafts, reviewer effort and factual corrections against the current process. This is a proposed next build extending knowledge-workbench components, not an implemented capability or a customer case study. The compiled marketing-content repository is not evidence that this controlled drafting workflow exists.\n\nThe reviewer retains the decision, and export must preserve citations and document/version provenance.',
    'The workflow creates demand; the platform must route and govern it correctly.',
    'PTU-Bundle-Commercial-Recommendation.md section 6, priority addition 1.');
}

// 07 - Routing and cost architecture
{
  const s = base('How Azure fits', 'One experience. Clear routes. Separate costs.',
    'Share compatible deployed model endpoints, not an interchangeable all-model PTU pool.', sources.motion);
  box(s, 0.62, 3.0, 3.1, 2.48, C.paper, C.border, true);
  text(s, 'Customer workflows', 0.9, 3.28, 2.56, 0.44, 19, { bold: true });
  text(s, 'Knowledge + staff work\nDocument operations\nEngineering changes', 0.9, 4.0, 2.56, 1.0, 16, { color: C.muted });
  arrow(s, 3.89, 4.02);
  box(s, 4.46, 3.0, 3.22, 2.48, C.dark, C.dark, true);
  text(s, 'Governed routing', 4.72, 3.28, 2.72, 0.44, 23, { bold: true, color: C.paper });
  text(s, 'Identity + permissions\nQuality + attribution\nPriority + headroom', 4.72, 4.0, 2.72, 1.0, 16, { color: C.light });
  arrow(s, 7.86, 4.02);
  box(s, 8.44, 2.97, 4.23, 1.22, C.pale, C.pale, true);
  text(s, 'Provisioned model', 8.69, 3.14, 3.74, 0.42, 22, { bold: true, color: C.rose });
  text(s, 'Verify model, API, version\nand processing geography.', 8.69, 3.62, 3.7, 0.43, 12);
  box(s, 8.44, 4.47, 4.23, 1.01, C.paper, C.border, true);
  text(s, 'Standard / Batch / other', 8.69, 4.6, 3.73, 0.36, 18, { bold: true });
  text(s, 'Use when justified; meter separately.', 8.69, 5.05, 3.7, 0.26, 13, { color: C.muted });
  box(s, 0.62, 5.9, 12.04, 0.67, C.paper, C.border, true);
  text(s, 'Separately billed as used:  hosting  /  search  /  storage  /  OCR  /  speech  /  embeddings  /  operations',
    0.9, 6.08, 11.5, 0.3, 16, { color: C.muted });
  notes(s, 'One experience. Clear routes. Separate costs.', '1 minute',
    'PTUs cover compatible model inference, not the whole application. We need to verify the actual provider endpoint, model and version, API, deployment type and processing geography. Two applications using different models or trust boundaries may need separate capacity groups.\n\nThe platform layer should attribute successful tasks and model demand per application, protect interactive service objectives with admission control, and use only approved, separately metered alternatives or spillover. No automatic routing or fallback is implied by this conceptual diagram.\n\nSearch, hosting, OCR, speech, embeddings on other deployments, storage and implementation remain separate cost lines. Azure adoption can grow through useful application services even when the right model option remains Standard or Batch. Do not double-count provider usage, billable spend or already committed capacity.\n\nReservations provide matching financial coverage, not a guarantee of deployable capacity or one runtime pool.',
    'That is why customers who already have PTUs need a different motion from new buyers.');
}

// 08 - Two commercial motions
{
  const s = base('Commercial motion', 'Two capacity situations. Two sales motions.',
    'The goal is useful customer demand, not artificial utilization.', sources.motion);
  const columns = [
    [0.62, 'A', 'Customer already has PTUs', 'ADOPT  /  PROTECT  /  RENEW',
      'Inventory compatible models and headroom.\nLand one workload; protect current service levels.\nExpand only when valuable demand justifies it.',
      'Success may be renewal confidence or rightsizing.'],
    [6.81, 'B', 'Customer is considering PTUs', 'PROVE  /  MEASURE  /  SIZE',
      'Prove the workflow and pass acceptance tests.\nMeasure per-model load and peak concurrency.\nCompare provisioned with Standard and Batch.',
      'A low-volume pilot can remain on Standard.'],
  ];
  columns.forEach(([x, n, title, label, body, foot]) => {
    box(s, x, 2.96, 5.87, 3.58, C.paper, C.border, true);
    circle(s, n, x + 0.26, 3.21);
    text(s, title, x + 0.96, 3.22, 4.58, 0.46, 23, { bold: true });
    text(s, label, x + 0.27, 3.98, 5.3, 0.26, 11, { bold: true, color: C.rose });
    text(s, body, x + 0.27, 4.44, 5.27, 1.39, 16, { valign: 'top', paraSpaceAfter: 9 });
    text(s, foot, x + 0.27, 6.0, 5.29, 0.34, 14, { color: C.rose, bold: true });
  });
  notes(s, 'Two capacity situations. Two sales motions.', '1 minute',
    'For an existing-PTU customer, start by understanding actual deployments, workloads, renewal timing and headroom. A compatible additional request within headroom generally does not add another PTU-hour when that capacity remains allocated anyway, but application and other service costs still apply. Protect current users and measure useful outcomes.\n\nFor a new buyer, the hurdle is different. Prove the application, capture realistic per-model demand and compare equivalent quality and service objectives across provisioned, Standard and eligible Batch. Do not force PTUs into a small pilot.\n\nAdopting idle capacity is not the same as selling additional capacity. It can support renewal, but an oversized allocation should still be rightsized. Expansion is justified only by sustained additional valuable demand or a demonstrated capacity constraint.',
    'This is how customer value translates into credible Azure growth.');
}

// 09 - Revenue logic
{
  const s = base('Growth logic', 'Turn customer value into Azure growth.',
    'Commercial hypothesis, not a forecast: count only useful, adopted and attributable demand.', sources.motion);
  const steps = [
    ['Land', 'One accepted workflow', 'Application services +\napproved model usage'],
    ['Adopt', 'Repeat use by real users', 'Useful demand within\ncompatible headroom'],
    ['Expand', 'More accepted workflows', 'Additional capacity only\nwhen demand supports it'],
    ['Renew', 'Outcome and cost review', 'Retain, expand or\nrightsize responsibly'],
  ];
  steps.forEach((r, i) => {
    const x = 0.62 + i * 3.13;
    text(s, String(i + 1).padStart(2, '0'), x, 3.01, 2.3, 0.8, 46, { bold: true, color: C.rose });
    text(s, r[0], x, 3.95, 2.65, 0.49, 28, { bold: true });
    text(s, r[1], x, 4.65, 2.65, 0.58, 17, { bold: true });
    text(s, r[2], x, 5.42, 2.65, 0.69, 16, { color: C.muted });
    if (i < 3) arrow(s, x + 2.73, 4.09, 0.28);
  });
  text(s, 'Do not optimize for tokens. Optimize for successful tasks, adoption, service objectives and full cost.', 0.64, 6.35, 12.0, 0.3, 16, { bold: true, color: C.rose });
  notes(s, 'Turn customer value into Azure growth.', '1 minute',
    'There are three distinct commercial effects. First, a useful application can create Azure service usage and appropriate model consumption. Second, adoption on existing compatible PTUs can improve value realization and renewal confidence. Third, additional adopted demand may justify a new or expanded provisioned deployment.\n\nDo not add those up as if they were all incremental PTU revenue. The lab does not support a dollar forecast, a savings percentage or a PTU quantity. Partners can provide scoped implementation and operations, but those services are not an automatic Microsoft support commitment.\n\nOur internal scorecard should connect each account to a successful workflow and an evidence-based next decision. More repositories, more agents and more tokens are not business success metrics.',
    'We win by being more specific about outcomes and more credible about proof.');
}

// 10 - Differentiation
{
  const s = base('How we win customers', 'Win with useful workflows and inspectable proof.',
    'Do not rebuild an existing licensed experience without a demonstrable gap.', sources.motion);
  const rows = [
    ['Fit', 'Start with their process, corpus and control requirements.', 'WHY THIS, NOT ANOTHER CHATBOT?'],
    ['Trust', 'Show source evidence, failure behavior and human decisions.', 'CAN THE TEAM RELY ON THE OUTPUT?'],
    ['Delivery', 'Name the implementation owner, support and acceptance tests.', 'WHO MAKES THIS WORK AFTER THE DEMO?'],
    ['Economics', 'Compare full cost per successful task at the target service level.', 'WHY THIS CAPACITY CHOICE?'],
  ];
  rows.forEach((r, i) => {
    const y = 2.98 + i * 0.88;
    circle(s, String(i + 1), 0.64, y + 0.06);
    text(s, r[0], 1.32, y + 0.04, 1.52, 0.45, 20, { bold: true });
    text(s, r[1], 3.0, y, 5.34, 0.63, 17);
    text(s, r[2], 8.74, y + 0.03, 3.8, 0.54, 11, { color: C.rose, bold: true });
  });
  notes(s, 'Win with useful workflows and inspectable proof.', '1 minute',
    'Do not pitch custom development as inherently better than Microsoft 365 Copilot, Copilot Studio, GitHub Copilot or Purview. Qualify an unmet workflow, integration, corpus, evidence schema or operational-control requirement. If an existing product meets the need with lower lifecycle cost, use it.\n\nOur differentiation is a focused business workflow with inspectable evidence, an accountable delivery model and a capacity decision tied to reality. For procurement, people retain award and legal decisions. For engineering, tests and human review retain change authority. For regulated accounts, data classification, network and identity approvals, processing geography and retention remain separate gates; PTUs confer none of those approvals.\n\nName the implementer and the operator before promising a production engagement.',
    'A short gated engagement is the practical way to prove this, not another portfolio sweep.');
}

// 11 - Engagement plan
{
  const s = base('Proposed execution', 'A 30-day qualification sprint, with decision gates.',
    'Suggested sequence only. Timing depends on approved access, owners, data and capacity availability.', sources.planned);
  const stages = [
    ['WEEK 1', 'Qualify', 'Sponsor + task\nBaseline + product gap', 'Account team + customer owner'],
    ['WEEK 2', 'Prove', 'Evaluation set\nEnd-to-end acceptance', 'Engineering + delivery partner'],
    ['WEEK 3', 'Measure', 'Model load + SLOs\nFull-cost comparison', 'CSA + capacity / economics lead'],
    ['WEEK 4', 'Decide', 'Pilot + support owner\nCapacity recommendation', 'Customer sponsor + account team'],
  ];
  stages.forEach((r, i) => {
    const x = 0.62 + i * 3.13;
    pill(s, r[0], x, 3.08, 1.08);
    box(s, x, 3.69, 2.65, 2.65, C.paper, C.border, true);
    text(s, r[1], x + 0.23, 3.98, 2.19, 0.46, 25, { bold: true });
    text(s, r[2], x + 0.23, 4.61, 2.18, 1.04, 15, { color: C.muted });
    text(s, r[3], x + 0.23, 5.77, 2.18, 0.37, 11, { color: C.rose, bold: true });
    if (i < 3) arrow(s, x + 2.76, 4.57, 0.25);
  });
  notes(s, 'A 30-day qualification sprint, with decision gates.', '1 minute',
    'This is a proposed engagement sequence, not a guaranteed delivery date or a funded plan. In week one, qualify the problem and the existing-product gap with a sponsor. In week two, agree a representative evaluation set and demonstrate the end-to-end journey, including error and permission cases. In week three, measure actual model-specific demand and compare alternatives at the same service objective and quality. Week four produces a documented capacity recommendation, pilot scope and operating owner.\n\nEvery gate can produce a no-go, more engineering work, or a Standard/Batch recommendation. If data or landing-zone approvals are missing, the work remains prerequisite-gated; do not work around them. Any new lab inference or capacity test needs explicit authorization and a bounded cost allowance.\n\nStart with one broad daily workflow and one complementary workflow, not all three bundles at once.',
    'Make success visible in one shared scorecard.');
}

// 12 - Measures
{
  const s = base('Shared scorecard', 'Measure business success before capacity expansion.',
    'Agree account-specific baselines and thresholds before the pilot. No achieved customer metrics are claimed here.', sources.motion);
  const cells = [
    [0.62, 2.99, '01', 'Customer outcome', 'Reviewer time, accepted work products,\nfactual corrections and task completion.'],
    [6.81, 2.99, '02', 'Adoption', 'Active users, repeat use and\nproduction-accepted workflows.'],
    [0.62, 4.84, '03', 'Operational fit', 'Per-model demand, peak concurrency,\ntail latency, errors and useful headroom.'],
    [6.81, 4.84, '04', 'Commercial decision', 'Full cost per successful task;\nrenewal, expansion or rightsizing rationale.'],
  ];
  cells.forEach(([x, y, n, title, body]) => {
    box(s, x, y, 5.86, 1.59, C.paper, C.border, true);
    circle(s, n, x + 0.25, y + 0.24);
    text(s, title, x + 0.96, y + 0.23, 4.62, 0.4, 23, { bold: true });
    text(s, body, x + 0.96, y + 0.81, 4.62, 0.6, 16, { color: C.muted });
  });
  notes(s, 'Measure business success before capacity expansion.', '1 minute',
    'Agree the baseline and thresholds with the customer before a pilot. Track time to an accepted artifact, task quality and reviewer corrections. Then track repeat use and accepted workflows, rather than registrations or raw requests.\n\nOperational measurement must be per model, with actual input/output lengths, cache behavior, calls per task, retries, peak concurrency and tail latency. Capture supporting-service and operating costs as well as model costs. Cost per successful task should use accepted tasks as the denominator, not all generated answers.\n\nFor commercial tracking, separate new Azure usage from already committed PTU spend. Record the decision and why it follows from the evidence: retain, expand, rightsize, or continue on Standard/Batch. These are proposed measures, not achieved customer results.',
    'Close with a concrete decision request for this group.');
}

// 13 - Clear ask
{
  const s = base('Decision requested today', 'Back the focused offer.\nGive the first two motions owners.', '', '', true);
  const asks = [
    ['1', 'Align on the offer', 'Three outcome bundles; knowledge + controlled drafting first.'],
    ['2', 'Nominate two accounts', 'One existing-PTU adoption motion; one new-demand qualification.'],
    ['3', 'Name accountable owners', 'Account lead, engineering / partner, operations and capacity lead.'],
  ];
  asks.forEach((r, i) => {
    const y = 2.88 + i * 0.96;
    circle(s, r[0], 0.67, y + 0.09, true);
    text(s, r[1], 1.4, y + 0.05, 4.45, 0.46, 23, { bold: true, color: C.paper });
    text(s, r[2], 6.23, y + 0.02, 6.1, 0.66, 18, { color: C.light });
  });
  box(s, 0.66, 6.02, 12.0, 0.57, C.pink, C.pink, true);
  text(s, 'Next output: an account-specific pilot scope, acceptance gates and a responsible capacity decision.',
    0.91, 6.16, 11.5, 0.29, 16, { bold: true, color: C.dark });
  notes(s, 'Back the focused offer. Give the first two motions owners.', '1 minute',
    'Close: My ask is not approval to buy capacity today. It is alignment on a focused three-bundle offer, two candidate account motions and the accountable people to execute them. Lead with knowledge and controlled drafting. Nominate one account with compatible existing PTUs and one account where a new production demand case can be measured.\n\nName an account lead, an engineering or delivery partner lead, an operating owner and a capacity/economics lead. Those are roles to assign, not people already committed. The next deliverable is an account-specific pilot scope with acceptance gates, a costed operating model and a defensible capacity recommendation.\n\nFinal line: We earn the capacity conversation by solving the customer\'s problem first.',
    'Open discussion; use the appendix for readiness, economics and source questions.');
}

// 14 - Appendix evidence
{
  const s = base('Appendix A / evidence detail', 'What the strongest recorded tests actually establish.',
    'Evidence snapshot: 12 September 2026. These are bounded synthetic tests, not production acceptance.', sources.evidence);
  const items = [
    ['CWYD', '8/8 selected criteria', 'Adapted local runtime; Azure Functions hosting unexercised.'],
    ['Document Knowledge Mining', 'Ingestion, QA, comparison', '2/10 fixtures; summary defect; no full browser journey.'],
    ['Modernize Your Code', 'Native API upload / process / download', 'No real source / target database equivalence; browser access limited.'],
    ['Content Processing', 'Native missing-document scenario', 'Full happy path unpassed; provider-filter warning unresolved.'],
  ];
  items.forEach((r, i) => {
    const y = 3.0 + i * 0.85;
    box(s, 0.62, y, 12.05, 0.71, C.paper, C.border, true);
    text(s, r[0], 0.85, y + 0.08, 2.91, 0.56, 16, { bold: true });
    text(s, r[1], 3.99, y + 0.1, 3.42, 0.49, 15, { color: C.rose, bold: true });
    text(s, r[2], 7.72, y + 0.07, 4.68, 0.56, 14, { color: C.muted });
  });
  text(s, 'SpecSuite / Planetary: inventory only. Voice Live PTU BYOM: documented route, not tested here.', 0.66, 6.48, 12.0, 0.22, 12, { bold: true, color: C.rose });
  notes(s, 'What the strongest recorded tests actually establish.', 'Appendix / as needed',
    'Use this page if asked whether the bundle is production-ready. The answer is no: selected scopes passed, and the limitations matter. CWYD ran in an adapted local runtime. DKM tested only two fixtures and had no full browser journey. Modernize\'s selected translation flow is not source-to-target execution equivalence. Content had a limited negative/missing-document success, not its complete happy path.\n\nThe other first-pass apps retained central workflow or semantic failures. Existing SpecSuite and Planetary were inventory-only. Voice Live has a documented customer-PTU BYOM route, but our four managed-model probes were text-mode component checks, not speech, telephony or PTU BYOM acceptance.\n\nDo not reuse the earlier categorical claim that Voice Live cannot use customer PTUs. The commercial recommendation qualifies and corrects that claim.',
    'If the question is PTU sizing or savings, use the economics gates instead of extrapolating these tests.',
    'reports/ptu-bundle-evaluation.md sections 1-3; PTU-Bundle-Commercial-Recommendation.md sections 2 and 4; Voice Live source listed in Appendix C.');
}

// 15 - Appendix economics
{
  const s = base('Appendix B / capacity economics', 'No fixed PTU quantity or savings claim from this lab.',
    'Compare equivalent quality, service objectives, processing geography and measurement periods.', sources.motion);
  const entries = [
    ['PROVISIONED OPTION', 'Capacity cost + other-model / spillover inference\n+ application services + implementation + operations'],
    ['ALTERNATIVE OPTION', 'Standard + eligible Batch / specialized services\n+ comparable application and delivery costs'],
  ];
  entries.forEach((r, i) => {
    const y = 3.02 + i * 1.2;
    box(s, 0.62, y, 12.04, 0.95, i === 0 ? C.pale : C.paper, i === 0 ? C.pale : C.border, true);
    text(s, r[0], 0.9, y + 0.27, 2.62, 0.34, 13, { bold: true, color: C.rose });
    text(s, r[1], 3.92, y + 0.16, 8.43, 0.64, 18);
  });
  text(s, 'Size from real demand', 0.66, 5.65, 4.06, 0.40, 22, { bold: true });
  text(s, 'Model-specific tokens, cache and output treatment, peaks,\nminimum sizes, headroom and realistic adoption.', 5.0, 5.61, 7.45, 0.68, 16, { color: C.muted });
  text(s, 'Reservation coverage is not deployable capacity. Confirm availability before buying matching coverage.', 0.66, 6.46, 12.0, 0.24, 12, { bold: true, color: C.rose });
  notes(s, 'No fixed PTU quantity or savings claim from this lab.', 'Appendix / as needed',
    'There is no reliable portfolio-wide token-to-PTU multiplier. Use model-specific output weighting, caching, minimum deployment sizes, duty cycle, peak overlap and headroom. The StepFly cache sample is not a general sizing correction. Measure useful demand and compare at a consistent quality and service objective.\n\nA reservation is financial coverage subject to the current matching rules; it does not guarantee capacity availability. Confirm deployment availability and current commercial terms before recommending matching coverage. Do not quote a price, savings percentage or fixed PTU number from this presentation.\n\nPTUs do not improve the same model\'s inherent answer quality, guarantee end-to-end application latency, repair retrieval, replace identity controls or provide security accreditation. Where Batch or Standard is better, recommend it.',
    'Refer to current product documentation at quotation time.',
    'PTU-Bundle-Commercial-Recommendation.md sections 2, 3 and 9; Microsoft provisioned throughput concepts and billing documentation.');
}

// 16 - Sources and demo
{
  const s = base('Appendix C / references and meeting navigation', 'Evidence behind the story. A safe way to show it.',
    'Local reports are internal. The website is a separately curated, public-safe publication.', '');
  box(s, 0.62, 2.98, 5.88, 3.48, C.paper, C.border, true);
  text(s, 'Internal evidence basis', 0.89, 3.24, 5.3, 0.4, 23, { bold: true });
  text(s, 'Commercial recommendation\n12 September 2026; corrects earlier conclusions.\n\nFirst-pass evaluation + continuation report\nSelected results and material limitations.', 0.89, 3.98, 5.26, 1.77, 17, { color: C.muted });
  text(s, 'Exact file references and links are in speaker notes.', 0.89, 6.0, 5.25, 0.25, 12, { color: C.rose, bold: true });
  box(s, 6.79, 2.98, 5.88, 3.48, C.dark, C.dark, true);
  text(s, '2-minute website walkthrough', 7.06, 3.24, 5.35, 0.4, 23, { bold: true, color: C.paper });
  text(s, '1  Overview: the three customer outcomes.\n2  Solutions: one candidate and its evidence limits.\n3  PTU guide: existing versus new capacity.\n4  Next steps: controlled drafts are planned.', 7.06, 3.99, 5.29, 1.69, 17, { color: C.light, paraSpaceAfter: 10 });
  text(s, 'Use the local built site; no inference or lab restart.', 7.06, 6.0, 5.29, 0.25, 12, { color: C.pink, bold: true });
  const refs = [
    'Internal: PTU-Bundle-Commercial-Recommendation.md (12 September 2026), especially sections 1-6 and 9-10.',
    'Internal: reports\\ptu-bundle-evaluation.md (12 September 2026), sections 1-3.',
    'Internal: PTU-Bundle-Continuation-Report.md; interpret with the commercial recommendation\'s corrections.',
    'Public: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput',
    'Public: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput-billing',
    'Public: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-bring-your-own-model',
    'Website: https://blue-beach-0fb8cd70f.5.azurestaticapps.net/',
    'Public documentation was recorded as checked on 12 September 2026 by the recommendation; not independently refreshed for this deck. Reconfirm at quotation time.',
  ];
  notes(s, 'Evidence behind the story. A safe way to show it.', 'Appendix / optional 2-minute walkthrough',
    'Use the rebuilt local site for the updated design unless publication has separately been confirmed. From this presentation folder, open ..\\site\\dist\\index.html. Website source changes are not automatically evidence that the hosted site has changed.\n\nWalk through Overview, open Solutions and inspect one selected-pass candidate, then use the PTU guide to explain existing versus new capacity. Finish on Next steps and make clear that controlled drafts are a proposed implementation. This is an informational portfolio demonstration, not a live accelerator execution.\n\nIf the browser is unavailable, use slides 3, 5 and 8. Do not open raw evidence, deployment inventories or operational consoles on the shared screen. Keep the deck and talking points outside site\\dist.',
    'Return to slide 13 for the decision.',
    refs.join('\n'));
}

const quickStart = `# PTU Accelerator - internal meeting talking points

**Meeting:** 14 September 2026, 2:00 PM. **Audience:** Microsoft internal account, solution and delivery stakeholders.
**Format:** 13-slide main story (about 13 minutes), optional 2-minute static website walkthrough, then discussion. Slides 14-16 are appendix.
**Evidence:** Recorded 12 September 2026 results; no new deployment, inference, customer reference validation or PTU benchmark.
**Internal only:** Do not publish this document or the deck in the website.

## 60-second opening

We are not offering twenty production-ready apps with a PTU purchase. We are building a focused way to help customers solve recurring knowledge, document and engineering problems on Azure. Our evaluation identified useful building blocks, tested selected workflows and made the remaining gaps explicit. The commercial path is to prove the outcome, get it adopted and attach the capacity its real demand supports. For customers with existing PTUs, that starts with value realization and renewal; for new buyers, it starts with functional proof and a fair Standard, Batch and provisioned comparison. Today I want alignment on the three-bundle offer, two candidate account motions and the delivery owners to take the next gated step.

## Meeting preparation

- Open \`PTU-Accelerator-Internal-2026-09-14.pptx\`; use PowerPoint Presenter View for the embedded notes.
- Keep \`PTU-Accelerator-Internal-2026-09-14.pdf\` as the slide-only backup.
- Open \`..\\site\\dist\\index.html\` for the updated local website. The hosted URL may still show the previous version until the normal publication workflow runs.
- Show only the static site and this deck. No live model calls, lab restart, raw operational evidence or resource inventory.
- If time is reduced to five minutes, use slides 1, 3, 4, 8 and 13.
- End by assigning roles and next outputs, not by asking for a capacity purchase today.

## Slide-by-slide delivery

`;
const qa = `
## Acronyms to explain once

PTU: Provisioned Throughput Unit, a unit of compatible model-serving capacity.
CWYD: Chat With Your Data. DKM: Document Knowledge Mining.
SLO: service-level objective, such as a target response time under a defined load.
CSA: Cloud Solution Architect. BYOM / BYOK: bring your own model / key; actual routing depends on the product path.

## Likely questions and recommended answers

**Is this an official Microsoft SKU or a supported turnkey bundle?**
No. It is a proposed field-and-partner delivery offer using selected accelerator components. Scope, licensing, ownership and post-go-live support must be explicitly agreed.

**What can we actually show today?**
The static portfolio and a walkthrough of recorded selected CWYD, DKM and Modernize results, with limits. The lab is paused/disarmed. A fresh live application demo requires separate approval and a verified setup. Do not describe the website as running the accelerators.

**Why not Microsoft 365 Copilot, Copilot Studio or GitHub Copilot?**
Use those when they meet the need. Qualify an unmet workflow, corpus, evidence, integration or operating-control requirement before recommending a custom application. Accelerator source availability alone is not a reason to rebuild.

**How does this increase Azure usage and PTU purchases?**
Useful deployed workflows can create application-service and model usage. Existing-PTU adoption improves value realization and may support renewal. Additional PTU purchases follow only when adopted, compatible workloads justify added capacity. These are distinct effects, not a forecast and not interchangeable revenue.

**Why not simply fill all idle PTUs with background jobs?**
Only admit useful approved work within measured headroom, priorities and cost budgets. Protect interactive users. Delay-tolerant work needs a Batch comparison; rightsizing may be the right renewal decision. Artificial token generation is not customer value.

**How much capacity or savings can we quote?**
None from this lab. Measure per-model workload, quality, cache and output treatment, peaks, concurrency, duty cycle, headroom and full-stack costs. Compare equivalent Standard, eligible Batch and provisioned options, then confirm capacity availability and current terms.

**Does a PTU purchase make the apps free or more accurate?**
No. It is model-serving capacity, not the application, search, OCR, speech, other model deployments, licensing or delivery. It does not inherently improve the same model's answer quality or guarantee end-to-end latency.

**Can all apps use one PTU pool?**
Only compatible requests can share a deployed model endpoint. Different models, API requirements, processing geography or trust boundaries can require separate groups. Reservation financial coverage is not one all-model runtime pool.

**What about Voice Live and developer BYOK?**
The recommendation records a documented Voice Live customer-PTU BYOM path, but the lab did not test it; managed text probes do not establish an audio journey. BYOK paths depend on the client, feature, licensing, policy, network and model configuration. Neither is a blanket customer-PTU routing guarantee.

**What would we build first?**
A controlled, source-backed drafting workflow on the selected knowledge workbench. Pair it with procurement evidence review or engineering work only where a sponsor and acceptance criteria exist. These are proposed builds, not currently demonstrated complete workflows.

**What about regulated customers and Canadian residency?**
Data classification, processing geography, identity/network approvals, retention, bilingual/accessibility needs and an accountable operating model are prerequisites. A Canadian resource address or private endpoint is not proof of Canadian-only model processing. This synthetic lab is not a customer accreditation.

## Close and record decisions

1. Agree whether the three-bundle framing and knowledge/drafting priority are the right focused offer.
2. Nominate one existing-PTU and one new-demand candidate account; these are nominations, not confirmed customers.
3. Assign account, engineering/partner, operations and capacity/economics roles.
4. Agree the next output: account-specific scope, prerequisites, acceptance thresholds and a costed capacity decision.

**Closing line:** We earn the capacity conversation by solving the customer's problem first.
`;

async function main() {
  await pptx.writeFile({ fileName: path.join(out, 'PTU-Accelerator-Internal-2026-09-14.pptx') });
  const talking = quickStart + sections.map(s =>
    `### ${s.number}. ${s.title}\n\n**Timing:** ${s.time}\n\n${s.body}\n\n**Transition:** ${s.transition}\n${s.refs ? `\n**Sources / qualifications:** ${s.refs}\n` : ''}`
  ).join('\n') + qa;
  fs.writeFileSync(path.join(out, 'Talking-Points-2026-09-14.md'), talking, 'utf8');
  console.log(`Created ${sections.length} slides with speaker notes and the matching talking-points guide.`);
}
main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
