// Public references only. Package revisions are reviewed independently of lab evidence.
export const problems = {
  engineering: 'Systems are hard to understand or change',
  answers: 'Information is hard to find',
  documents: 'Document review takes too long',
  drafting: 'Writing and analysis are repetitive',
  service: 'Staff and customers need better assistance',
  data: 'Data is difficult to turn into insight',
};

const source = (repo, revision) => ({
  repository: `https://github.com/${repo}/tree/${revision}`,
  guide: `https://github.com/${repo}/blob/${revision}/README.md`,
  revision,
});
export const sources = {
  knowledge: source('Azure-Samples/chat-with-your-data-solution-accelerator', '0fce71307dfa76a82ac82ec73bdde3daa47e503d'),
  orchestration: source('microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator', '8ac703a71f10b622bd3c82a9cc2b5dfe921c3025'),
  mining: source('microsoft/Document-Knowledge-Mining-Solution-Accelerator', '7df8ed33a86dd4f0f9e7417e882039fd38556e59'),
  processing: source('microsoft/content-processing-solution-accelerator', '659eaa1f503dd08b1e1aea1c72eab11c7c191d00'),
  chatbot: source('microsoft/customer-chatbot-solution-accelerator', 'cb86d1153df30a1bc6e744d74d3ff583764cd154'),
  conversation: source('microsoft/Conversation-Knowledge-Mining-Solution-Accelerator', '8a00aa54bc25fd3624020648c63f2c069172d8ca'),
  modernize: source('microsoft/Modernize-your-code-solution-accelerator', '7592ea97550fb711d7d8b64186875967d574c5d5'),
  planetary: source('microsoft/Planetary-Explorer', 'cadb0b0631844bec9bf369ea2a46024dc2bd4cf3'),
  generation: source('microsoft/content-generation-solution-accelerator', 'fa956c9ec374f0f7e9b03ae2873d38e5269186fe'),
  platform: source('microsoft/Deploy-Your-AI-Application-In-Production', '1ed62d982f777b85f3fe281adfd7150921ccd9ce'),
  employee: source('microsoft/Employee-Self-Service-Agent-Developer-Kit', '3236a513b7312b13602326fbdf7778797174d45f'),
  foundation: source('microsoft/agentic-applications-for-unified-data-foundation-solution-accelerator', '28c25024e43884b0a23c996d5cc8d3419f4e448c'),
  operations: source('microsoft/real-time-intelligence-operations-solution-accelerator', 'cfbdb91ee83ed31b5ccc5de7feca7a0b5b2e5f68'),
  stepfly: source('microsoft/StepFly', 'a6229192a69dd2eebc58d9b8f754dbc396029c4e'),
  video: source('Azure-Samples/netaivideoanalyzer', '1d8ed2ece3ee4c05441f98a0e06965c0207f21e7'),
  voiceagent: source('Azure-Samples/art-voice-agent-accelerator', 'a2e1ce2edbf103661c56a861cccef73c30acacee'),
  mcpsecurity: source('Azure-Samples/sherpa', '12be921ec85bd915105d9c6b5335cffe8c680966'),
};

export const platformGuides = {
  byok: 'https://docs.github.com/en/copilot/concepts/models/bring-your-own-key',
  enterpriseByok: 'https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/enable-custom-models',
  vscode: 'https://code.visualstudio.com/docs/agent-customization/language-models',
  voice: 'https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-bring-your-own-model',
  containers: 'https://learn.microsoft.com/en-us/azure/container-apps/overview',
  extraction: 'https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/retrieval-augmented-generation?view=doc-intel-4.0.0',
};

export const onboarding = {
  1: { problems: ['answers'] },
  2: { problems: ['drafting'] },
  3: { problems: ['engineering'] },
  4: { problems: ['answers', 'documents'] },
  5: { problems: ['engineering'] },
  6: { problems: ['documents'] },
  7: { problems: ['service', 'answers'] },
  8: { problems: ['drafting', 'data'] },
  9: { problems: ['engineering'] },
  10: { problems: ['data'] },
  11: { problems: ['service'] },
  12: { problems: ['documents'] },
  13: { problems: ['drafting'] },
  14: { problems: ['engineering'] },
  15: { problems: ['service', 'answers'] },
  16: { problems: ['data', 'answers'] },
  17: { problems: ['data'] },
  18: { problems: ['engineering'] },
  19: { problems: ['data'] },
  20: { problems: ['engineering'] },
  21: { problems: ['service'] },
  22: { problems: ['engineering'] },
};

export const tenantSteps = [
  'Agree one outcome, an accountable business owner, an engineering owner and measurable acceptance criteria.',
  'Confirm data permission, identity, service and region availability, model/API compatibility, quota, licenses and the full service budget.',
  'Open the pinned source and later maintenance notices. Review prerequisites, license, support ownership and deployment templates; retain the reviewed revision or explicitly approve its replacement.',
  'Have the tenant platform team adapt configuration to approved network and identity controls. Inspect model-resource creation even when reusing a project; verify intended endpoint and persisted-agent routing. Obtain approval before deployment commands.',
  'Deploy only into an approved pilot environment using the chosen package instructions. Use synthetic or permitted data and bounded spending.',
  'Test the named outcome, access restrictions, failure handling and costs. Assign monitoring, support and rollback ownership before any wider rollout.',
];
