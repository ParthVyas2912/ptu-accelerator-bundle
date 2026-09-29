/**
 * Local-only generation of the customer-facing PTU accelerator one-pager and
 * two-pager (Word). All copy comes from customer-content.cjs, which is checked
 * against the website catalog before anything is written.
 */
const fs = require('node:fs');
const path = require('node:path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, LevelFormat, ExternalHyperlink,
  TabStopType, TabStopPosition, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber,
} = require('docx');
const C = require('./customer-content.cjs');

const { blue: BLUE, darkBlue: DARKBLUE, ink: INK, muted: MUTED, tint: TINT, rule: RULE } = C.BRAND;
const logoGray = fs.readFileSync(C.LOGO.gray);
const logoWhite = fs.readFileSync(C.LOGO.white);

const MARGIN = 864; // 0.6 inch
const CONTENT = 12240 - MARGIN * 2; // 10512
const THIRDS = [3504, 3504, 3504];
const HALVES = [5256, 5256];

const thin = { style: BorderStyle.SINGLE, size: 1, color: RULE };
const cellBorders = { top: thin, bottom: thin, left: thin, right: thin };
const noBorder = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const blankBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const accentTop = { top: { style: BorderStyle.SINGLE, size: 12, color: BLUE }, bottom: thin, left: thin, right: thin };
const pad = { top: 90, bottom: 90, left: 130, right: 130 };
const tightPad = { top: 46, bottom: 46, left: 130, right: 130 };

const run = (text, opts = {}) => new TextRun({ text, font: 'Segoe UI', color: INK, size: 18, ...opts });
const para = (children, spacing = { after: 0, line: 240 }, extra = {}) => new Paragraph({ spacing, children, ...extra });
const body = (text, opts = {}) => para([run(text, opts)], { after: 120, line: 264 });
const spacer = (after = 100) => para([], { after });
const microsoftLogo = (data, width, height) => new ImageRun({
  type: 'png', data, transformation: { width, height },
  altText: { title: 'Microsoft', description: 'Microsoft logo', name: 'Microsoft logo' },
});

function sectionHeading(text, before = 200) {
  return new Paragraph({
    spacing: { before, after: 110 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE, space: 4 } },
    children: [run(text.toUpperCase(), { bold: true, size: 20, color: DARKBLUE, characterSpacing: 20 })],
  });
}

function bullet(text, lead, size = 18) {
  return new Paragraph({
    numbering: { reference: 'dots', level: 0 },
    spacing: { after: 70, line: 252 },
    children: [run(lead, { bold: true, color: DARKBLUE, size }), run(' ' + text, { size })],
  });
}

