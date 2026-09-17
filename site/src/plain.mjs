// Plain-language explanations for readers who have never seen these packages.
// Every statement here is a restatement of the reviewed dossier content in ordinary
// words. It introduces no capability, measurement or readiness claim of its own:
// `benefits` describes the gain a package is designed to produce, never evidence that
// it did. Tested status stays with the evidence panel on each solution page.
export const plainLanguage = {
  1: {
    form: 'A web application you deploy: a chat window for staff, plus an admin page for loading documents.',
    what: 'A private question-answering site for your own documents. You load an approved collection — policies, procedures, manuals — and staff ask questions in ordinary language. Every answer shows the passage it came from, so the reader can check it rather than trust it.',
    does: [
      'Takes documents and web pages you upload and prepares them for search.',
      'Finds the passages that relate to a question before it answers.',
      'Writes the answer in plain language with citations to the source.',
      'Keeps the conversation so people can ask follow-up questions.',
    ],
    benefits: [
      'People stop asking colleagues where a policy lives and get the passage itself.',
      'Answers are checkable: a citation means a reader can confirm it.',
      'New joiners find the reasoning behind an unfamiliar process without interrupting someone senior.',
    ],
    chooseIf: [
      'Your problem is really "the answer is in our documents somewhere".',
      'Readers need to see the source, not just a confident paragraph.',
    ],
    insteadIf: [
      'You need to compare many documents or filter a large collection: see Document Knowledge Mining.',
      'You need the same fields pulled out of every file into a record: see Content Processing.',
    ],
  },
  2: {
    form: 'A web application you deploy, plus an engine engineers configure for each workflow.',
    what: 'A way to break one large task into steps, give each step to a specialised assistant, and have a coordinator keep them in order. You watch the steps happen instead of receiving only a final answer. It is a foundation to configure, not a finished business system.',
    does: [
      'Splits a submitted task into steps and assigns each to a specialised agent.',
      'Runs those steps, letting agents use only the tools you permit.',
      'Shows the intermediate work so a person can inspect the reasoning.',
      'Combines the steps into one response for human review.',
    ],
    benefits: [
      'Work that normally spans several people can be drafted in one pass; the coordination is the point.',
      'Visible intermediate steps make an answer auditable instead of a single block of text to judge.',
      'One configurable engine can serve several workflows rather than commissioning a tool for each.',
    ],
    chooseIf: [
      'Your task genuinely has distinct stages that different specialists would handle.',
      'You need to inspect the intermediate work, not only the final output.',
    ],
    insteadIf: [
      'You only need answers from documents: a retrieval application such as Enterprise Knowledge is simpler.',
      'You need something dependable now: upstream describes this as a proof of concept, not for commercial use.',
    ],
  },
  3: {
    form: 'An owner-led engagement. No public package has been confirmed for this catalog.',
    what: 'The intended idea is to turn an existing codebase into written specifications engineers can read, review and keep current — useful when a system is inherited and nobody can state exactly what it does. This catalog has not confirmed an authoritative package or owner, so treat this as a scoping conversation rather than something to install.',
    does: [
      'Would take authorized source material as its input.',
      'Would produce structured specifications for engineers to review.',
      'Would leave a baseline to maintain as the system changes.',
    ],
    benefits: [
      'A written baseline for behaviour that currently exists only in the code and in people\u2019s heads.',
      'Change and handover discussions start from a document instead of a reading exercise.',
      'Requirements work has something concrete to argue with.',
    ],
    chooseIf: [
      'You own a system whose documented behaviour has drifted from its code.',
      'You can reach the offering owner to confirm what the package actually is.',
    ],
    insteadIf: [
      'You want to change or translate code rather than describe it: see Modernize.',
      'You need something deployable today: no confirmed package stands behind this entry.',
    ],
  },
  4: {
    form: 'A web application you deploy for searching, filtering and comparing a document collection.',
    what: 'A research workbench for a body of documents. It reads the text and the pictures in your files, pulls out topics, names and other details you can filter by, and lets you ask questions across everything, across a chosen subset, or of one document at a time.',
    does: [
      'Processes both text and images in uploaded documents into searchable material.',
      'Extracts topics, entities and metadata so a large collection can be narrowed.',
      'Answers questions across all documents, a selected set, or a single file.',
      'Suggests follow-up questions to continue an investigation.',
    ],
    benefits: [
      'Narrowing comes first: a large collection is cut to the relevant few before anyone reads.',
      'Comparing documents against each other is the built-in job, not something assembled by hand.',
      'Scans and image-heavy material become searchable instead of sitting in a folder.',
    ],
    chooseIf: [
      'You have many documents and the hard part is finding and comparing the relevant ones.',
      'Your material includes scans, diagrams or images that plain text search misses.',
    ],
    insteadIf: [
      'You mainly need one trusted answer from a maintained policy set: Enterprise Knowledge is lighter to run.',
      'You need identical fields extracted from every document: see Content Processing.',
    ],
  },
  5: {
    form: 'A configuration choice inside tools developers already use. There is no application to deploy.',
    what: 'A way to point developer tools such as Visual Studio Code or GitHub Copilot at a model your organization chooses, instead of only the default one. Two different routes exist — one a developer configures locally, one an enterprise manages centrally — and they differ in licensing, network path and which features keep working.',
    does: [
      'Adds an organization-chosen model to the model picker in a supported client.',
      'Sends developer requests to that model instead of the default one.',
      'Lets administrators manage which custom models the enterprise may use.',
    ],
    benefits: [
      'Developers keep the tool they know while the organization decides which model does the work.',
      'Model choice and provider billing become an administrative decision rather than an individual one.',
      'A bounded pilot can compare a preferred model against real development tasks before any rollout.',
    ],
    chooseIf: [
      'Your developers already use a supported client and the only question is which model answers.',
      'You need central control over model choice or provider billing.',
    ],
    insteadIf: [
      'You want a new application for staff rather than a change to developer tooling.',
      'You expect every Copilot feature to work unchanged: coverage depends on the route and the client.',
    ],
  },
  6: {
    form: 'A web application you deploy that follows documents through a processing pipeline.',
    what: 'An intake system for packs of related documents; the example built in is an insurance claim. Each document is read and its fields pulled out and checked, then the pack is summarised as a whole with a report of what is missing. Moving it to a different intake process means rewriting the field definitions and rules.',
    does: [
      'Extracts fields from each document and maps them to a defined schema.',
      'Evaluates and stores each result with a confidence score.',
      'Summarises the pack as a whole rather than one file at a time.',
      'Reports what the pack is missing, linked back to the documents reviewed.',
    ],
    benefits: [
      '"Is this pack complete?" is answered before a reviewer spends time on it.',
      'Structured fields come out of unstructured paperwork, so other systems can use them.',
      'Findings point back at the documents, so a reviewer checks rather than trusts.',
    ],
    chooseIf: [
      'Work arrives as a bundle of related documents that must be checked for completeness.',
      'You need consistent fields from every document, not a conversation.',
    ],
    insteadIf: [
      'You want to explore and compare documents rather than process them to a schema: see Document Knowledge Mining.',
      'You are assessing bids or contracts against a rubric: see RFP & contract review, which is a proposed workflow only.',
    ],
  },
  7: {
    form: 'A web application you deploy: an example storefront plus a chat widget that embeds in it.',
    what: 'An assistant that sits inside a customer-facing website and answers questions about products and policies, passing different kinds of question to different specialists behind the scenes. Example retail, healthcare and banking storefronts are included with sample data; those are demonstrations, not connections to any real ordering or banking system.',
    does: [
      'Embeds a chat widget into a host website.',
      'Routes each question to a product specialist or a policy specialist.',
      'Answers from the supplied catalog and policy material.',
      'Includes an optional spoken-conversation path.',
    ],
    benefits: [
      'Routine "where is my order" and "what is the return policy" traffic is answered where the customer already is.',
      'Separating product questions from policy questions keeps each answer closer to its source.',
      'Three industry examples give a concrete starting shape instead of a blank page.',
    ],
    chooseIf: [
      'You are prototyping a customer-facing assistant and want a complete shape to study.',
      'Your questions divide cleanly into product facts and written policy.',
    ],
    insteadIf: [
      'You are close to putting this in front of customers: its grounded-answer test failed here, so treat it as a prototype to repair.',
      'Your users are staff rather than customers: Enterprise Knowledge fits internal question answering.',
    ],
  },
  8: {
    form: 'A web application you deploy, with screens for loading data, exploring it and viewing dashboards.',
    what: 'A way to look across a large pile of recorded conversations — support calls, chats, transcripts — and find the themes, rather than reading them one at a time. It can both quote individual conversations as evidence and count them, because it uses search for examples and database queries for totals.',
    does: [
      'Takes in conversation records and enriches them for search.',
      'Answers questions using both retrieved examples and calculated totals.',
      'Builds dashboards from the measures you define.',
      'Links an aggregate number back to the records behind it.',
    ],
    benefits: [
      'A recurring problem becomes a counted theme instead of an anecdote someone remembers.',
      'The number and its supporting examples sit together, so the claim can be checked.',
      'Analysis covers the whole set, not the handful someone had time to read.',
    ],
    chooseIf: [
      'You hold a permitted set of conversation records and want themes and trends across them.',
      'You need both the statistic and the examples underneath it.',
    ],
    insteadIf: [
      'Your source material is documents rather than conversations: see Document Knowledge Mining.',
      'You need this dependable now: the tested output had meaning-level defects that need repair first.',
    ],
  },
  9: {
    form: 'A web application you deploy for converting code in batches.',
    what: 'A conversion assistant for one specific database migration: Informix SQL into T-SQL, the dialect SQL Server uses. You upload a batch of SQL; it translates, checks the result against a real T-SQL parser, reviews the meaning and lets you export the drafts for your engineers to test properly. It is not a general "migrate anything" tool.',
    does: [
      'Converts a batch of Informix SQL into T-SQL drafts.',
      'Checks the generated syntax with a parser, not only a model opinion.',
      'Reviews each translation for meaning and attempts repairs.',
      'Exports the drafts and a processing summary for independent testing.',
    ],
    benefits: [
      'The tedious first pass of a migration is drafted in bulk, leaving engineers the judgement work.',
      'A parser check catches broken syntax before an engineer spends time on it.',
      'Progress becomes countable across a batch instead of tracked file by file.',
    ],
    chooseIf: [
      'You are moving Informix SQL to SQL Server and want reviewable drafts at volume.',
      'Your engineers will test the output against the target database themselves.',
    ],
    insteadIf: [
      'Your dialect is not Informix, or the job is SAS or whole-application migration: this package does not establish those.',
      'You want a system described rather than its code converted: see SpecSuite, subject to its open questions.',
    ],
  },
  10: {
    form: 'A web application you deploy: a map beside a conversation.',
    what: 'An Earth-observation explorer. You ask about a place and a time period in ordinary language — vegetation, surface water, how somewhere has changed — and it finds suitable satellite imagery, loads it onto a map and helps interpret what you are seeing. It is an open-source project, not a supported Microsoft product.',
    does: [
      'Turns a place-and-time question into a search across public geospatial datasets.',
      'Loads the matching imagery as layers on an interactive map.',
      'Helps interpret the result alongside the imagery it used.',
      'Keeps the underlying scenes available so the answer can be inspected.',
    ],
    benefits: [
      'Finding the right imagery, normally a specialist task, starts from an ordinary question.',
      'The answer and the picture behind it stay side by side, so an interpretation can be challenged.',
      'Non-specialists can take part in an analysis that would otherwise need an expert to drive.',
    ],
    chooseIf: [
      'You have genuine Earth-science or environmental questions and a specialist who can sanity-check answers.',
      'Satellite imagery is your evidence base.',
    ],
    insteadIf: [
      'Your data is business data rather than imagery: see Agentic Unified Data Foundation.',
      'You need a supported product with a support agreement behind it.',
    ],
  },
  11: {
    form: 'A Microsoft service your application talks to. There is no application to deploy.',
    what: 'The live-speech layer that wraps around a model: it listens, manages the back-and-forth of a spoken conversation, and speaks the reply. "Bring your own model" means the thinking can be done by a model deployment your organization controls rather than only a service-managed one. The application around it is still yours to build.',
    does: [
      'Runs a real-time microphone session with speech in and speech out.',
      'Handles turn taking and interruption inside the conversation.',
      'Can send the reasoning to a compatible model deployment you own.',
      'Leaves the business logic, escalation and interface to your application.',
    ],
    benefits: [
      'Spoken access opens a service to people for whom typing is slow, awkward or impossible.',
      'Using your own model deployment keeps the reasoning on a route you control.',
      'A ready-made client exists, so speech behaviour can be judged before an application is built.',
    ],
    chooseIf: [
      'Speech is the point: the interaction has to be spoken rather than typed.',
      'Your workflow is narrow and well bounded rather than open-ended conversation.',
    ],
    insteadIf: [
      'You want the telephony and call handling built for you as well: see Real-time voice agents.',
      'Text is acceptable: it is cheaper, simpler and far easier to evaluate.',
    ],
  },
  12: {
    form: 'A proposed workflow. No verified package or deployment route stands behind it yet.',
    what: 'A design for helping reviewers work through bids, proposals or contracts: locating the relevant passages, checking them against criteria agreed in advance, and showing the reviewer the evidence behind each finding. Nothing here has been built or tested. It is a shape for a pilot, written so a discussion can start from something concrete.',
    does: [
      'Would extract passages from an authorized document pack.',
      'Would compare them against a rubric your team agrees beforehand.',
      'Would present each finding linked to the passage supporting it.',
      'Would leave every decision to a named human reviewer.',
    ],
    benefits: [
      'Reviewers start from located evidence instead of a cold read of the whole pack.',
      'An agreed rubric makes review consistent between different reviewers.',
      'Missing information surfaces while it can still be requested.',
    ],
    chooseIf: [
      'You want to scope a reviewer-assistance pilot and can define the rubric.',
      'Your reviewers stay the decision-makers throughout.',
    ],
    insteadIf: [
      'You need something deployable now: no verified package exists for this entry.',
      'Your documents arrive as structured intake packs: see Content Processing.',
    ],
  },
  13: {
    form: 'An internal web application you deploy for drafting marketing material.',
    what: 'A drafting workspace for campaigns. You fill in a brief — audience, message, tone, what you need, the call to action — and a set of specialised assistants research the product, write copy, generate images and check the result against your brand guidelines. It produces drafts for an editor, not material ready to publish.',
    does: [
      'Turns a completed creative brief into a structured request.',
      'Researches the relevant product or catalog material.',
      'Generates draft copy and draft images.',
      'Returns brand-guideline feedback graded by severity.',
    ],
    benefits: [
      'The blank page disappears: reviewers edit a draft instead of commissioning one.',
      'Brand feedback arrives during drafting rather than at the end of an approval queue.',
      'Variations are cheap, so choices get made by comparison.',
    ],
    chooseIf: [
      'Your work is marketing content and you have brand guidance to check against.',
      'An editor approves everything before it is published.',
    ],
    insteadIf: [
      'You need official correspondence or briefing drafts: that is a planned workflow on the roadmap, not this package.',
      'You need factual or legal clearance: brand feedback is neither.',
    ],
  },
  14: {
    form: 'Infrastructure templates engineers run. There is no user interface and nobody logs in.',
    what: 'The groundwork an AI application needs before it can be hosted properly: network, identity, monitoring, AI and search services, expressed as configuration your platform team can read and challenge. Its users are the engineers who will host something else on top of it. The name of the package does not make anything deployed from it production-certified.',
    does: [
      'Provisions a configurable Azure environment from reviewed templates.',
      'Sets up AI and search services for an application to use.',
      'Offers optional data-platform and governance integrations, each with its own prerequisites.',
      'Leaves the business application itself to be onboarded separately.',
    ],
    benefits: [
      'Environment decisions are made once, reviewably, instead of improvised per project.',
      'Platform responsibilities and application responsibilities stay clearly separated.',
      'The configuration can be argued with before anything is created.',
    ],
    chooseIf: [
      'You are preparing to host an AI application and need the environment agreed first.',
      'Your platform team would rather review configuration than receive a finished environment.',
    ],
    insteadIf: [
      'You are looking for something staff can use: this has no end-user experience at all.',
      'Your tenant already has an approved landing-zone pattern.',
    ],
  },
  15: {
    form: 'A toolkit for the people who build a Copilot Studio agent. It is not itself a deployable chatbot.',
    what: 'A kit for the makers who build and maintain an employee help agent in Microsoft Copilot Studio. It helps them prepare answer topics, connect approved HR and IT systems, and test the result before publishing. The employee-facing agent is set up and licensed separately; installing this kit does not create it.',
    does: [
      'Gives makers a prepared workspace for building topics and templates.',
      'Supports configuration of approved employee-service integrations.',
      'Provides evaluation material for testing a journey before release.',
      'Synchronises approved changes through the platform.',
    ],
    benefits: [
      'Changes to employee answers are tested before staff ever see them.',
      'HR and IT knowledge is maintained deliberately instead of edited live.',
      'Makers work to a structured method rather than inventing conventions per change.',
    ],
    chooseIf: [
      'You already run, or plan to run, an employee agent in Copilot Studio.',
      'Your Power Platform administrators are involved from the start.',
    ],
    insteadIf: [
      'You want a standalone assistant hosted in your own Azure environment: this is not that.',
      'You are assuming reserved model capacity will serve it: that routing is not established here.',
    ],
  },
  16: {
    form: 'A web application you deploy that answers questions about governed business data.',
    what: 'A conversational way into business data that is already governed in Microsoft Fabric — sales, product or customer questions asked in ordinary language and answered from the records themselves, not from documents about them. Retail and insurance example datasets are included so the shape can be tried before your own data is involved.',
    does: [
      'Takes a business question through an authenticated web application.',
      'Turns it into governed queries against Fabric data.',
      'Returns an answer with the data context behind it.',
      'Ships example datasets whose answers can be checked against a known query.',
    ],
    benefits: [
      'Business questions get asked directly instead of queued as report requests.',
      'Answers come from the governed dataset, so permissions and definitions still apply.',
      'Example data makes it possible to verify an answer against a known-correct result.',
    ],
    chooseIf: [
      'Your data already lives in Fabric and is governed there.',
      'The questions are about records and numbers rather than documents.',
    ],
    insteadIf: [
      'Your answers live in documents: see Enterprise Knowledge or Document Knowledge Mining.',
      'You expect all reasoning to run on your reserved capacity: part of this route uses Microsoft-managed AI.',
    ],
  },
  17: {
    form: 'A Fabric-based starting point: live dashboards, alert rules and a data agent to ask questions.',
    what: 'A worked example of operational monitoring. Equipment and sensor readings stream in, appear on a live dashboard, and raise an alert when a rule you set is crossed; the history can then be questioned in ordinary language. It arrives with invented factory data and a simulator, so it can be explored before any real telemetry is connected.',
    does: [
      'Streams telemetry into a real-time store and dashboard.',
      'Sends configured notifications when an alert rule is met.',
      'Answers questions over historical and streaming data.',
      'Includes synthetic data and an event simulator for exploration.',
    ],
    benefits: [
      'Operational patterns become visible in the moment rather than in next week\u2019s report.',
      'Alerts reach the people who can act, through rules you control.',
      'Investigating an anomaly stops being a query-writing exercise.',
    ],
    chooseIf: [
      'You have streaming operational or sensor data and already use Microsoft Fabric.',
      'Dashboards and alerts are the outcome you want, not a chat interface.',
    ],
    insteadIf: [
      'You need safety-critical or production monitoring: this is a demonstration starting point.',
      'Your data is not telemetry: the pattern will not transfer cleanly.',
    ],
  },
  18: {
    form: 'A research prototype with a web dashboard. It is not a product.',
    what: 'An experiment in automating incident diagnosis. It takes a written troubleshooting guide, turns it into a plan of diagnostic steps and works through them with tools, showing its reasoning at each stage. In this catalog\u2019s evaluation it did not reach a correct root cause, so it belongs in a research conversation rather than an operations one.',
    does: [
      'Converts a troubleshooting guide into a planned sequence of diagnostic steps.',
      'Runs those steps using permitted diagnostic tools.',
      'Keeps shared context so later steps use earlier findings.',
      'Shows the full execution trace for review.',
    ],
    benefits: [
      'Troubleshooting knowledge that sits in documents becomes something executable.',
      'The diagnostic path is visible, so a conclusion can be argued with.',
      'Routine first-line investigation could begin before an engineer picks up the incident.',
    ],
    chooseIf: [
      'You are exploring research directions in automated diagnosis.',
      'You have written troubleshooting guides and a safe, synthetic incident to test against.',
    ],
    insteadIf: [
      'You need something dependable for live incidents: it did not reach the intended outcome in testing.',
      'You want engineering assistance for code rather than incidents: see Modernize.',
    ],
  },
  19: {
    form: 'A small reference application developers run and adapt.',
    what: 'A developer sample that describes what is in a video by taking still frames from it and asking a model about those pictures. You choose how many frames to sample and what to ask. Because it looks at samples rather than the whole video, brief events between frames can be missed entirely.',
    does: [
      'Accepts a video and extracts a chosen number of frames.',
      'Sends the selected frames to a model together with your prompt.',
      'Returns a written description, the frame count and a sample image.',
      'Lets you compare the effect of different sampling settings and prompts.',
    ],
    benefits: [
      'A rough description of visual material is produced without watching all of it.',
      'The sampling trade-off is visible and adjustable rather than hidden.',
      'It is small enough for a developer to read and understand end to end.',
    ],
    chooseIf: [
      'You want to judge whether frame-based description is good enough for a narrow task.',
      'Your team works in .NET and wants a readable starting sample.',
    ],
    insteadIf: [
      'You need spoken audio transcribed or events timestamped: it does neither.',
      'You need continuous or reliable detection: sampling will miss things.',
    ],
  },
  20: {
    form: 'Nothing yet. This is an inventory placeholder with no confirmed package or owner.',
    what: 'This entry exists so that a name in the inventory is not quietly dropped. No authoritative package, owner or deployment route has been established, so nothing is claimed about what it does. The honest next step is identification, not evaluation.',
    does: [
      'Holds a place in the inventory while the offering is identified.',
      'Records what must be established before any assessment can begin.',
    ],
    benefits: [
      'Keeping an unknown visible stops it being mistaken for either a capability or an oversight.',
      'A named gap can be assigned to someone; a forgotten one cannot.',
    ],
    chooseIf: [
      'You can identify the intended offering, or name its owner.',
    ],
    insteadIf: [
      'You are choosing something to pilot: this entry has nothing to pilot.',
    ],
  },
  21: {
    form: 'An engineering codebase teams build on. It is not a finished application.',
    what: 'The working parts of a spoken agent that answers a phone call or a browser conversation: taking the call, streaming audio both ways, knowing when the caller has stopped speaking, and passing the conversation to a person when it should not continue. The agent\u2019s actual business logic is yours to write. The package describes itself as covering roughly the first eighty per cent of the work.',
    does: [
      'Connects a call arriving from a telephone number or a browser.',
      'Streams audio in both directions while the conversation is happening.',
      'Manages turn taking and interruption.',
      'Offers two audio approaches behind one switch: separate speech steps, or a single managed voice-to-voice service.',
      'Provides a documented route for handing the caller to a person.',
    ],
    benefits: [
      'The hardest engineering in a voice agent, real-time audio and turn taking, is already solved, so the team works on the conversation.',
      'Two audio paths behind one switch mean the latency and control trade-off can be measured rather than argued.',
      'A clean handoff to a person is designed in, rather than added after the first bad call.',
    ],
    chooseIf: [
      'Callers must speak to something immediately, and routine enquiries dominate the volume.',
      'You have engineers who will own a real-time service, including how it fails.',
    ],
    insteadIf: [
      'You only need speech added to one bounded workflow: Voice Live is a much smaller step.',
      'You cannot fund telephony numbers, real-time speech and always-on hosting: none of them are free.',
    ],
  },
  22: {
    form: 'A hands-on training workshop in a repository. It is deliberately not a product.',
    what: 'A security course for engineers, built as a climb through progressive camps. Its subject is the connection between an AI agent and the tools or data it reaches — the Model Context Protocol, or MCP, now the common way to make that connection. Each camp stands up something insecure, attacks it, fixes it with an Azure control, then proves the attack no longer works.',
    does: [
      'Walks engineers through staged exercises covering identity, gateway controls, input and output safety, and monitoring.',
      'Deploys deliberately vulnerable servers and supplies working exploits against them.',
      'Applies the control that defeats each attack, then re-runs the attack to prove it.',
      'Maps its exercises to a published list of the top MCP risks.',
    ],
    benefits: [
      'Engineers who have broken something insecure themselves review agent tooling differently afterwards.',
      'A team gains shared vocabulary and a checklist, so security review stops depending on one person.',
      'Weaknesses are found in a training environment instead of a shared one.',
    ],
    chooseIf: [
      'Your teams are exposing tools or data to AI agents, or are about to.',
      'You can provide a disposable, isolated environment with no production connectivity.',
    ],
    insteadIf: [
      'You are looking for software to deploy: this produces skilled engineers, not an application.',
      'You cannot isolate the environment: it deploys working vulnerabilities by design.',
    ],
  },
};
