/**
 * Single source of customer-facing copy for the one-pager, two-pager and
 * customer deck. Public-safe only: the same material as the website, with no
 * tenant, subscription, resource, evidence or customer detail.
 * `checkAgainstSite()` fails the build if order, names or problems drift from
 * site/src/content.mjs and site/src/onboarding.mjs.
 */
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const HUB_URL = 'https://ai-solutions-hub-ca.azurewebsites.net/';

const BRAND = {
  blue: '0078D4', darkBlue: '243A5E', ink: '1B1B1B', muted: '5A5A5A',
  tint: 'EEF4FB', rule: 'D6DEE8', paper: 'FFFFFF', canvas: 'F5F7FA',
  // Microsoft logo colours, used only as a small accent motif.
  squares: ['F25022', '7FBA00', '00A4EF', 'FFB900'],
};

const ASSETS = path.join(__dirname, '..', 'site', 'src', 'assets');
const LOGO = {
  gray: path.join(ASSETS, 'microsoft-gray.png'),
  white: path.join(ASSETS, 'microsoft-white.png'),
};

const TAGLINE = '20 Microsoft and Azure AI solutions. Choose the ones that fit your work.';
const DISCLAIMER = 'A curated catalog of solutions, not an official Microsoft commercial SKU. Readiness varies by solution; each guide states its own.';

const PROBLEMS = {
  answers: 'Information is hard to find',
  documents: 'Document review takes too long',
  engineering: 'Systems are hard to understand or change',
  service: 'Staff and customers need better assistance',
  drafting: 'Writing and analysis are repetitive',
  data: 'Data is difficult to turn into insight',
};

// Customer-priority order; must match customerOrder in site/src/content.mjs.
// [id, name, alias, one-line business value, problems]
const CATALOG = [
  [1, 'Enterprise Knowledge', 'Chat With Your Data', 'Help staff find and explain information in an approved collection of documents.', ['answers']],
  [6, 'Content Processing', 'Document intake', 'Intake document packs and flag missing material before review.', ['documents']],
  [4, 'Document Knowledge Mining', 'DKM', 'Ask questions across many documents and compare what they say.', ['answers', 'documents']],
  [12, 'RFP & contract review', 'Procurement review', 'Compare proposals and contracts against the evidence they are required to show.', ['documents']],
  [9, 'Modernize', 'Code modernization', 'Help engineering teams review a bounded code and SQL-dialect conversion.', ['engineering']],
  [3, 'SpecSuite', 'Code to spec, spec to code', 'Turn existing code into specifications and connected system knowledge, then guide improvement.', ['engineering']],
  [15, 'Employee Self-Service', 'ESS', 'Help staff navigate routine internal guidance and service requests.', ['service', 'answers']],
  [21, 'Real-time voice agents', 'Azure Real-Time Agent', 'Answer routine spoken enquiries by phone or browser, and hand off to a person.', ['service']],
  [7, 'Customer chatbot', 'Service questions', 'Answer routine service questions from approved guidance.', ['service', 'answers']],
  [11, 'Voice Live', 'Voice interaction', 'Explore spoken access to a bounded assistant workflow.', ['service']],
  [2, 'Multi-agent orchestration', 'MACAE', 'Coordinate several assistant steps for a larger piece of staff work.', ['drafting']],
  [8, 'Conversation Mining', 'Conversation insight', 'Find themes and recurring issues across approved conversation records.', ['drafting', 'data']],
  [13, 'Content Generation', 'Drafting experiments', 'A starting point for marketing and communications generation experiments.', ['drafting']],
  [16, 'Agentic Unified Data Foundation', 'Microsoft Fabric data agents', 'Connect an AI application to governed enterprise data through a Fabric data agent.', ['data', 'answers']],
  [17, 'RealTime Operations', 'Operational signals', 'Explore assistance around operational signals and emerging issues.', ['data']],
  [19, 'Video workflow', 'Video exploration', 'Explore a narrowly scoped video understanding task under review.', ['data']],
  [10, 'Planetary Explorer', 'Geospatial exploration', 'Explore specialist geospatial questions where there is a defined need.', ['data']],
  [5, 'Bring Your Own Key pilot', 'Developer tooling', 'Connect developer tools to a model your organization manages.', ['engineering']],
  [22, 'MCP security workshop', 'Guided security lab', 'Teach engineers how to secure the tool connections that AI agents depend on.', ['engineering']],
  [14, 'Private platform baseline', 'Shared foundation', 'A common technical starting point for future integrated workflows.', ['engineering']],
].map(([id, name, alias, value, problems]) => ({ id, name, alias, value, problems }));

// Short tile copy for the six top picks (the first six in CATALOG).
const TOP_PICK_COPY = {
  1: 'Staff ask questions of an approved document set and get answers with sources.',
  6: 'Take in document packs and flag missing or incomplete material before review.',
  4: 'Ask questions across many documents and compare what they actually say.',
  12: 'Check proposals and contracts against the evidence they are required to show.',
  9: 'Help engineering teams review a bounded code and SQL-dialect conversion.',
  3: 'Turn existing code into specifications and system knowledge, then guide improvement.',
};
const TOP_PICKS = CATALOG.slice(0, 6).map((item) => ({ ...item, tile: TOP_PICK_COPY[item.id] }));

