/**
 * Local-only generation of the customer-facing AI Solutions Hub two-pager.
 * Content is restricted to the same public-safe material as the stakeholder
 * website: no tenant, subscription, resource or private evidence detail.
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, LevelFormat, ExternalHyperlink,
  TabStopType, TabStopPosition, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber,
} = require('docx');

const HUB_URL = 'https://ai-solutions-hub-ca.azurewebsites.net/';

const BLUE = '0078D4';
const DARKBLUE = '243A5E';
const INK = '1B1B1B';
const MUTED = '5A5A5A';
const TINT = 'EEF4FB';
const RULE = 'D6DEE8';

const ASSETS = path.join(__dirname, '..', 'site', 'src', 'assets');
const logoGray = fs.readFileSync(path.join(ASSETS, 'microsoft-gray.png'));
const logoWhite = fs.readFileSync(path.join(ASSETS, 'microsoft-white.png'));

const MARGIN = 864; // 0.6 inch
const CONTENT = 12240 - MARGIN * 2; // 10512

const thin = { style: BorderStyle.SINGLE, size: 1, color: RULE };
const cellBorders = { top: thin, bottom: thin, left: thin, right: thin };
const noBorder = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const blankBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const pad = { top: 90, bottom: 90, left: 130, right: 130 };
const tightPad = { top: 46, bottom: 46, left: 130, right: 130 };

const run = (text, opts = {}) => new TextRun({ text, font: 'Segoe UI', color: INK, size: 18, ...opts });

const body = (text, opts = {}) => new Paragraph({
  spacing: { after: 120, line: 264 },
  children: [run(text, opts)],
});

function sectionHeading(text) {
  return new Paragraph({
    spacing: { before: 200, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE, space: 4 } },
    children: [run(text.toUpperCase(), { bold: true, size: 20, color: DARKBLUE, characterSpacing: 20 })],
  });
}

function bullet(text, lead) {
  return new Paragraph({
    numbering: { reference: 'dots', level: 0 },
    spacing: { after: 70, line: 252 },
    children: lead
      ? [run(lead, { bold: true, color: DARKBLUE }), run(' ' + text)]
      : [run(text)],
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

/* ---------------------------------------------------------------- banner */

const banner = new Table({
  width: { size: CONTENT, type: WidthType.DXA },
  columnWidths: [CONTENT],
  rows: [new TableRow({
    children: [cell([
      new Paragraph({
        spacing: { after: 60 },
        children: [new ImageRun({
          type: 'png',
          data: logoWhite,
          transformation: { width: 104, height: 47 },
          altText: { title: 'Microsoft', description: 'Microsoft logo', name: 'Microsoft logo' },
        })],
      }),
      new Paragraph({
        spacing: { after: 40 },
        children: [run('PTU accelerator', { bold: true, size: 40, color: 'FFFFFF' })],
      }),
      new Paragraph({
        spacing: { after: 0 },
        children: [run('20 Microsoft and Azure AI solutions. Choose the ones that fit your work.', { size: 21, color: 'D9E8F7' })],
      }),
    ], { width: CONTENT, fill: DARKBLUE, borders: blankBorders })],
  })],
});

/* ------------------------------------------------------- three-up tiles */

function tile(title, sub, lines, width) {
  const children = [
    new Paragraph({ spacing: { after: 50 }, children: [run(title, { bold: true, size: 19, color: BLUE })] }),
    new Paragraph({ spacing: { after: 90 }, children: [run(sub, { size: 16, color: MUTED, italics: true })] }),
  ];
  lines.forEach((l) => children.push(new Paragraph({
    spacing: { after: 40, line: 240 },
    children: [run('— ' + l, { size: 16 })],
  })));
  return cell(children, { width, fill: TINT });
}

