// Authored selection guidance from public sources, separate from functional evidence.
export const programReviewDate = '2026-09-20';

export const pathways = [
  {
    id: 'engineering', title: 'Engineering Modernization', lead: 'Owner-supported adaptation',
    outcome: 'Make a bounded SQL migration reviewable and testable.',
    primary: 9, extensions: [3, 5],
    scope: 'One SQL dialect, a small permitted source set and an executable source/target comparison. Broader engineering tooling is a separate scope.',
    gate: 'The Modernize upstream is no longer maintained. Name a maintenance owner or choose a supported replacement before a new deployment.',
    measures: [
      ['Outcome', 'Reviewer time per accepted migration compared with the current process.'],
      ['Quality', 'Source/target execution equivalence, preserved interfaces and regression results.'],
      ['Adoption', 'Accepted changes and repeat use across a real modernization backlog.'],
    ],
    boundary: 'Engineers approve every change. No automatic production changes or claim of complete migration equivalence.',
    extension: 'Specification assistance or supported developer-tool integration only after owner and endpoint validation.',
  },
  {
    id: 'knowledge', title: 'Knowledge & Staff Work', lead: 'Recommended first pilot',
    outcome: 'Help staff find authoritative answers they can check.',
    primary: 1, extensions: [4],
    scope: 'One approved document collection, one user group and representative questions, including missing answers and restricted documents.',
    gate: 'Start with Chat With Your Data. Accept citation quality, permission boundaries and safe no-answer behavior before broader use.',
    measures: [
      ['Outcome', 'Time to a source-verified answer compared with the current search process.'],
      ['Quality', 'Citation correctness, unsupported answers and permission-boundary failures.'],
      ['Adoption', 'Repeat users and successfully completed knowledge tasks, not raw query count.'],
    ],
    boundary: 'People check consequential answers. Controlled briefing and correspondence drafting remains a planned extension.',
    extension: 'Add document comparison only for a demonstrated gap; DKM needs a maintenance owner. Avoid a second overlapping retrieval stack.',
  },
  {
    id: 'procurement', title: 'Procurement & Document Operations', lead: 'Document-workflow priority',
    outcome: 'Prepare complete evidence packs for a human reviewer.',
    primary: 6, extensions: [12],
    scope: 'One document-pack type with known complete, incomplete and malformed examples. Start with Content Processing, not autonomous procurement.',
    gate: 'Prove complete-pack processing as well as missing-evidence detection. RFP and contract review remains a separate, gated workflow.',
    measures: [
      ['Outcome', 'Reviewer preparation time and rework per accepted document pack.'],
      ['Quality', 'Material-field accuracy, missed evidence and unsupported findings.'],
      ['Adoption', 'Accepted packs and recurring intake volume within the approved service budget.'],
    ],
    boundary: 'Authorized reviewers retain compliance, supplier-selection and award decisions. A generated finding is not a decision.',
    extension: 'Use MACAE RFP/contract packs as implementation references only after final synthesis and evidence traceability pass.',
  },
];

export const pilotGates = [
  ['Scope and ownership', 'Name business, engineering and review owners. Agree the baseline, target, permitted data, representative examples, time box and spending limit before starting.'],
  ['Outcome and safety', 'Evaluate the complete user journey, material errors, citations, permissions, missing inputs and escalation. Source inspection and successful provisioning are not acceptance.'],
  ['Routing and economics', 'Trace every model path, including persisted agents and retrieval planning. Confirm deployment, model/version, API and approved geography; compare Standard, eligible Batch and existing PTU headroom.'],
  ['Operate or stop', 'Expand only after agreed quality, useful demand and operating ownership are established. Otherwise repair, change the approach or stop; do not generate work to fill capacity.'],
];

export const programSources = [
  { label: 'Current solution accelerator catalog', url: 'https://accelerators.ms/#section=accelerators' },
  { label: 'MSUS accelerator scenario catalog', url: 'https://msusazureaccelerators.github.io/' },
];