const VALUE = [
  ['Choose freely, start from the problem.', 'Twenty solutions in one catalog, filtered by business problem, with plain-language guides a business owner can read without an architect in the room.'],
  ['Know the prerequisites up front.', 'Every entry lists what it needs, what it costs to run beyond the model, and how mature it is. Surprises happen before the pilot, not during it.'],
  ['Put existing capacity to useful work.', 'Provisioned throughput, Standard and Batch are weighed against measured demand for a compatible model, API version and approved geography.'],
  ['Measure what matters.', 'Repeat use, accepted output, time saved, quality and total service cost against a baseline, so the next renewal is an evidence-based decision.'],
];

const STARTERS = [
  {
    title: 'Trusted answers', solutions: 'Enterprise Knowledge, extended with Document Knowledge Mining',
    summary: 'The usual first pilot. Point it at an approved document set and let staff ask questions of it, with sources shown and a human reviewer in the loop.',
    who: 'Knowledge workers, policy and advisory teams, service desks.',
    needs: ['An approved, maintained document collection', 'A business owner and a named reviewer', 'An approved Azure environment and model deployment'],
    measure: 'Answer acceptance, repeat use and time to a sourced answer.',
  },
  {
    title: 'Document intake', solutions: 'Content Processing, extended with RFP & contract review',
    summary: 'The document-workflow priority. Take in submission packs, flag what is missing or incomplete, and give reviewers a consistent starting position.',
    who: 'Intake, procurement, claims and compliance reviewers.',
    needs: ['Representative document packs and a completeness checklist', 'A reviewer who owns the final decision', 'An approved Azure environment and model deployment'],
    measure: 'Reviewer time per pack, missing-item detection and rework.',
  },
  {
    title: 'Code modernization', solutions: 'Modernize and SpecSuite',
    summary: 'Worth it where there is an active backlog and an accountable owner for the code it touches, not as a one-off demonstration.',
    who: 'Application owners and engineering teams with legacy systems.',
    needs: ['A bounded, representative code or SQL sample', 'An owner who can run tests on the result', 'Approved code access and an Azure environment'],
    measure: 'Reviewed changes accepted, test results and engineer time saved.',
  },
];

const JOURNEY = [
  ['Choose', 'Shortlist two or three solutions against your own problems and prerequisites.'],
  ['Deploy', 'Your team deploys with our guidance, or we scope end-to-end help.'],
  ['Adopt', 'Configure, evaluate with real material and hand over to a named owner.'],
  ['Expand', 'Onboard further teams once the first workflow proves its value.'],
];

const THIRTY_DAYS = [
  ['Weeks 1\u20132', 'Pick one problem and one solution; confirm the data, owners and approvals it needs.'],
  ['Weeks 3\u20134', 'Stand up a bounded pilot with real material and a named human reviewer.'],
  ['Gate', 'Review outcome quality, repeat use, capacity utilization and total service cost against the baseline, then decide to expand, repair or stop.'],
];

const CAPACITY = {
  does: [
    'Makes throughput and latency predictable at suitable utilization.',
    'Lets a workload with steady demand use capacity you already own.',
  ],
  doesNot: [
    'Make a model more accurate or repair retrieval quality.',
    'Guarantee end-to-end application latency or confer an accreditation.',
    'Cover hosting, search, document intelligence, speech or storage, which are billed separately.',
  ],
  check: 'Routing must be confirmed for the specific model, API version and geography.',
};

const MEASURES = [
  ['Adoption', 'Repeat use by the intended team, not one-off trials.'],
  ['Time saved', 'Against a measured baseline for the same task.'],
  ['Quality', 'Outputs a named reviewer accepts without rework.'],
  ['Useful capacity', 'Utilization and total service cost, including non-model services.'],
];

async function checkAgainstSite() {
  const src = path.join(__dirname, '..', 'site', 'src');
  const content = await import(pathToFileURL(path.join(src, 'content.mjs')).href);
  const onboarding = await import(pathToFileURL(path.join(src, 'onboarding.mjs')).href);
  const fail = (message) => { throw new Error(`customer-content.cjs is out of step with the site: ${message}`); };
  const ids = CATALOG.map((item) => item.id);
  if (JSON.stringify(ids) !== JSON.stringify(content.customerOrder)) fail('catalog order differs from customerOrder');
  if (JSON.stringify(ids.slice(0, 6)) !== JSON.stringify(content.topPicks)) fail('top picks differ');
  const byId = Object.fromEntries(content.candidates.map((item) => [item.id, item]));
  for (const item of CATALOG) {
    if (byId[item.id].name !== item.name) fail(`name for ${item.id}`);
    if (JSON.stringify(onboarding.onboarding[item.id].problems) !== JSON.stringify(item.problems)) fail(`problems for ${item.id}`);
  }
  if (JSON.stringify(onboarding.problems) !== JSON.stringify(Object.fromEntries(Object.keys(onboarding.problems).map((key) => [key, PROBLEMS[key]])))) fail('problem labels');
}

module.exports = {
  HUB_URL, BRAND, LOGO, TAGLINE, DISCLAIMER, PROBLEMS, CATALOG, TOP_PICKS,
  VALUE, STARTERS, JOURNEY, THIRTY_DAYS, CAPACITY, MEASURES, checkAgainstSite,
};