const tileWidths = [3504, 3504, 3504];
const TOP_PICKS = [
  ['Enterprise Knowledge', 'Chat With Your Data', 'Staff ask questions of an approved document set and get answers with sources.'],
  ['Content Processing', 'Document intake', 'Take in document packs and flag missing or incomplete material before review.'],
  ['Document Knowledge Mining', 'DKM', 'Ask questions across many documents and compare what they actually say.'],
  ['RFP & contract review', 'Evidence review', 'Check proposals and contracts against the evidence they are required to show.'],
  ['Modernize', 'Code modernization', 'Help engineering teams review a bounded code and SQL-dialect conversion.'],
  ['SpecSuite', 'Code to spec, spec to code', 'Turn existing code into specifications and system knowledge, then guide improvement.'],
];
const topPickTile = ([name, alias, value], i) => cell([
  new Paragraph({ spacing: { after: 30 }, children: [run(String(i + 1).padStart(2, '0') + '  ', { bold: true, size: 16, color: MUTED }), run(name, { bold: true, size: 19, color: BLUE })] }),
  new Paragraph({ spacing: { after: 60 }, children: [run(alias, { size: 15, color: MUTED, italics: true })] }),
  new Paragraph({ spacing: { after: 0, line: 240 }, children: [run(value, { size: 16 })] }),
], { width: tileWidths[i % 3], fill: TINT });
const topPicksTable = new Table({
  width: { size: CONTENT, type: WidthType.DXA },
  columnWidths: tileWidths,
  rows: [0, 3].map((offset) => new TableRow({
    children: TOP_PICKS.slice(offset, offset + 3).map((item, j) => topPickTile(item, offset + j)),
  })),
});

/* --------------------------------------------------------- the catalogue */

// Customer-priority order, matching customerOrder in site/src/content.mjs.
const CATALOG = [
  ['Enterprise Knowledge', 'Chat With Your Data', 'Help staff find and explain information in an approved collection of documents.'],
  ['Content Processing', 'Document intake', 'Intake document packs and flag missing material before review.'],
  ['Document Knowledge Mining', 'DKM', 'Ask questions across many documents and compare what they say.'],
  ['RFP & contract review', 'Procurement review', 'Compare proposals and contracts against the evidence they are required to show.'],
  ['Modernize', 'Engineering assistance', 'Help engineering teams review a bounded code and SQL-dialect conversion.'],
  ['SpecSuite', 'Code to spec, spec to code', 'Turn existing code into specifications and connected system knowledge, then guide improvement.'],
  ['Employee Self-Service', 'ESS', 'Help staff navigate routine internal guidance and service requests.'],
  ['Real-time voice agents', 'Azure Real-Time Agent', 'Answer routine spoken enquiries by phone or browser, and hand off to a person.'],
  ['Customer chatbot', 'Service questions', 'Answer routine service questions from approved guidance.'],
  ['Voice Live', 'Voice interaction', 'Explore spoken access to a bounded assistant workflow.'],
  ['Multi-agent orchestration', 'MACAE', 'Coordinate several assistant steps for a larger piece of staff work.'],
  ['Conversation Mining', 'Conversation insight', 'Find themes and recurring issues across approved conversation records.'],
  ['Content Generation', 'Drafting experiments', 'A starting point for marketing and communications generation experiments.'],
  ['Agentic Unified Data Foundation', 'Microsoft Fabric data agents', 'Connect an AI application to governed enterprise data through a Fabric data agent.'],
  ['RealTime Operations', 'Operational signals', 'Explore assistance around operational signals and emerging issues.'],
  ['Video workflow', 'Video exploration', 'Explore a narrowly scoped video understanding task under review.'],
  ['Planetary Explorer', 'Geospatial exploration', 'Explore specialist geospatial questions where there is a defined need.'],
  ['Bring Your Own Key pilot', 'Developer tooling', 'Connect developer tools to a model your organization manages.'],
  ['MCP security workshop', 'Guided security lab', 'Teach engineers how to secure the tool connections that AI agents depend on.'],
  ['Private platform baseline', 'Shared foundation', 'A common technical starting point for future integrated workflows.'],
];

