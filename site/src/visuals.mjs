// Authored workflow illustrations, not product screenshots or deployment evidence.
export const visualIcons = {
  code: 'm8 6-6 6 6 6m8-12 6 6-6 6M14 3l-4 18',
  document: 'M5 2h9l5 5v15H5V2Zm9 0v6h5M9 12h6m-6 4h6',
  answer: 'M3 3h18v14H9l-6 4V3Zm4 5h10M7 12h7',
  graph: 'M10 2h4v4h-4V2ZM2 18h4v4H2v-4Zm16 0h4v4h-4v-4ZM12 6v5M4 18v-7h16v7',
  check: 'm4 12 5 5L20 6',
  data: 'M3 3v18h19M7 16v-5m5 5V6m5 10V9',
  cloud: 'M6 19a5 5 0 1 1 0-10 7 7 0 0 1 13-1 5.5 5.5 0 0 1-1 11H6Z',
  shield: 'm12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6l9-4Zm-4 9 3 3 5-5',
  voice: 'M10 3h4v12h-4V3ZM6 10v3a6 6 0 0 0 12 0v-3M12 19v3m-4 0h8',
  search: 'M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Zm-2 5 6 6M7 8h6m-6 4h4',
  map: 'm2 5 7-3 6 3 7-3v17l-7 3-6-3-7 3V5Zm7-3v17m6-14v17',
  video: 'M2 5h20v14H2V5Zm8 3 6 4-6 4V8Z',
};

// Short labels describe intended flows; existing dossiers remain the claim authority.
export const solutionVisuals = {
  1: { audience: 'Knowledge teams', stages: [['document', 'Documents'], ['search', 'Retrieve'], ['answer', 'Cited answer']] },
  2: { audience: 'Workflow builders', stages: [['document', 'Task'], ['graph', 'Agent steps'], ['answer', 'Synthesis']] },
  3: { audience: 'Software teams', stages: [['code', 'Existing code'], ['graph', 'Specs + graph'], ['code', 'Code changes']] },
  4: { audience: 'Document reviewers', stages: [['document', 'Documents'], ['search', 'Compare'], ['answer', 'Findings']] },
  5: { audience: 'Developer teams', stages: [['code', 'Developer tool'], ['cloud', 'Model route'], ['answer', 'Assistance']] },
  6: { audience: 'Operations teams', stages: [['document', 'Documents'], ['graph', 'Extract'], ['data', 'Fields']] },
  7: { audience: 'Customer service teams', stages: [['answer', 'Visitor question'], ['search', 'Product + policy'], ['answer', 'Response']] },
  8: { audience: 'Service analysts', stages: [['answer', 'Conversations'], ['search', 'Find patterns'], ['data', 'Insights']] },
  9: { audience: 'Software teams', stages: [['code', 'Legacy code'], ['graph', 'Plan changes'], ['check', 'Review + test']] },
  10: { audience: 'Research teams', stages: [['map', 'Place + time'], ['search', 'Find imagery'], ['map', 'Map layers']] },
  11: { audience: 'Service builders', stages: [['voice', 'Speech'], ['cloud', 'Model'], ['voice', 'Spoken reply']] },
  12: { audience: 'Procurement teams', stages: [['document', 'RFP + contract'], ['search', 'Evidence'], ['check', 'Human review']] },
  13: { audience: 'Content teams', stages: [['document', 'Brief'], ['graph', 'Draft'], ['check', 'Editorial review']] },
  14: { audience: 'Platform teams', stages: [['code', 'Requirements'], ['cloud', 'Infrastructure'], ['shield', 'Validation']] },
  15: { audience: 'Assistant builders', stages: [['code', 'Toolkit'], ['graph', 'Configure'], ['answer', 'Assistant']] },
  16: { audience: 'Business data teams', stages: [['data', 'Fabric data'], ['graph', 'Data agent'], ['answer', 'Answer']] },
  17: { audience: 'Operations analysts', stages: [['data', 'Signals'], ['search', 'Investigate'], ['check', 'Human decision']] },
  19: { audience: 'Media app builders', stages: [['video', 'Video clip'], ['search', 'Sample frames'], ['document', 'Description']] },
  21: { audience: 'Voice app builders', stages: [['voice', 'Live audio'], ['graph', 'Agent tools'], ['voice', 'Response']] },
  22: { audience: 'Security learners', stages: [['code', 'Lab server'], ['search', 'Inspect risks'], ['shield', 'Practice controls']] },
};
