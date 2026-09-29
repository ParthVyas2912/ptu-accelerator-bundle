/**
 * Local-only generation of the customer-facing PTU accelerator deck
 * (16:9, Microsoft-branded, speaker notes included). All copy comes from
 * customer-content.cjs, which is checked against the website catalog first.
 */
const fs = require('node:fs');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const C = require('./customer-content.cjs');

const B = C.BRAND;
const W = 13.333, H = 7.5, X = 0.7, CW = W - 2 * X;
const FONT = 'Segoe UI', HEAD = 'Segoe UI Semibold';

const pngSize = (file) => { const b = fs.readFileSync(file); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; };
const logo = (variant, height) => {
  const file = C.LOGO[variant]; const { w, h } = pngSize(file);
  return { path: file, h: height, w: height * (w / h) };
};

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Microsoft';
pptx.company = 'Microsoft';
pptx.title = 'PTU accelerator \u2014 customer overview';
pptx.subject = 'One catalog of 20 Microsoft and Azure AI solutions to put provisioned capacity to useful work';
pptx.lang = 'en-US';
pptx.theme = { headFontFace: HEAD, bodyFontFace: FONT, lang: 'en-US' };

const text = (s, value, x, y, w, h, size, o = {}) => s.addText(value, {
  x, y, w, h, fontFace: FONT, fontSize: size, color: B.ink, margin: 0, valign: 'top', ...o,
});
const rect = (s, x, y, w, h, fill, o = {}) => s.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { color: o.line || fill, width: o.lineWidth || 0.75 } });
const squares = (s, x, y, size = 0.14, gap = 0.03) => B.squares.forEach((color, i) =>
  rect(s, x + (i % 2) * (size + gap), y + Math.floor(i / 2) * (size + gap), size, size, color));

let slideNo = 0;
function slide(kicker, title, subtitle, notes) {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: B.paper };
  rect(s, 0, 0, W, 0.09, B.blue);
  text(s, kicker.toUpperCase(), X, 0.45, CW, 0.3, 12, { bold: true, color: B.blue, charSpacing: 2 });
  text(s, title, X, 0.8, CW, 0.9, 32, { fontFace: HEAD, bold: true, color: B.darkBlue, valign: 'middle' });
  if (subtitle) text(s, subtitle, X, 1.7, CW, 0.5, 16, { color: B.muted, valign: 'middle' });
  s.addImage({ ...logo('gray', 0.26), x: X, y: 6.98 });
  text(s, 'PTU accelerator  \u00b7  AI Solutions Hub', X + 0.8, 7.0, 6, 0.25, 10, { color: B.muted, valign: 'middle' });
  text(s, String(slideNo), W - X - 0.6, 7.0, 0.6, 0.25, 10, { color: B.muted, align: 'right', valign: 'middle' });
  s.addNotes(notes);
  return s;
}

function card(s, x, y, w, h, o) {
  rect(s, x, y, w, h, o.fill || B.canvas, { line: o.line || B.rule });
  if (o.accent !== false) rect(s, x, y, w, 0.07, o.accentColor || B.blue);
  let cy = y + 0.25;
  if (o.number) { text(s, o.number, x + 0.25, cy, 1, 0.3, 12, { bold: true, color: B.muted }); cy += 0.35; }
  text(s, o.title, x + 0.25, cy, w - 0.5, o.titleH || 0.45, o.titleSize || 18, { bold: true, color: o.titleColor || B.darkBlue, fontFace: HEAD });
  cy += o.titleH || 0.45;
  if (o.sub) { text(s, o.sub, x + 0.25, cy, w - 0.5, 0.3, 12, { italic: true, color: B.muted }); cy += 0.38; }
  if (o.body) text(s, o.body, x + 0.25, cy + 0.05, w - 0.5, y + h - cy - 0.2, o.bodySize || 14, { color: B.ink });
}

const bullets = (items, size = 15, color = B.ink) => items.map((t) => ({ text: t, options: { bullet: { indent: 16 }, fontSize: size, color, paraSpaceAfter: 6 } }));