const readme = (repo, revision) => `https://github.com/${repo}/blob/${revision}/README.md`;
export const catalogReview = [
  {
    name: 'Chat with Your Data', decision: 'First pilot',
    reason: 'One shared knowledge workbench; verify citations, permissions and actual model routing.',
    url: readme('Azure-Samples/chat-with-your-data-solution-accelerator', '0fce71307dfa76a82ac82ec73bdde3daa47e503d'),
  },
  {
    name: 'Content Processing', decision: 'Core workflow to validate',
    reason: 'Document intake and completeness; full intended outcome still needs acceptance.',
    url: readme('microsoft/content-processing-solution-accelerator', '9a3f15e4b1403c0851507a9009bc1d39141c4eab'),
  },
  {
    name: 'Multi-Agent Custom Automation Engine', decision: 'Scoped workflow development',
    reason: 'RFP and contract-review packs, not another generic agent product. Require final synthesis and human review.',
    url: readme('microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator', 'e89689e475eecf23ef2b48ad9e556bde16776e8d'),
  },
  {
    name: 'Modernize Your Code', decision: 'Maintenance owner required',
    reason: 'SQL-dialect conversion, not arbitrary code migration. Upstream says no longer maintained.',
    url: readme('microsoft/Modernize-your-code-solution-accelerator', 'f5d25c1f8bbe391b13c43ad5a8f7ea835aef1e7a'),
  },
  {
    name: 'Document Knowledge Mining', decision: 'Selective owned adaptation',
    reason: 'Keep distinctive comparison capabilities only where needed. Upstream says no longer maintained.',
    url: readme('microsoft/Document-Knowledge-Mining-Solution-Accelerator', '1d9b68967d540c972357dd08286e08fcaf8bcc39'),
  },
  {
    name: 'Customer Chatbot', decision: 'Service-specific expansion',
    reason: 'Use for a named service operation after grounded-answer and escalation acceptance, not another generic FAQ.',
    url: readme('microsoft/customer-chatbot-solution-accelerator', 'cb86d1153df30a1bc6e744d74d3ff583764cd154'),
  },
  {
    name: 'Conversation Knowledge Mining', decision: 'Analysis-specific expansion',
    reason: 'Validate analytical correctness first. Nonurgent transcript analysis may fit Batch better than reserved capacity.',
    url: readme('microsoft/Conversation-Knowledge-Mining-Solution-Accelerator', 'fd8210c286dbb3f6ca39f83e6afb9eb924dde668'),
  },
  {
    name: 'Microsoft IQ', decision: 'Supply-chain assessment only',
    reason: 'Supplier disruption and contract-informed analysis with substantial Fabric and M365 dependencies. Not added as a validated catalog app.',
    url: readme('microsoft/microsoft-iq-solution-accelerator', '2f457295896d7739886f4bbf1ae881cf71470610'),
  },
  {
    name: 'Container Migration', decision: 'Specialist owned adaptation',
    reason: 'Only for an active Kubernetes migration program. Upstream says no longer maintained; not a default addition.',
    url: readme('microsoft/Container-Migration-Solution-Accelerator', '47e6c70b1612f82329b5d295092407ff9e584166'),
  },
  {
    name: 'Multi-Agent Content Generation', decision: 'Marketing-specific option',
    reason: 'Marketing copy and images, not controlled policy or briefing drafts. Image costs are separate.',
    url: readme('microsoft/content-generation-solution-accelerator', 'fa956c9ec374f0f7e9b03ae2873d38e5269186fe'),
  },
  {
    name: 'Agentic Applications for Unified Data Foundation', decision: 'Existing data-platform option',
    reason: 'Consider only with governed data, a sponsor and existing Fabric prerequisites; verify customer-model routing.',
    url: readme('microsoft/agentic-applications-for-unified-data-foundation-solution-accelerator', '995d3007baae798e2a60f94e4dd8502b5b82dfa6'),
  },
  {
    name: 'Unified Data Foundation with Fabric', decision: 'Supporting data platform',
    reason: 'A data foundation, not evidence of customer PTU consumption. Do not buy a platform merely to create model demand.',
    url: readme('microsoft/unified-data-foundation-with-fabric-solution-accelerator', '167c308e58e5f1f8e864d103fa88339ce7445fd5'),
  },
  {
    name: 'Real-Time Intelligence for Operations', decision: 'Operations-specific option',
    reason: 'Telemetry, KQL and dashboards are not chat-model PTU workloads. A customer-PTU route was not established.',
    url: readme('microsoft/real-time-intelligence-operations-solution-accelerator', 'd2f8e7684de02f81182218ab6da41e23c5bda1de'),
  },
  {
    name: 'Data & Agent Governance and Security', decision: 'Reference, not an app slot',
    reason: 'Governance is necessary, not a standalone PTU demand source. Upstream says no longer maintained.',
    url: readme('microsoft/Data-and-Agent-Governance-and-Security-Accelerator', '17bb4d7d9ac643830868eb9439b595e2ea7c9928'),
  },
  {
    name: 'Deploy Your AI Application in Production', decision: 'Architecture reference',
    reason: 'Reuse an approved platform, not a duplicate stack. Upstream says no longer maintained; the name is not certification.',
    url: readme('microsoft/deploy-your-ai-application-in-production', '4fa38951a36484fb95a54f9e396f05b94a2b7f4c'),
  },
];

export const legacyGuidance = [
  ['Reuse scenarios, not old stacks', 'Document process automation, claims completeness and helpdesk escalation are useful workflow patterns for the selected modern components. Legacy frameworks and incomplete deployment instructions need fresh engineering review.'],
  ['Do not multiply the catalog', 'Several retail, government and conversational pages describe variants of the same partner offering. A sector label is not another application, and a partner claim is not verified model routing.'],
  ['Keep other AI workloads separate', 'IoT, vision, forecasting, fraud models, workplace analytics, data ingestion and governance labs may be valuable. Their existing processing is not customer Azure OpenAI PTU consumption.'],
];