function cell(children, opts = {}) {
  return new TableCell({
    borders: opts.borders || cellBorders,
    width: { size: opts.width, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    margins: opts.tight ? tightPad : pad,
    verticalAlign: VerticalAlign.TOP,
    children,
  });
}

const table = (columnWidths, rows) => new Table({
  width: { size: CONTENT, type: WidthType.DXA }, columnWidths, rows: rows.map((children) => new TableRow({ children })),
});

/* ------------------------------------------------------------- shared parts */

function banner(title, subtitle) {
  return table([CONTENT], [[cell([
    para([microsoftLogo(logoWhite, 104, 47)], { after: 60 }),
    para([run(title, { bold: true, size: 40, color: 'FFFFFF' })], { after: 40 }),
    para([run(subtitle, { size: 21, color: 'D9E8F7' })]),
  ], { width: CONTENT, fill: DARKBLUE, borders: blankBorders })]]);
}

function topPickTile(item, i, compact) {
  return cell([
    para([run(String(i + 1).padStart(2, '0') + '  ', { bold: true, size: 16, color: MUTED }), run(item.name, { bold: true, size: 19, color: BLUE })], { after: 30 }),
    para([run(item.alias, { size: 15, color: MUTED, italics: true })], { after: compact ? 40 : 60 }),
    para([run(item.tile, { size: 16 })]),
  ], { width: THIRDS[i % 3], fill: TINT });
}

const topPicksTable = (compact = false) => table(THIRDS, [0, 3].map((offset) =>
  C.TOP_PICKS.slice(offset, offset + 3).map((item, j) => topPickTile(item, offset + j, compact))));

const journeyParagraph = (compact = false) => para([
  run(C.JOURNEY.map(([step]) => step).join('  \u2192  ') + '.  ', { bold: true, color: DARKBLUE }),
  run(compact ? 'We help you shortlist solutions against your problems, then either support your team\u2019s deployment or scope end-to-end help through evaluation, handover and onboarding of further teams. Delivery and support are agreed before work starts.' : 'We help you shortlist solutions against your own problems, arrange approved code access, and either support your team\u2019s deployment or scope end-to-end help through configuration, evaluation, handover and onboarding of further teams. Delivery, funding and operational support are agreed explicitly before work starts.'),
], { after: 100, line: 264 });

function callout(lead, compact = false) {
  if (compact) {
    return table([CONTENT], [[cell([
      para([microsoftLogo(logoGray, 76, 34), run('  Explore all 20 solutions:  ', { bold: true, size: 18, color: DARKBLUE }),
        new ExternalHyperlink({ children: [run(C.HUB_URL, { color: BLUE, bold: true, underline: {} })], link: C.HUB_URL })]),
    ], { width: CONTENT, fill: TINT, borders: accentTop })]]);
  }
  return table([CONTENT], [[cell([
    para([microsoftLogo(logoGray, 76, 34), run('    Explore the catalog', { bold: true, size: 22, color: DARKBLUE })], { after: 50 }),
    para([
      run(lead),
      new ExternalHyperlink({ children: [run(C.HUB_URL, { color: BLUE, bold: true, underline: {} })], link: C.HUB_URL }),
    ], { after: 50 }),
    para([run('A single, self-contained page. No sign-in, no analytics, no data leaves your browser.', { size: 16, color: MUTED, italics: true })]),
  ], { width: CONTENT, fill: TINT, borders: accentTop })]]);
}

function document(title, description, children, margin) {
  return new Document({
    creator: 'Microsoft',
    title,
    description,
    styles: { default: { document: { run: { font: 'Segoe UI', size: 18, color: INK } } } },
    numbering: {
      config: [{
        reference: 'dots',
        levels: [{ level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 300, hanging: 200 } } } }],
      }],
    },
    sections: [{
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { right: MARGIN, left: MARGIN, header: 400, footer: 340, ...margin } },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            spacing: { after: 0 },
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
            children: [run('PTU accelerator  \u00b7  AI Solutions Hub', { size: 15, color: MUTED }), run('\tMicrosoft', { size: 15, color: MUTED })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            spacing: { before: 60, after: 0 },
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 6 } },
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
            children: [
              run('Microsoft  \u00b7  PTU accelerator  \u00b7  a curated catalog of solutions, not an official Microsoft commercial SKU', { size: 13, color: MUTED }),
              run('\tPage ', { size: 13, color: MUTED }),
              new TextRun({ children: [PageNumber.CURRENT], font: 'Segoe UI', size: 13, color: MUTED }),
              run(' of ', { size: 13, color: MUTED }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], font: 'Segoe UI', size: 13, color: MUTED }),
            ],
          })],
        }),
      },
      children,
    }],
  });
}

const intro = 'Most organizations buying Azure AI capacity face the same question a quarter later: what is it actually being used for? The PTU accelerator answers that with one catalog of 20 Microsoft and Azure AI solutions. There are no bundles to buy into: teams pick the solutions that fit their work, understand the prerequisites before committing budget, and measure the outcome alongside capacity utilization.';

/* ---------------------------------------------------------------- one-pager */

function onePager() {
  const valueGrid = table(HALVES, [0, 2].map((offset) => C.VALUE.slice(offset, offset + 2).map(([lead, text], j) => cell([
    para([run(lead, { bold: true, size: 18, color: DARKBLUE })], { after: 40 }),
    para([run(text, { size: 16 })], { after: 0, line: 240 }),
  ], { width: HALVES[j], borders: accentTop }))));

  const problemRows = Object.entries(C.PROBLEMS).map(([key, label], i) => [
    cell([para([run(label, { bold: true, size: 16, color: DARKBLUE })])], { width: 3500, tight: true, fill: i % 2 ? 'F7FAFD' : undefined }),
    cell([para([run(C.CATALOG.filter((item) => item.problems.includes(key)).map((item) => item.name).join('  \u00b7  '), { size: 15 })])], { width: 7012, tight: true, fill: i % 2 ? 'F7FAFD' : undefined }),
  ]);

  return document('PTU accelerator \u2014 one-page overview', 'Customer-facing one-page overview of the PTU accelerator solution catalog.', [
    banner('PTU accelerator', C.TAGLINE),
    spacer(90),
    body('Most organizations buying Azure AI capacity face the same question a quarter later: what is it being used for? The PTU accelerator is one catalog of 20 Microsoft and Azure AI solutions. No bundles: teams pick what fits their work, see the prerequisites before committing budget, and measure the outcome.'),
    valueGrid,
    sectionHeading('Top picks to start with', 180),
    topPicksTable(true),
    sectionHeading('All 20 solutions, by business problem \u2014 choose any mix', 180),
    table([3500, 7012], problemRows),
    sectionHeading('How we work with you', 180),
    journeyParagraph(true),
    callout('', true),
  ], { top: 640, bottom: 560 });
}