/* 1 - Title */
{
  const s = pptx.addSlide(); slideNo += 1;
  s.background = { color: B.darkBlue };
  s.addImage({ ...logo('white', 0.5), x: X, y: 0.6 });
  text(s, 'PTU accelerator', X, 2.3, 10, 1.1, 54, { fontFace: HEAD, bold: true, color: 'FFFFFF', valign: 'middle' });
  text(s, C.TAGLINE, X, 3.45, 11, 0.6, 22, { color: 'D9E8F7', valign: 'middle' });
  rect(s, X, 4.35, 1.2, 0.06, B.blue);
  text(s, 'Customer overview  \u00b7  AI Solutions Hub', X, 4.6, 10, 0.4, 16, { color: 'D9E8F7', valign: 'middle' });
  squares(s, W - X - 0.6, H - 1.05, 0.26, 0.05);
  text(s, C.DISCLAIMER, X, H - 0.8, 10, 0.4, 10, { color: 'B8C9DD', valign: 'middle' });
  s.addNotes('Open with the customer\u2019s situation, not the product. The PTU accelerator is one catalog of 20 Microsoft and Azure AI solutions. Teams choose the few that fit their work; there are no bundles to buy into. It is a curated catalog, not an official Microsoft commercial SKU.');
}

/* 2 - The question */
{
  const s = slide('The question every AI capacity owner gets', 'You own the capacity. What is it doing for your people?',
    'A quarter after buying Azure AI capacity, most organizations are asked the same question.',
    'Frame the problem in the customer\u2019s words. The usual blockers are not the model: they are choosing a workload, discovering prerequisites late, and having no measure of value when renewal comes around. Ask which of these sounds familiar.');
  const items = [
    ['Capacity waiting for work', 'Provisioned throughput is only useful when a real workload with steady demand runs on it.'],
    ['Pilots that stall', 'Data access, approvals and owners are discovered after a demo, not before a pilot.'],
    ['No measure of value', 'Without a baseline, adoption and time saved are anecdotes at renewal time.'],
  ];
  const w = (CW - 0.6) / 3;
  items.forEach(([title, body], i) => card(s, X + i * (w + 0.3), 2.55, w, 3.6, { number: `0${i + 1}`, title, body, bodySize: 16, titleSize: 20, titleH: 0.8 }));
}

/* 3 - What it is */
{
  const s = slide('What the PTU accelerator is', 'One catalog. 20 solutions. You choose.',
    'Microsoft and Azure AI solutions, organized by the business problem they solve. No bundles to buy into.',
    'Four promises. Teams start from their problem and choose freely from the catalog. Every entry states its prerequisites and maturity before anyone commits budget. Capacity decisions follow measured demand for a compatible model, API version and geography. And we agree up front how success will be measured.');
  const w = (CW - 0.3) / 2, h = 1.95;
  C.VALUE.forEach(([title, body], i) => card(s, X + (i % 2) * (w + 0.3), 2.5 + Math.floor(i / 2) * (h + 0.25), w, h, { title, body, bodySize: 15 }));
}

/* 4 - Problems */
{
  const s = slide('Start from the problem', 'Six business problems. Solutions for each.',
    'Every solution in the catalog maps to at least one problem your teams recognize.',
    'Ask the audience which two rows describe their week. Each row lists the catalog solutions that address it; several solutions help with more than one problem. This is how the website filters the catalog too.');
  const w = (CW - 0.6) / 3, h = 2.15;
  Object.entries(C.PROBLEMS).forEach(([key, label], i) => {
    const names = C.CATALOG.filter((item) => item.problems.includes(key)).map((item) => item.name);
    card(s, X + (i % 3) * (w + 0.3), 2.4 + Math.floor(i / 3) * (h + 0.15), w, h, { title: label, titleSize: 16, titleH: 0.7, body: names.map((n) => n.replace(/ /g, '\u00a0').replace(/-/g, '\u2011')).join('\u00a0\u00a0\u00b7  '), bodySize: 12 });
  });
}

/* 5 - Top picks */
{
  const s = slide('Top picks', 'Six solutions customers ask about first.',
    'A starting point for the conversation, not a readiness ranking. Choose any mix of all 20.',
    'These six are the most requested. Knowledge and document work are the broadest; code modernization is strong where there is an engineering owner. Top pick means demand, not readiness: each solution guide states its own maturity and prerequisites.');
  const w = (CW - 0.6) / 3, h = 2.1;
  C.TOP_PICKS.forEach((item, i) => card(s, X + (i % 3) * (w + 0.3), 2.4 + Math.floor(i / 3) * (h + 0.2), w, h, {
    title: item.name, titleColor: B.blue, titleSize: 16, sub: item.alias, body: item.tile, bodySize: 13, titleH: 0.4,
  }));
}

