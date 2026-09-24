// Plain-language explanations for readers who have never seen these packages.
// Restates reviewed dossiers and the supplied SpecSuite product description.
// Examples illustrate intended use, not customer deployments or measured results.
// Tested status stays with the evidence panel on each solution page.
export const plainLanguage = {
  1: {
    brief: {
      what: 'An internal question-and-answer website for the information buried in your policies, manuals and procedures, with a chat screen for staff and a document-loading screen for administrators.',
      does: 'You load approved files or web pages. When someone asks a question, the app finds relevant passages, drafts an answer with source citations and supports follow-up questions.',
      value: 'Help employees find and understand existing guidance without opening dozens of files or repeatedly asking a subject-matter expert. Readers can check the cited source.',
      example: 'Load a travel handbook, ask which expenses need advance approval, then open the cited policy passage to confirm the answer.',
    },
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
      'You have a specialist comparison or filtering gap after a CWYD-first pilot: assess Document Knowledge Mining only with a named maintenance owner or approved replacement, not a duplicate stack.',
      'You need the same fields pulled out of every file into a record: see Content Processing.',
    ],
  },
  2: {
    brief: {
      what: 'A configurable application for tasks that need several AI assistants working in sequence, rather than one chatbot answering a question.',
      does: 'Engineers define specialist roles and permitted tools. A coordinator assigns the work, passes results between assistants and shows their intermediate outputs before attempting a combined response.',
      value: 'Prototype work that combines research, analysis and drafting in one reviewable process. It is not a finished business app; the recorded final-response failure needs repair.',
      example: 'Configure a briefing workflow in which one assistant gathers approved material, another compares findings and a third drafts a summary for a person to review.',
    },
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
    brief: {
      what: 'A private code-to-spec and spec-to-code tool for understanding and evolving existing or legacy software, designed to work across programming languages.',
      does: 'Analyzes a codebase into specifications and a knowledge graph: a connected map of behavior, components and dependencies. Engineers use the reviewed specifications to generate or improve code.',
      value: 'Understand unfamiliar systems, recover business rules, plan modernization and guide code changes. Confirm language and framework coverage on your own code rather than assuming universal support.',
      example: 'Take an inherited billing module, map its rules and dependencies, review the specification, then use it to guide an improved implementation and regression tests.',
    },
    form: 'Private code through an owner-approved access or delivery arrangement; confirm the supported package before deployment.',
    what: 'SpecSuite connects code-to-spec and spec-to-code work. Starting with an existing or legacy codebase, it is designed to recover specifications and build a knowledge graph: a connected map of what the software does and how its components relate. Engineers can use that understanding to explain the system, improve its design, plan modernization and generate revised code from reviewed specifications. The offering is described as language-spanning; the actual languages, frameworks and repository size must be checked in an owner-led pilot. The code is private, and we can coordinate access or an approved handoff. This product description does not change the historical testing status.',
    does: [
      'Analyzes authorized existing or legacy source code to recover behavior, business rules and specifications.',
      'Connects that understanding in a knowledge graph so engineers can explore components and dependencies.',
      'Uses reviewed specifications to guide code generation, improvements and application modernization.',
      'Keeps engineers responsible for checking the recovered understanding and testing generated changes.',
    ],
    benefits: [
      'Engineers can understand an inherited application without starting every investigation by reading the entire codebase.',
      'Specifications and connected knowledge provide a shared baseline for handover, design discussions and change planning.',
      'Modernization can start from reviewed behavior and requirements, not just a line-by-line code translation.',
    ],
    chooseIf: [
      'You own a system whose documented behaviour has drifted from its code.',
      'You want to carry recovered system knowledge into improved code or a modernization effort, with engineers reviewing both directions.',
    ],
    insteadIf: [
      'You want Informix SQL-to-T-SQL conversion drafts rather than specifications: assess Modernize only with a maintenance owner or approved replacement; it is not arbitrary code migration.',
      'You need a public self-service download or guaranteed coverage of every language: arrange private access and confirm supported inputs with the owner first.',
    ],
  },
  4: {
    brief: {
      what: 'A research workbench for finding and comparing evidence across a large collection of documents, including information in pictures and scanned pages.',
      does: 'You upload documents; it extracts searchable text, topics and named entities. Filter the collection, select relevant files, then ask questions across that specific set or compare their contents.',
      value: 'Investigate differences, recurring requirements or conflicting statements instead of reading every file end to end. Use it for a specialist gap, with an accountable maintenance owner.',
      example: 'Select three versions of a procedure and ask what changed in the approval requirements, then check the cited material against the originals.',
    },
    form: 'A specialist document-search and comparison application whose upstream is no longer maintained. A named maintenance owner or approved replacement is required before a new deployment.',
    what: 'A research workbench for a body of documents. It reads the text and the pictures in your files, pulls out topics, names and other details you can filter by, and lets you ask questions across everything, across a chosen subset, or of one document at a time. Start with Enterprise Knowledge for general knowledge work; assess this specialist option only for a remaining gap, without building duplicate stacks.',
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
      'A CWYD-first pilot leaves a specific need for collection filtering, selected-document comparison or image-heavy evidence.',
      'A named owner will maintain the selected implementation, or an approved replacement meets that specialist need.',
    ],
    insteadIf: [
      'You mainly need answers from an owned policy collection: start with Enterprise Knowledge rather than a second knowledge stack.',
      'Nobody can own maintenance: choose an approved maintained alternative instead of deploying this unsupported upstream.',
      'You need identical fields extracted from every document: see Content Processing.',
    ],
  },
  5: {
    brief: {
      what: 'A way to use an organization-chosen AI model inside supported developer tools, such as Visual Studio Code or GitHub Copilot. It is configuration, not a new application.',
      does: 'Add an approved model connection so supported coding requests go to that model. Local developer setup and centrally managed enterprise setup have different authentication, licensing and feature coverage.',
      value: 'Let developers keep their familiar editor while the organization evaluates model choice, governance and billing. Confirm the supported route before assuming requests can consume existing PTUs.',
      example: 'Pilot a custom model on explaining a function and drafting its tests, comparing answer quality and available features with the default model.',
    },
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
    brief: {
      what: 'An intake application for work that arrives as a pack of related documents. Its built-in example processes insurance claims; another process needs its own fields and rules.',
      does: 'Reads each file, extracts fields into a structured record, evaluates the results and summarizes the whole pack with missing-information findings for a reviewer.',
      value: 'Prepare consistent records and identify incomplete submissions before someone starts a detailed review. The complete processing path still needs evaluation; this does not approve a claim or request.',
      example: 'Submit a sample claim pack with one required document missing and inspect the completeness report and extracted fields before handing it to a reviewer.',
    },
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
      'You want document answers rather than structured intake: start with Enterprise Knowledge; assess Document Knowledge Mining only for an unmet specialist gap and with maintenance ownership.',
      'You are assessing bids or contracts against a rubric: see RFP & contract review, which is a proposed workflow only.',
    ],
  },
  7: {
    brief: {
      what: 'A customer-facing website assistant, supplied as example storefronts with an embeddable chat widget. The examples use sample product and policy information, not live customer systems.',
      does: 'A visitor types a question; the application routes it to a product or policy specialist and drafts a response using the configured material. An optional voice path is included.',
      value: 'Prototype help with product selection and service-policy questions inside a website. Its grounded-answer test failed here, so repair and reevaluate it before exposing it to customers.',
      example: 'Ask whether a sample product fits a stated need and what its return policy says, then verify both answers against the supplied catalog and policy.',
    },
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
    brief: {
      what: 'An analysis workspace for understanding patterns across many support conversations, chats or transcripts, rather than using AI to answer a live customer.',
      does: 'Load permitted conversation records, ask questions about recurring themes and explore dashboards. It combines relevant conversation excerpts with database calculations so a count can be checked against examples.',
      value: 'Help service teams investigate repeated complaints, common questions and process gaps. The evaluated output had meaning-level defects, so findings need validation rather than automatic acceptance.',
      example: 'Ask which delivery problems appear most often in a sample set of support chats, then inspect the matching conversations behind each reported theme.',
    },
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
      'Your source material is documents rather than conversations: start with Enterprise Knowledge; consider Document Knowledge Mining only for a specialist gap with a maintenance owner or approved replacement.',
      'You need this dependable now: the tested output had meaning-level defects that need repair first.',
    ],
  },
  9: {
    brief: {
      what: 'A conversion assistant for moving database code from Informix SQL to the SQL Server dialect, T-SQL. It is not a general-purpose application or programming-language migration tool.',
      does: 'Upload a batch of SQL. The application drafts conversions, checks the generated syntax with a parser, reviews meaning, attempts repairs and exports the results with a processing summary.',
      value: 'Give database engineers a reviewable first pass instead of translating every script by hand. Behavioral testing and a maintenance owner are required; upstream is no longer maintained.',
      example: 'Convert a small set of reporting queries, run the originals and drafts against equivalent test data, and compare the results before accepting the changes.',
    },
    form: 'A SQL-dialect conversion application whose upstream is no longer maintained. A named maintenance owner or approved replacement is required before a new deployment.',
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
      'A named owner will maintain the implementation and your engineers will test the output against the target database themselves.',
    ],
    insteadIf: [
      'Your dialect is not Informix, or the job is SAS or whole-application migration: this package does not establish those.',
      'You need ongoing upstream maintenance: select an approved maintained SQL-conversion alternative rather than assuming this package is supported.',
      'You want a system described rather than its code converted: see SpecSuite, subject to its open questions.',
    ],
  },
  10: {
    brief: {
      what: 'A map-based assistant for exploring satellite imagery and environmental change. It puts a conversation beside the geographic evidence, rather than answering from ordinary business documents.',
      does: 'Ask about a place and time period. The application searches public geospatial datasets, loads relevant imagery as map layers and helps interpret what those scenes show.',
      value: 'Help research teams find imagery for questions about vegetation, surface water or changes over time. A domain specialist still needs to check the data and interpretation.',
      example: 'Choose a region and two time periods, find relevant surface-water imagery, then inspect the scenes to investigate whether visible water coverage changed.',
    },
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
    brief: {
      what: 'A service integration that adds live, spoken conversation to an application. It supplies the speech interaction; your team still builds the business workflow and interface.',
      does: 'Streams microphone audio, handles pauses and interruptions, and speaks the reply from a model. The documented bring-your-own-model route can connect to a compatible deployment your organization controls.',
      value: 'Offer spoken access when typing is inconvenient or inaccessible. Speech charges are separate, and this catalog has not tested the complete voice or customer-PTU integration.',
      example: 'Prototype a voice interface to an approved help workflow: ask a question aloud, interrupt to clarify it, and assess the reply and response delay.',
    },
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
    brief: {
      what: 'A proposed assistant for reviewing requests for proposals, supplier responses and contracts against criteria your team defines. It is not yet an implemented local procurement application.',
      does: 'The intended workflow takes a document pack and review rubric, locates relevant passages, compares them with the requirements and presents evidence-linked findings or missing information.',
      value: 'Give reviewers an organized starting point for consistent assessment instead of a cold read of every page. People retain all procurement, legal and approval decisions.',
      example: 'For a sample bid, locate the evidence for each required deliverable and flag unanswered criteria for the reviewer to investigate—not to make an award automatically.',
    },
    form: 'A proposed local workflow, not an implemented application. Upstream MACAE scenario packs provide implementation references, not a verified local deployment.',
    what: 'A design for helping reviewers work through bids, proposals or contracts: locating the relevant passages, checking them against criteria agreed in advance, and showing the reviewer the evidence behind each finding. The multi-agent orchestration accelerator has upstream RFP evaluation and contract-compliance packs to study, but this local workflow remains unimplemented and not functionally demonstrated. Those packs do not fix the recorded final-synthesis failure. Human reviewers keep every procurement and legal decision.',
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
      'Your reviewers stay the decision-makers, and an implementation owner can repair and evaluate the complete workflow before use.',
    ],
    insteadIf: [
      'You need a proven procurement application now: the upstream references do not establish one here.',
      'Your documents arrive as structured intake packs: assess Content Processing, whose full happy path still needs work.',
    ],
  },
  13: {
    brief: {
      what: 'An internal drafting workspace for marketing campaigns, not official correspondence or policy briefings. A marketer starts with a creative brief instead of a blank prompt.',
      does: 'Provide the audience, message, tone and call to action. Specialist assistants research product material, draft copy and images, then return feedback against configured brand guidelines.',
      value: 'Explore campaign variations and give editors material to refine. Brand feedback is not factual or legal clearance, and the catalog established compilation—not a complete working campaign process.',
      example: 'Draft two campaign concepts for a sample product launch with different audiences, then have an editor compare the wording, images and brand feedback.',
    },
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
      'You need official correspondence or briefing drafts: that is an unbuilt use-case idea, not this package.',
      'You need factual or legal clearance: brand feedback is neither.',
    ],
  },
  14: {
    brief: {
      what: 'A set of infrastructure templates for the cloud environment behind an AI application. It gives platform engineers a starting design, not a chatbot or staff-facing tool.',
      does: 'Engineers review configuration for hosting, identity, networking, monitoring, AI and search services, plus optional data and governance integrations, before provisioning an approved environment.',
      value: 'Make platform decisions explicit and reusable when onboarding AI workloads. Prefer an existing approved foundation; this upstream is unmaintained and needs a maintenance owner or replacement.',
      example: 'Before hosting a document assistant, compare its service requirements with the template and your existing environment, then identify which approved components can be reused.',
    },
    form: 'Infrastructure reference templates for engineers, not a business application. Upstream is no longer maintained; new deployment requires a named maintenance owner or approved replacement.',
    what: 'A reference for the groundwork an AI application needs: network, identity, monitoring, AI and search services, expressed as configuration your platform team can read and challenge. Prefer the existing approved tenant foundation. This package is neither a turnkey production platform nor proof of production readiness, and a new deployment needs someone explicitly accountable for maintenance or an approved replacement.',
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
      'Your platform team needs an infrastructure reference to compare with the approved tenant foundation.',
      'Any new deployment has a named maintenance owner or approved replacement and separate application acceptance checks.',
    ],
    insteadIf: [
      'You are looking for something staff can use: this has no end-user experience at all.',
      'Your tenant already has an approved landing-zone pattern: reuse it instead of duplicating services.',
      'You need a supported turnkey production platform: choose an approved maintained foundation, not this reference alone.',
    ],
  },
  15: {
    brief: {
      what: 'A toolkit for the people who build employee-help assistants in Microsoft Copilot Studio. Installing the kit does not itself create or license a working staff chatbot.',
      does: 'Makers prepare answer topics and templates, configure approved HR or IT connections, test employee journeys with evaluation material and synchronize approved changes through the platform.',
      value: 'Maintain employee-service answers through a repeatable build-and-test process rather than editing them directly in front of staff. Platform permissions, licensing and model billing are separate decisions.',
      example: 'Build a password-help topic, test whether it gives the approved instructions for common employee questions, then publish the reviewed change to the employee agent.',
    },
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
    brief: {
      what: 'A web application for asking questions about records already held in Microsoft Fabric, the data and analytics platform. It works with business data, not a folder of documents.',
      does: 'A signed-in user asks a question in ordinary language. The application works with a Fabric Data Agent to query the configured data and return an answer with data context.',
      value: 'Let business teams explore sales, product or other governed records without writing each query themselves. Permissions and answer accuracy need testing; not all reasoning runs on customer PTUs.',
      example: 'Using the sample retail data, ask which products sold most in a period and compare the answer with a known database query.',
    },
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
    brief: {
      what: 'A Microsoft Fabric starting point for watching operational activity as it happens, using live dashboards, alert rules and a data-questioning assistant.',
      does: 'Streams sensor or equipment readings into a real-time data store, displays the readings, sends configured notifications when thresholds are crossed and supports questions about the history.',
      value: 'Help operations teams spot unusual patterns and investigate them instead of waiting for a periodic report. It includes a simulator; production monitoring and model routing still need validation.',
      example: 'Run simulated factory readings, configure a temperature threshold and inspect an alert alongside the recent readings to understand what triggered it.',
    },
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
  19: {
    brief: {
      what: 'A small developer application that generates descriptions of a video by examining selected still images. It is not continuous video monitoring or an audio-transcription service.',
      does: 'Upload a permitted clip, choose how many frames to sample and enter a question. The app extracts those frames and returns a model-generated description, frame counts and a representative image.',
      value: 'Evaluate whether rough visual summaries are useful for a narrow review task. Sampling can miss brief events, so the generated description must be checked against the full video.',
      example: 'Describe a short sample equipment-demonstration clip at two sampling rates, then compare what each summary captures or misses while watching the original.',
    },
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
  21: {
    brief: {
      what: 'An engineering codebase for building assistants that speak with callers over a telephone or browser. It includes call and audio handling, unlike a speech service alone.',
      does: 'Connects the call, streams speech, coordinates tools and conversation, handles interruptions and provides a route to hand off to a person. Your team supplies the business logic.',
      value: 'Build a bounded spoken service journey without starting the real-time communication infrastructure from scratch. Telephony, speech and hosting have separate costs and require operational ownership.',
      example: 'Prototype a caller asking a routine service question, then requesting a human; evaluate the spoken answer, interruption behavior and transfer in an approved test environment.',
    },
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
    brief: {
      what: 'A guided training workshop on securing the connections between AI assistants and their tools or data, using Model Context Protocol (MCP). It is learning material, not a business app.',
      does: 'Engineers work through progressive exercises: inspect an intentionally insecure example, observe the weakness, apply an identity, gateway or safety control, then check that the control blocks the problem.',
      value: 'Build practical skills for reviewing agent integrations before rollout. Exercises must stay in disposable, isolated environments with no production connectivity; they are not a PTU-utilization workload.',
      example: 'In an isolated lab, compare a tool connection before and after an access control is applied, then document what changed and how it was verified.',
    },
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