/* ---------------------------------------------------------------- two-pager */

function twoPager() {
  const starters = table(THIRDS, [C.STARTERS.map((s, i) => cell([
    para([run(s.title, { bold: true, size: 19, color: DARKBLUE })], { after: 50 }),
    para([run(s.solutions, { size: 15, color: BLUE })], { after: 70 }),
    para([run(s.summary, { size: 16 })], { after: 40, line: 240 }),
  ], { width: THIRDS[i], borders: accentTop }))]);

  const catWidths = [3500, 7012];
  const header = [
    cell([para([run('Solution', { bold: true, size: 17, color: 'FFFFFF' })])], { width: catWidths[0], fill: BLUE, tight: true }),
    cell([para([run('What it does for the business', { bold: true, size: 17, color: 'FFFFFF' })])], { width: catWidths[1], fill: BLUE, tight: true }),
  ];
  const catalog = new Table({
    width: { size: CONTENT, type: WidthType.DXA },
    columnWidths: catWidths,
    rows: [
      new TableRow({ tableHeader: true, children: header }),
      ...C.CATALOG.map((item, i) => new TableRow({
        children: [
          cell([para([
            run(item.name, { bold: true, size: 16, color: DARKBLUE }), run('  ' + item.alias, { size: 14, color: MUTED }),
            ...(i < 6 ? [run('\u2605 TOP PICK', { bold: true, size: 12, color: BLUE, break: 1 })] : []),
          ], { after: 0, line: 230 })], { width: catWidths[0], fill: i % 2 ? 'F7FAFD' : undefined, tight: true }),
          cell([para([run(item.value, { size: 16 })], { after: 0, line: 230 })], { width: catWidths[1], fill: i % 2 ? 'F7FAFD' : undefined, tight: true }),
        ],
      })),
    ],
  });

  return document('PTU accelerator \u2014 customer overview', 'Customer-facing two-page overview of the PTU accelerator solution catalog.', [
    banner('PTU accelerator', C.TAGLINE),
    spacer(),
    body(intro),
    sectionHeading('Why customers engage'),
    ...C.VALUE.map(([lead, text]) => bullet(text, lead)),
    sectionHeading('Top picks to start with'),
    topPicksTable(),
    sectionHeading('How we work with you'),
    journeyParagraph(),
    sectionHeading('Three starter pilots'),
    starters,

    new Paragraph({ pageBreakBefore: true, spacing: { after: 0 }, children: [] }),
    sectionHeading('All 20 solutions, most requested first'),
    body('Top picks are what customers ask about first, not a readiness claim. A shortlist of two or three is typical. Readiness varies by entry \u2014 some workflows have passed bounded tests, others are inspected, prerequisite-gated or proposed \u2014 and each solution guide states its own position before any deployment decision.', { size: 16, color: MUTED }),
    catalog,
    sectionHeading('Where capacity fits'),
    body(`Provisioned throughput ${C.CAPACITY.does[0].charAt(0).toLowerCase()}${C.CAPACITY.does[0].slice(1, -1)}. It does not make a model more accurate, guarantee end-to-end application latency, repair retrieval quality or confer an accreditation. Hosting, search, document intelligence, speech and storage are billed separately from model capacity. ${C.CAPACITY.check}`),
    sectionHeading('A realistic first 30 days'),
    para(C.THIRTY_DAYS.flatMap(([when, what]) => [run(when + '. ', { bold: true, color: DARKBLUE }), run(what + '  ')]), { after: 120, line: 264 }),
    callout('Browse all 20 solutions, compare outcomes and print a shortlist in the AI Solutions Hub: '),
  ], { top: 720, bottom: 620 });
}

(async () => {
  await C.checkAgainstSite();
  const outDir = path.join(__dirname, 'customer');
  fs.mkdirSync(outDir, { recursive: true });
  for (const [name, build] of [['PTU-Accelerator-One-Pager.docx', onePager], ['PTU-Accelerator-Two-Pager.docx', twoPager]]) {
    const file = path.join(outDir, name);
    fs.writeFileSync(file, await Packer.toBuffer(build()));
    console.log('Wrote ' + file);
  }
})().catch((error) => { console.error(error); process.exit(1); });