/* 6-8 - Starter pilots */
C.STARTERS.forEach((st, index) => {
  const s = slide(`Starter pilot ${index + 1} of 3`, st.title, st.solutions,
    `${st.summary} Walk through who it helps, what the customer must bring, and how the pilot will be judged. Prerequisites are the customer\u2019s to confirm; nothing here implies the pilot is already built for their environment.`);
  const lw = 5.6;
  text(s, st.summary, X, 2.55, lw, 1.6, 20, { color: B.ink });
  text(s, 'WHO IT HELPS', X, 4.35, lw, 0.3, 12, { bold: true, color: B.blue, charSpacing: 1.5 });
  text(s, st.who, X, 4.7, lw, 0.8, 16, { color: B.ink });
  const rx = X + lw + 0.5, rw = CW - lw - 0.5;
  rect(s, rx, 2.45, rw, 4.2, B.canvas, { line: B.rule });
  rect(s, rx, 2.45, 0.07, 4.2, B.blue);
  text(s, 'WHAT YOU BRING', rx + 0.35, 2.7, rw - 0.6, 0.3, 12, { bold: true, color: B.blue, charSpacing: 1.5 });
  text(s, bullets(st.needs, 16), rx + 0.35, 3.1, rw - 0.6, 1.8, 16);
  text(s, 'HOW WE MEASURE IT', rx + 0.35, 5.05, rw - 0.6, 0.3, 12, { bold: true, color: B.blue, charSpacing: 1.5 });
  text(s, st.measure, rx + 0.35, 5.45, rw - 0.6, 1.0, 16, { color: B.ink });
});

/* 9 - Full catalog */
{
  const s = slide('The full catalog', 'All 20 solutions, most requested first.',
    'Top picks highlighted. Readiness varies by solution; each guide states its own position.',
    'The whole catalog on one page, in the order customers ask about them. Several entries are workshops, design patterns or foundations rather than finished apps; the website says which. A shortlist of two or three is typical.');
  const cols = 4, rows = 5, gx = 0.2, gy = 0.16;
  const w = (CW - gx * (cols - 1)) / cols, h = (6.85 - 2.3 - gy * (rows - 1)) / rows;
  C.CATALOG.forEach((item, i) => {
    const x = X + (i % cols) * (w + gx), y = 2.3 + Math.floor(i / cols) * (h + gy);
    const top = i < 6;
    rect(s, x, y, w, h, top ? B.blue : B.canvas, { line: top ? B.blue : B.rule });
    text(s, `${String(i + 1).padStart(2, '0')}  ${item.name}`, x + 0.15, y + 0.07, w - 0.3, 0.44, 12, { bold: true, color: top ? 'FFFFFF' : B.darkBlue });
    text(s, item.alias, x + 0.15, y + h - 0.29, w - 0.3, 0.24, 10, { color: top ? 'D9E8F7' : B.muted });
  });
}

/* 10 - How we work */
{
  const s = slide('How we work with you', 'Choose. Deploy. Adopt. Expand.',
    'Delivery, funding and operational support are agreed explicitly before work starts.',
    'We help shortlist against the customer\u2019s own problems, arrange approved code access, and either support their team\u2019s deployment or scope end-to-end help. Nothing is delivered by default; each engagement is agreed explicitly.');
  const w = (CW - 0.45) / 4;
  C.JOURNEY.forEach(([step, body], i) => {
    const x = X + i * (w + 0.15);
    s.addShape(i === 0 ? pptx.ShapeType.homePlate : pptx.ShapeType.chevron, { x, y: 2.9, w, h: 1.0, fill: { color: i % 2 ? B.darkBlue : B.blue }, line: { color: 'FFFFFF', width: 0 } });
    text(s, step, x + (i ? 0.62 : 0.3), 2.9, w - 1.0, 1.0, 22, { bold: true, color: 'FFFFFF', valign: 'middle', fontFace: HEAD });
    text(s, body, x + 0.1, 4.25, w - 0.3, 1.8, 17, { color: B.ink });
  });
}

/* 11 - 30 days */
{
  const s = slide('A realistic first 30 days', 'One problem. One pilot. One clear decision.',
    'A bounded qualification sprint, not a delivery commitment.',
    'Weeks one and two are about readiness: the data, the owner and the approvals. Weeks three and four run a bounded pilot with real material and a named reviewer. The gate is a genuine decision: expand, repair, or stop.');
  const w = (CW - 0.6) / 3;
  C.THIRTY_DAYS.forEach(([when, what], i) => card(s, X + i * (w + 0.3), 2.55, w, 3.4, {
    title: when, titleSize: 24, titleH: 0.7, titleColor: i === 2 ? B.blue : B.darkBlue, body: what, bodySize: 16,
  }));
}