const catWidths = [3500, 7012];
const catalogTable = new Table({
  width: { size: CONTENT, type: WidthType.DXA },
  columnWidths: catWidths,
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell([new Paragraph({ children: [run('Solution', { bold: true, size: 17, color: 'FFFFFF' })] })], { width: catWidths[0], fill: BLUE, tight: true }),
        cell([new Paragraph({ children: [run('What it does for the business', { bold: true, size: 17, color: 'FFFFFF' })] })], { width: catWidths[1], fill: BLUE, tight: true }),
      ],
    }),
    ...CATALOG.map(([name, alias, value], i) => new TableRow({
      children: [
        cell([new Paragraph({
          spacing: { after: 0, line: 230 },
          children: [run(name, { bold: true, size: 16, color: DARKBLUE }), run('  ' + alias, { size: 14, color: MUTED }), ...(i < 6 ? [run('\u2605 TOP PICK', { bold: true, size: 12, color: BLUE, break: 1 })] : [])],
        })], { width: catWidths[0], fill: i % 2 ? 'F7FAFD' : undefined, tight: true }),
        cell([new Paragraph({
          spacing: { after: 0, line: 230 },
          children: [run(value, { size: 16 })],
        })], { width: catWidths[1], fill: i % 2 ? 'F7FAFD' : undefined, tight: true }),
      ],
    })),
  ],
});

/* --------------------------------------------------- starter paths row */

function starter(title, sub, lines, width) {
  const children = [
    new Paragraph({ spacing: { after: 50 }, children: [run(title, { bold: true, size: 19, color: DARKBLUE })] }),
    new Paragraph({ spacing: { after: 70 }, children: [run(sub, { size: 16, color: BLUE })] }),
  ];
  lines.forEach((l) => children.push(new Paragraph({
    spacing: { after: 40, line: 240 },
    children: [run(l, { size: 16 })],
  })));
  return cell(children, { width, borders: { top: { style: BorderStyle.SINGLE, size: 12, color: BLUE }, bottom: thin, left: thin, right: thin } });
}

const startersTable = new Table({
  width: { size: CONTENT, type: WidthType.DXA },
  columnWidths: tileWidths,
  rows: [new TableRow({
    children: [
      starter('Trusted answers', 'Enterprise Knowledge (CWYD)', [
        'The usual first pilot. Point it at an approved document set and let staff ask questions of it, with sources shown and a human reviewer in the loop.',
      ], tileWidths[0]),
      starter('Document intake', 'Content Processing', [
        'The document-workflow priority. Take in submission packs, flag what is missing or incomplete, and give reviewers a consistent starting position.',
      ], tileWidths[1]),
      starter('Code modernization', 'Modernize and SpecSuite', [
        'Worth it where there is an active backlog and an accountable owner for the code it touches, not as a one-off demonstration.',
      ], tileWidths[2]),
    ],
  })],
});

/* -------------------------------------------------------------- call out */

const callout = new Table({
  width: { size: CONTENT, type: WidthType.DXA },
  columnWidths: [CONTENT],
  rows: [new TableRow({
    children: [cell([
      new Paragraph({
        spacing: { after: 50 },
        children: [
          new ImageRun({
            type: 'png',
            data: logoGray,
            transformation: { width: 76, height: 34 },
            altText: { title: 'Microsoft', description: 'Microsoft logo', name: 'Microsoft logo' },
          }),
          run('    Explore the catalog', { bold: true, size: 22, color: DARKBLUE }),
        ],
      }),
      new Paragraph({
        spacing: { after: 50 },
        children: [
          run('Browse all 20 solutions, compare outcomes and print a shortlist in the AI Solutions Hub: '),
          new ExternalHyperlink({
            children: [run(HUB_URL, { color: BLUE, bold: true, underline: {} })],
            link: HUB_URL,
          }),
        ],
      }),
      new Paragraph({
        spacing: { after: 0 },
        children: [run('A single, self-contained page. No sign-in, no analytics, no data leaves your browser.', { size: 16, color: MUTED, italics: true })],
      }),
    ], { width: CONTENT, fill: TINT, borders: { top: { style: BorderStyle.SINGLE, size: 12, color: BLUE }, bottom: thin, left: thin, right: thin } })],
  })],
});

/* ------------------------------------------------------------- document */