/* 12 - Capacity */
{
  const s = slide('Where capacity fits', 'Capacity follows the workload.',
    'Provisioned throughput is a capacity decision, made after the workload is understood.',
    'Be precise here. Provisioned throughput gives predictable throughput and latency at suitable utilization. It does not improve answer quality, and it does not cover the other Azure services a solution uses. Routing must be confirmed for the specific model, API version and geography.');
  const w = (CW - 0.3) / 2;
  rect(s, X, 2.5, w, 3.4, B.canvas, { line: B.rule }); rect(s, X, 2.5, w, 0.07, B.squares[1]);
  text(s, 'WHAT IT DOES', X + 0.3, 2.8, w - 0.6, 0.3, 12, { bold: true, color: B.darkBlue, charSpacing: 1.5 });
  text(s, bullets(C.CAPACITY.does, 17), X + 0.3, 3.2, w - 0.6, 2.5, 17);
  const rx = X + w + 0.3;
  rect(s, rx, 2.5, w, 3.4, B.canvas, { line: B.rule }); rect(s, rx, 2.5, w, 0.07, B.squares[0]);
  text(s, 'WHAT IT DOES NOT DO', rx + 0.3, 2.8, w - 0.6, 0.3, 12, { bold: true, color: B.darkBlue, charSpacing: 1.5 });
  text(s, bullets(C.CAPACITY.doesNot, 17), rx + 0.3, 3.2, w - 0.6, 2.5, 17);
  text(s, C.CAPACITY.check, X, 6.15, CW, 0.4, 15, { italic: true, color: B.muted });
}

/* 13 - Measures */
{
  const s = slide('Success you can measure', 'Agree the measures before the pilot starts.',
    'So the next capacity or renewal decision is based on evidence, not anecdotes.',
    'Agree these four measures and their baseline in week one. They are what the expand, repair or stop decision is based on.');
  const w = (CW - 0.9) / 4;
  C.MEASURES.forEach(([title, body], i) => card(s, X + i * (w + 0.3), 2.55, w, 3.2, {
    number: `0${i + 1}`, title, titleSize: 20, titleH: 0.6, body, bodySize: 15, accentColor: B.squares[i],
  }));
}

/* 14 - Next step */
{
  const s = pptx.addSlide(); slideNo += 1;
  s.background = { color: B.darkBlue };
  s.addImage({ ...logo('white', 0.4), x: X, y: 0.55 });
  text(s, 'THE NEXT CONVERSATION', X, 1.45, CW, 0.3, 12, { bold: true, color: '9CC9F0', charSpacing: 2 });
  text(s, 'Bring one use case. Leave with a next step.', X, 1.8, CW, 0.9, 34, { fontFace: HEAD, bold: true, color: 'FFFFFF', valign: 'middle' });
  const asks = [
    ['The problem', 'Who needs help, and what do they struggle with today?'],
    ['The owner', 'Who owns the workflow and can accept or reject the output?'],
    ['The material', 'Which approved data or code can a pilot use?'],
  ];
  const w = (CW - 0.6) / 3;
  asks.forEach(([title, body], i) => {
    const x = X + i * (w + 0.3);
    rect(s, x, 3.0, w, 2.0, '2E4A73', { line: '3C5C8A' });
    rect(s, x, 3.0, w, 0.07, B.squares[i + 1]);
    text(s, title, x + 0.25, 3.25, w - 0.5, 0.45, 20, { bold: true, color: 'FFFFFF', fontFace: HEAD });
    text(s, body, x + 0.25, 3.8, w - 0.5, 1.0, 15, { color: 'D9E8F7' });
  });
  text(s, 'Explore all 20 solutions in the AI Solutions Hub', X, 5.35, CW, 0.4, 16, { color: 'D9E8F7' });
  text(s, [{ text: C.HUB_URL, options: { hyperlink: { url: C.HUB_URL }, color: 'FFFFFF', bold: true } }], X, 5.75, CW, 0.5, 22);
  text(s, C.DISCLAIMER, X, H - 0.7, CW - 1, 0.4, 10, { color: 'B8C9DD', valign: 'middle' });
  squares(s, W - X - 0.6, H - 1.05, 0.26, 0.05);
  s.addNotes('Close with a concrete ask: one problem, one owner, one set of approved material. The website lets the customer browse all 20 solutions, check prerequisites and print a shortlist. No sign-in, no analytics, and no data leaves the browser.');
}

(async () => {
  await C.checkAgainstSite();
  const outDir = path.join(__dirname, 'customer');
  fs.mkdirSync(outDir, { recursive: true });
  const file = path.join(outDir, 'PTU-Accelerator-Customer-Deck.pptx');
  await pptx.writeFile({ fileName: file });
  console.log(`Wrote ${file} (${slideNo} slides)`);
})().catch((error) => { console.error(error); process.exit(1); });