const doc = new Document({
  creator: 'Microsoft',
  title: 'PTU accelerator — customer overview',
  description: 'Customer-facing two-page overview of the AI Solutions Hub catalog.',
  styles: {
    default: { document: { run: { font: 'Segoe UI', size: 18, color: INK } } },
  },
  numbering: {
    config: [{
      reference: 'dots',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 300, hanging: 200 } } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 720, right: MARGIN, bottom: 620, left: MARGIN, header: 400, footer: 340 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          spacing: { after: 0 },
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          children: [
            run('PTU accelerator  \u00b7  AI Solutions Hub', { size: 15, color: MUTED }),
            run('\tMicrosoft', { size: 15, color: MUTED }),
          ],
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
            run('Microsoft  ·  PTU accelerator  ·  a curated catalog of solutions, not an official Microsoft commercial SKU', { size: 13, color: MUTED }),
            run('\tPage ', { size: 13, color: MUTED }),
            new TextRun({ children: [PageNumber.CURRENT], font: 'Segoe UI', size: 13, color: MUTED }),
            run(' of ', { size: 13, color: MUTED }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: 'Segoe UI', size: 13, color: MUTED }),
          ],
        })],
      }),
    },
    children: [
      banner,
      new Paragraph({ spacing: { after: 100 }, children: [] }),

      body('Most organizations buying Azure AI capacity face the same question a quarter later: what is it actually being used for? The PTU accelerator answers that with one catalog of 20 Microsoft and Azure AI solutions. There are no bundles to buy into: teams pick the solutions that fit their work, understand the prerequisites before committing budget, and measure the outcome alongside capacity utilization.'),

      sectionHeading('Why customers engage'),
      bullet('Twenty solutions in one catalog, filtered by business problem, with plain-language guides a business owner can read without a solution architect in the room.', 'Choose freely, start from the problem.'),
      bullet('Every entry lists what it needs, what it costs to run beyond the model, and how mature it is. Surprises happen before the pilot, not during it.', 'Know the prerequisites up front.'),
      bullet('Provisioned throughput, Standard and Batch are weighed against measured demand for a compatible model, API version and approved geography.', 'Put existing capacity to useful work.'),
      bullet('Repeat use, accepted output, time saved, quality and total service cost against a baseline — so the next renewal is an evidence-based decision.', 'Measure what matters.'),

      sectionHeading('Top picks to start with'),
      topPicksTable,

      sectionHeading('How we work with you'),
      new Paragraph({
        spacing: { after: 100, line: 264 },
        children: [
          run('Choose  →  Deploy  →  Adopt  →  Expand.  ', { bold: true, color: DARKBLUE }),
          run('We help you shortlist candidates against your own problems, arrange approved code access, and either support your team\u2019s deployment or scope end-to-end help through configuration, evaluation, handover and onboarding of further teams. Delivery, funding and operational support are agreed explicitly before work starts. Each pilot runs to an agreed acceptance gate that ends in a clear expand, repair or stop decision.'),
        ],
      }),

      sectionHeading('Three starter pilots'),
      startersTable,

      new Paragraph({ pageBreakBefore: true, spacing: { after: 0 }, children: [] }),
      sectionHeading('All 20 solutions, most requested first'),
      body('Top picks are what customers ask about first, not a readiness claim. A shortlist of two or three is typical. Readiness varies by entry \u2014 some workflows have passed bounded tests, others are inspected, prerequisite-gated or proposed \u2014 and each solution guide states its own position before any deployment decision.', { size: 16, color: MUTED }),
      catalogTable,

      sectionHeading('Where capacity fits'),
      body('Provisioned throughput can make throughput and latency predictable at suitable utilization. It does not make a model more accurate, guarantee end-to-end application latency, repair retrieval quality or confer an accreditation. Hosting, search, document intelligence, speech and storage are billed separately from model capacity, and routing must be confirmed for the specific model, API version and geography.'),

      sectionHeading('A realistic first 30 days'),
      new Paragraph({
        spacing: { after: 0, line: 264 },
        children: [
          run('Weeks 1\u20132. ', { bold: true, color: DARKBLUE }),
          run('Pick one problem and one starting point; confirm the data, owners and approvals it needs.  '),
          run('Weeks 3\u20134. ', { bold: true, color: DARKBLUE }),
          run('Stand up a bounded pilot with real material and a named human reviewer.  '),
          run('Gate. ', { bold: true, color: DARKBLUE }),
          run('Review outcome quality, repeat use, capacity utilization and total service cost against the baseline, then decide to expand, repair or stop.'),
        ],
      }),

      callout,
    ],
  }],
});

const out = path.join(__dirname, 'AI-Solutions-Hub-Two-Pager.docx');
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(out, buffer);
  console.log('Wrote ' + out);
});
