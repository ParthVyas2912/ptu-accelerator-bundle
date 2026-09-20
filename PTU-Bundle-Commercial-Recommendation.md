# What should actually go into the PTU solution bundle?

**Decision brief for DND and strategic accounts | 12 September 2026**

**Basis:** the original M365 Researcher response, both MCAPS evaluation reports, selected underlying evidence, and Microsoft/GitHub documentation. This is a commercial recommendation, not a new deployment, capacity test, customer reference validation, or production certification. Readiness below refers to the recorded lab results, not a fresh health check.

## Addendum - 20 September 2026: maintenance gates and a focused pilot

**This addendum supersedes earlier maintenance and default-inclusion assumptions, not the dated historical evidence below.** The September 12 brief and its recorded results remain intact. Later public-source review is not functional testing, deployment proof, a repair of failed synthesis or a change to the established package architecture revisions. The later pins cited here are separate review references.

**Start with a focused CWYD-first knowledge pilot, not the full catalog as a deployment promise.** Use one approved collection, an accountable content/operating owner, citation and access checks, and explicit acceptance criteria. Selected earlier passes do not establish a production service. Add capabilities only for a demonstrated gap and avoid duplicate knowledge, retrieval and hosting stacks.

| Candidate or reference | Current recommendation and gate |
|---|---|
| CWYD | First pilot candidate, subject to permissions, useful answers, actual approved model routing and operational acceptance. Reusing a Foundry project is not evidence of reusing PTUs. |
| Content Processing | Remains **partial**: the recorded missing-document scenario passed with its warning, but the full happy path did not. Repair and evaluate complete and incomplete packs before expanding document operations. |
| MACAE RFP / contract review | Use the actual upstream [RFP evaluation pack](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator/tree/e89689e475eecf23ef2b48ad9e556bde16776e8d/content_packs/rfp_evaluation) and [contract-compliance pack](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator/tree/e89689e475eecf23ef2b48ad9e556bde16776e8d/content_packs/contract_compliance) as implementation references. The local procurement workflow is still proposed/not implemented, and final-synthesis remediation plus end-to-end evaluation remain required. Pack availability is not a successful deployment or a fix. Review upstream usage/support terms; human reviewers retain procurement, award and legal decisions. |
| Document Knowledge Mining | Its [later pinned README](https://github.com/microsoft/Document-Knowledge-Mining-Solution-Accelerator/blob/1d9b68967d540c972357dd08286e08fcaf8bcc39/README.md) says it is **no longer maintained**. Preserve its specialist multimodal discovery, filters and document-comparison potential, but only as an owner-maintained option for a gap left by CWYD, or replace it. Require a named maintenance owner or approved replacement before new deployment; do not start a duplicate knowledge stack by default. |
| Modernize Your Code | Its [later pinned README](https://github.com/microsoft/Modernize-your-code-solution-accelerator/blob/f5d25c1f8bbe391b13c43ad5a8f7ea835aef1e7a/README.md) says it is **no longer maintained**. Treat it as owner-maintained SQL-dialect conversion, with Informix SQL to T-SQL in the shipped experience, not arbitrary programming-language or whole-application migration. Require a named maintenance owner or approved replacement before new deployment and independent target-engine execution checks. |
| AI application deployment foundation | Its [later pinned README](https://github.com/microsoft/deploy-your-ai-application-in-production/blob/4fa38951a36484fb95a54f9e396f05b94a2b7f4c/README.md) says it is **no longer maintained**. It is an infrastructure reference, not turnkey production. Prefer an existing approved tenant foundation; new deployment requires a named maintenance owner or approved replacement and separate application acceptance. |

The reviewed **no-longer-maintained** set also includes **Container Migration** and **Data Governance**. These are reviewed external references, not additional applications in this bundle, not new deployments and not an expansion of the offer.

**Model-routing gate:** current source review found that existing-Foundry-project paths in CWYD, Content Processing and MACAE can still deploy `GlobalStandard` models. Review model-deployment resources and persisted agent model selections for the chosen application; verify the actual approved endpoint, model, API and geography rather than assuming project reuse means PTU reuse. Apply the same check if the proposed procurement workflow selects MACAE, without assuming every application uses the same implementation. Separately billed extraction, search, storage, hosting and other services remain outside any model-capacity claim.

**Catalog scope:** reuse useful scenarios from the legacy catalog as patterns within selected workflows; do not turn that catalog into a promise of 39 deployable apps. **Microsoft IQ** is a conditional future supply-chain assessment, only if a sponsor, concrete problem, authoritative package, prerequisites, support and model-routing basis are established. It is not a default addition to the pilot or a presumed PTU workload.

## 1. My honest answer

**The original business hypothesis is good. The twenty-item catalog is too broad to be the offer.**

Customers do not need twenty accelerators. They need a small set of applications their people will repeatedly use, an accountable implementation team, and predictable operation at the required scale.

I would launch **three outcome bundles**, supported by one governed model platform:

1. **Enterprise Knowledge and Staff Work:** trusted answers, document comparison, and source-backed briefing/policy drafts.
2. **Procurement and Document Operations:** evidence-backed contract/RFP review, document intake, and missing-evidence checks.
3. **Engineering Modernization:** code understanding, specifications, and verified modernization; add customer-endpoint developer assistance only where the chosen client supports it.

Use the existing Chat With Your Data, Document Knowledge Mining, Content Processing and Modernize Your Code work as building blocks. Include SpecSuite conditionally on its owner and delivery/support agreement. Develop contract review and controlled drafting into actual customer workflows rather than selling generic multi-agent orchestration.

**The most important missing application is a controlled, source-backed briefing and document-drafting workbench—not another generic chatbot.**

Keep service operations and geospatial support as account-specific expansions. Do not count the native managed-model consumption of Voice Live, Copilot Studio, Security Copilot or Fabric as customer Azure OpenAI PTU consumption. **Importantly, Voice Live now documents a BYOM route that explicitly supports customer PTUs.** That is a credible follow-on integration to validate, not the route we tested. Studio and Fabric also document separately billed customer-model paths. An unverified internal project still does not belong in a promised deployment package.

**Sales message:** “We help you deploy useful enterprise applications, then provide the model capacity their proven production demand requires.” Not: “Buy PTUs and get twenty production-ready apps.”

### What I would put in front of a customer today

- **Guided demonstrations:** the selected CWYD, DKM and Modernize workflows that passed, with their limitations disclosed.
- **Existing SpecSuite/Planetary demonstrations:** only through their owners; our exercise did not retest them.
- **A solution-design and implementation offer:** named outcomes, delivery scope, acceptance tests and operating ownership.
- **Not a turnkey production bundle.** The lab contains hosting adaptations, paused/disarmed services, incomplete browser journeys and unresolved business-workflow failures. Deployment assets exist; “all apps are ready for customer use” is not supported.

## 2. What the exercise tells us—and what I would correct

The original researcher was directionally right about knowledge, engineering and document work. Its numerical rankings and “High” PTU labels were hypotheses, not commercial proof.

I would also narrow several statements in the continuation report:

| Earlier implication | More defensible interpretation |
|---|---|
| No PTUs in the MCAPS lab is the principal negative finding. | **It is a measurement boundary, not a failure of the strategy.** The lab intentionally used Standard capacity. It tested selected functionality, not the economic benefit of a customer's provisioned deployment. |
| Token-heavy or multi-agent means a strong PTU driver. | Only if the work is useful, production demand is material, and provisioned capacity beats the relevant alternatives or satisfies a justified performance requirement. More agents can mean avoidable cost and failure points. |
| A 71.8% prompt-cache rate implies a general 3–4× PTU sizing correction. | That rate is from StepFly's twenty-call sample. It is not a portfolio-wide factor. Model-specific output weighting, cache treatment, peak demand, minimum deployment size and headroom still matter. |
| Four Voice Live sessions prove conversational voice performance. | They were **text-mode component probes**. They do not establish speech recognition quality, audio latency, interruption handling, telephony or full contact-centre readiness. Connection time included credential acquisition, but its exact contribution was not isolated. |
| Voice Live cannot consume customer Azure OpenAI PTUs. | **This was too categorical.** Microsoft's current BYOM documentation explicitly lists “Use your PTU (Provisioned Throughput Units) deployments.” Our managed-model probes did not test that integration. Speech costs and the combined billing treatment still need verification. [P5] |
| “Document generation no longer exists.” | The **specific referenced repository** now describes marketing content generation. That does not invalidate the business-document use case or establish that no other offering exists. |
| A template containing Fabric means Fabric is mandatory for every deployment. | Fabric is a gate for enabled Fabric paths. The inspected platform documentation also describes disabling Fabric/Purview. A conditional template declaration is not a mandatory dependency. |
| An app is either inherently PTU-dependent or cannot use PTUs. | Check its actual inference path. Standard often works too; custom extensions can introduce customer-managed inference. A product's native billing and a custom Azure OpenAI extension are separate things. |

The source-backed lesson is **“select and harden the valuable workflows,” not “the whole portfolio is bad.”** An accelerator defect is a delivery risk, not proof that the underlying customer problem lacks value.

## 3. Two different commercial motions

### A. Customer has not purchased PTUs

The burden of proof is higher. Establish:

- A buyer, a valuable recurring task and representative adoption—not just a large employee count.
- Correct application outcomes and a production latency/throughput objective.
- Measured per-model demand, including calls per task, input/output lengths, caching and retries.
- A fair comparison with Standard and, for delay-tolerant processing, Batch.
- Compatible model/version, geography, API, deployment availability and contractual scope.

**Do not force PTUs into a low-volume pilot.** A valuable application can remain on Standard indefinitely and still be a successful customer outcome.

For perspective, the researcher's cited **8,000 monthly queries**—not independently verified here—would average only **0.76 user queries/minute** over 22 eight-hour working days. That could still hide expensive multi-call tasks or sharp peaks, but the headline volume alone does not justify a large provisioned deployment.

### B. Customer already has PTUs

This bundle can be useful immediately as an **adoption and renewal program**:

1. Inventory the actual provisioned deployments, existing workloads, expiry/renewal position and available headroom.
2. Select applications whose model, API, quality needs and approved geography match those deployments.
3. Connect through the customer's approved identity/network path and verify actual provider routing.
4. Prioritize interactive users; admit useful background work only within measured headroom and its own time/cost budget.
5. Track successful business tasks and incremental costs—not just utilization.

For a deployment that stays allocated regardless, an additional compatible request within headroom generally does not add another PTU-hour charge. **It does not make the entire application free:** hosting, search, OCR, speech, storage, other model deployments, spillover and implementation remain chargeable.

Using spare capacity can improve renewal confidence without producing an immediate expansion sale. **New PTU sales occur when additional valuable, adopted workloads justify additional capacity.** Filling idle capacity and selling more capacity are different stages.

Do not retain an oversized commitment indefinitely merely to avoid acknowledging underuse. At renewal, compare rightsizing with real forecast demand.

### What PTUs improve—and do not improve

Provisioned capacity can make model-serving throughput and latency more predictable under the validated load and provide attractive economics at suitable utilization. It does **not** make the same model inherently more accurate, give it new business features, guarantee end-to-end application latency, repair broken retrieval, or confer a security accreditation.

There is no universally interchangeable “PTU bucket.” Multiple applications may share a **compatible deployed model endpoint**. Different model deployments and different residency/trust boundaries need separate capacity decisions. Reservation discount scope is not the same as runtime pooling.

Microsoft's current billing guidance distinguishes a **reservation** from a **deployment**: reservations provide matching financial coverage, not a guarantee of deployable capacity. Matching is not by model/deployment ID; it follows the documented deployment type, scope, quantity and geographic rules. Establish deployment availability before purchasing matching coverage. Neither a reservation's financial utilization nor its coverage of several deployments proves those applications share one runtime capacity pool. [P1–P2]

## 4. Verdict on all twenty original candidates

**“Existing PTU usefulness” assumes compatible routing, acceptable quality and spare capacity.** High is a commercial judgment, not measured production readiness. The order below follows the original catalog so no candidate disappears from the assessment.

| # | Candidate | Usefulness to an existing PTU customer | Honest sales and readiness verdict |
|---|---|---|---|
| 1 | **Enterprise Knowledge Assistant / CWYD** | **High.** Repeated, cited answers over approved manuals, policy and knowledge. | **Core anchor.** Selected 8/8 criteria passed in an adapted local runtime. Strong broad adoption potential, but demonstrate a gap beyond existing Microsoft 365/search capabilities. Hosted production, permissions and scale still need validation. |
| 2 | **Generic multi-agent automation / MACAE** | **Conditional.** Valuable if it completes a real approved workflow. | **Implementation engine, not a flagship SKU.** Planning and specialists ran; final synthesis did not pass. Sell procurement or service outcomes, not “more agents consume more PTUs.” |
| 3 | **SpecSuite** | **High potential.** Repository understanding, specifications and code generation. | **Engineering anchor, conditional.** Strong problem/solution fit. Existing app was protected and inventory-only. Historical DND PTU evidence comes from the supplied research, not this lab. Obtain named owner, licensing, support and a repeatable quality demonstration. |
| 4 | **Document Knowledge Mining** | **High.** Document comparison, evidence lookup and cited synthesis. | **Core anchor, combined with CWYD rather than a second generic chat product.** Selected ingestion/QA/comparison passed; only 2/10 fixtures and no full browser journey. OCR/search/embeddings are separate costs. |
| 5 | **GitHub Copilot / VS Code BYOK** | **Potentially high for supported customer-endpoint interactions.** | **Controlled engineering add-on.** Not configured in this lab. Current VS Code local BYOK and enterprise Copilot BYOK have different licensing, policies and routing; see §7. Do not claim all Copilot features consume the customer's PTUs. |
| 6 | **Content Processing** | **High with useful compatible work waiting; medium as a new purchase driver.** | **Core document-operations building block.** Native missing-document scenario passed with a provider-filter warning; full happy path did not. Continuous time-sensitive intake may justify PTUs; overnight backlogs may be better on Batch. |
| 7 | **Customer/constituent chatbot** | **High potential at actual service scale.** | **Service expansion after repair.** Product API and routing worked; the grounded chat answer was a generic refusal. Strong customer value is plausible, but do not put that current journey in a ready-to-run demo. |
| 8 | **Conversation Knowledge Mining** | **Medium.** Summaries and follow-up work over approved transcripts. | **Later service add-on.** KPI, prose and context failures remain. Post-call analysis is often delay-tolerant; evaluate Batch. Speech/transcription do not automatically use chat PTUs. |
| 9 | **Modernize Your Code** | **High during an active modernization program.** | **Engineering bundle component.** Selected upload/process/download passed, not full source/target database equivalence. Strong project value; weaker perpetual-capacity case if demand ends with a migration. Require execution-based acceptance. |
| 10 | **Planetary Explorer** | **Medium, specialist-dependent.** Language reasoning and explanations can use inference. | **Account-specific extension.** Existing deployments were inventoried, not retested. Geospatial compute and data access are not PTU usage. Include for an identified infrastructure/environmental analyst community, not a generic consumption forecast. |
| 11 | **Call Center Voice Live** | **Low on the tested managed path; potentially high through documented PTU BYOM at service scale.** | **Conditional service-bundle expansion—not an exclusion.** Microsoft explicitly documents customer PTU use through BYOM. The lab proved only text-mode managed-model connectivity. Validate the accelerator's BYOM configuration, end-to-end audio quality/latency, model compatibility and full billing before selling it as PTU-backed. [P5] |
| 12 | **Contract/RFP compliance reviewer** | **High potential.** Repeated comparison, evidence matrices and reviewer assistance. | **Priority build for the procurement bundle.** Packs were inspected, not functionally demonstrated. The underlying use case is stronger than the current package. Human reviewers retain decisions; no autonomous award or legal judgment. |
| 13 | **“Document Generation” / current marketing-content repo** | **Low DND priority; possible commercial marketing fit.** | **Do not use this repo as evidence of controlled business-document generation.** Only infrastructure compilation was verified. Build the source-backed drafting workflow in §6; do not count image-generation charges as chat PTU consumption. |
| 14 | **Private-tenant AI platform baseline** | **High enablement value, not standalone task demand.** | **Shared foundation, not a separate business app.** Template compiled; no app outcome was proven. Reuse an approved customer platform rather than duplicating expensive services or enabling optional Fabric by default. |
| 15 | **Employee Self-Service** | **Medium if the custom app calls the customer's model.** | **Knowledge/service scenario, not automatically another product.** MACAE HR was not functionally completed. The separate ESS developer kit is a Copilot Studio path with different prerequisites/billing. Avoid rebuilding licensed employee-service capabilities without a clear gap. |
| 16 | **Unified Data Foundation agents** | **Conditional/unknown until actual model routing is established.** | **Data-platform extension, not launch core.** Fabric prerequisites blocked evaluation. Sell it where governed data and a business sponsor already exist; purchasing Fabric capacity is not purchasing PTUs. |
| 17 | **Real-Time Operations Intelligence** | **Conditional.** Interactive explanations/investigations can generate model demand. | **Later operations extension.** Not validated. Telemetry ingestion volume is not LLM volume. Use deterministic analytics for metrics; call models for tasks that benefit from them. |
| 18 | **Incident/Troubleshooting / StepFly** | **Medium potential for the problem; low readiness for this implementation.** | **Do not ship the research prototype as the incident product.** It rejected decoys but never reached the planted root cause within the budget. Build a bounded runbook/ticket workflow instead. |
| 19 | **Video/media analysis** | **Low–medium, narrowly scoped.** Sampled visual reasoning can use a supported model. | **Specialist pilot only.** Six tests included four successful model cases, one provider safety rejection and one decode failure with no call: five provider attempts, not six. No continuous-video SLA or operational readiness was established. |
| 20 | **Harbinger** | **Unknown.** | **Hold outside the commercial offer.** No validated package, owner, support model or model-routing evidence. A name in an internal opportunity list is not a deployable solution. |

### My commercial priority order

1. **Knowledge and document intelligence:** strongest cross-account anchor; combine overlapping capabilities.
2. **Procurement/evidence review and controlled drafting:** strongest next customer workflows to build, especially for DND/public-sector administration.
3. **Engineering modernization:** compelling where an engineering sponsor and sustained program exist.
4. **Service operations:** credible expansion after current defects are resolved; Voice Live BYOM is a concrete PTU integration opportunity to test for high-volume service accounts.
5. **Geospatial, Fabric and media:** specialist account plays, not default capacity assumptions.

High business value does not automatically equal high **incremental PTU-sales value**. A small expert team may save substantial effort while generating too little sustained traffic to justify a new allocation.

## 5. The bundle I would actually package

This is a proposed field/partner delivery offer, **not an existing Microsoft commercial SKU or support commitment**.

| Bundle | Customer buys an outcome | Included solution components | Why capacity could be justified | Acceptance before production |
|---|---|---|---|---|
| **Knowledge and Staff Work** | Less time finding, comparing and turning authoritative information into usable work. Buyers: CIO, knowledge/policy and program leaders. | One permission-aware knowledge workbench; CWYD/DKM capabilities; controlled briefing/policy drafting; bilingual review where required. | Repeated interactive retrieval and synthesis across several adopted departments. | Correct citations, no-answer behavior, document/version and permission boundaries, task completion, measured latency at target concurrency. |
| **Procurement and Document Operations** | Faster evidence preparation and exception review. Buyers: procurement, records, finance and program authorities. | Intake/extraction; schema mapping; contract/RFP evidence matrices; missing-document and obligation checks; explicit approval. | Regular document flows plus interactive analyst review and deadline-sensitive synthesis. | Accuracy on material fields, traceable evidence for each finding, false-positive/negative review, safe handling of incomplete inputs. No autonomous awards. |
| **Engineering Modernization** | Better understanding and controlled change of legacy systems. Buyers: CTO, app owners and engineering platform leads. | SpecSuite if owner-approved; Modernize Your Code; requirements/change-impact analysis; optional supported BYOK cohort. | Repeated repository analysis and code/specification generation across an active program, not just a one-off demo. | Source/target execution tests, interface preservation, reviewable changes, test coverage and no unsanctioned changes to production. |

**One shared foundation:** approved identity and network access, model routing, per-application attribution, workload priorities, queues/admission control, evaluations, operational monitoring and cost reporting. Start with existing customer services where practical. A giant new landing zone is not a prerequisite for every small application.

Do not assume all three bundles use one model. Validate a small number of model-specific capacity groups. Use deterministic code and cheaper appropriate models where they achieve the required quality.

**Do not launch a separate Security/SOC or Mission Planning bundle just to complete a catalog.** Security Copilot has its own capacity/commercial model, and bespoke security workflows need their own ownership and validation. For DND, start with approved administrative, engineering and information-support tasks; do not infer authorization for operational military decision-making from a successful lab demo.

## 6. What more applications should be included?

I would add **five targeted workflows**, in this order. These are proposed implementations/extensions, not five newly discovered supported Microsoft products, and none was deployed in this exercise.

### 1. Controlled briefing, correspondence and policy-drafting workbench

**Highest-priority addition.**

- **Buyer/value:** program, policy and executive-support leaders need a source-backed first draft they can review—not a blank chatbot.
- **Workflow:** choose approved sources and a template; produce a briefing note, options summary or correspondence draft; show citations, uncertainties and a comparison against the previous version; require human approval.
- **Why this is better than another RAG demo:** it delivers a work product and fits an existing approval process. It also creates a reason to return daily.
- **PTU potential:** **High if adopted broadly**; low-volume users alone do not justify capacity. Interactive drafting and revisions produce meaningful model work.
- **Build approach:** extend the selected knowledge workbench with templates, versioned sources, evaluations and controlled export. Do not rebrand the marketing-content accelerator.
- **Proof/KPI:** accepted drafts, reviewer effort, factual corrections and time to an approved artifact—not token volume.

### 2. Engineering requirements and change-impact reviewer

- **Buyer/value:** engineering assurance, application and infrastructure teams need to understand what a changed requirement affects.
- **Workflow:** connect requirements, design/specification records, source modules and tests; draft an evidence-linked impact matrix and identify unsupported links.
- **PTU potential:** **High in a recurring engineering program**; not inherently high for a one-time import.
- **Build approach:** an owner-approved SpecSuite extension plus document/code retrieval. GraphRAG is an optional research-backed technique for connected evidence—not the default when ordinary retrieval suffices. Index-building is a separate workload with separate economics.
- **Proof/KPI:** verified affected items found, missed dependencies, reviewer acceptance and change-review lead time.

### 3. Bilingual policy comparison and drafting assistant

- **Buyer/value:** Canadian policy, communications and service teams need terminology-consistent English/French work and visibility into substantive differences.
- **Workflow:** compare versions, find missing obligations or inconsistent terms, propose edits against approved terminology, and route to qualified review.
- **PTU potential:** **Medium; high only at substantial adoption.** The reasoning/review layer can use customer Azure OpenAI. Pure bulk translation should be compared with Azure Translator or other approved services, not forced onto a general LLM.
- **Build approach:** a language-aware workflow in the knowledge/drafting workbench, with a bilingual evaluation set and subject-matter reviewers.
- **Proof/KPI:** material discrepancies detected, terminology adherence, rework and review time. No claim of certified translation.

### 4. Audit and access-to-information evidence workbench

- **Buyer/value:** records, compliance and access-to-information/privacy teams need to locate relevant evidence, build timelines and prepare review packages.
- **Workflow:** scoped retrieval, source-preserving summaries, duplicate identification, chronology and draft evidence bundles.
- **PTU potential:** **Medium as a new-sale driver; useful for existing compatible headroom.** Interactive review is a stronger PTU case than an overnight discovery backlog.
- **Build approach:** extend DKM with permissions, provenance, retention/legal-hold integration and task-specific evaluation. This is **not** a replacement for Microsoft Purview/eDiscovery or a records system.
- **Proof/KPI:** completeness on a reviewed corpus, citation correctness and review effort. Authorized staff make exemption, redaction and release decisions.

### 5. Bounded service-desk investigation and resolution assistant

- **Buyer/value:** service owners want quicker ticket triage, runbook discovery and good escalation handoffs.
- **Workflow:** summarize an authorized ticket, retrieve approved procedures, suggest non-destructive checks, and draft a resolution/escalation record; tools operate within explicit permissions.
- **PTU potential:** **Medium–High if there is sustained service volume.** Small incident teams or rare major incidents may not justify dedicated capacity.
- **Build approach:** retrieval plus a bounded workflow and deterministic tools, optionally using MACAE after its relevant path is fixed. Do not use StepFly's research DAG as the production product.
- **Proof/KPI:** correct runbook selection, resolution/escalation accuracy, analyst time and reopened tickets; no autonomous high-impact changes.

**Packaging discipline:** maintenance-manual assistance is a vertical knowledge pack, not another platform. Procurement evidence review is already in the selected bundle, not a “new” app to inflate the count. One good workbench with several governed workflows is more maintainable than twenty separate chat frontends.

### Additional integration priority: Voice Live on the customer's PTU model

This is an extension of an existing candidate, not a sixth new application. Microsoft's BYOM guide explicitly supports PTU deployments through `byom-azure-openai-chat-completion`. For an account with substantial customer/service-desk voice demand, it could become a stronger capacity driver than several low-volume administrative apps combined. That is a hypothesis to measure, not a claim proved by the four text probes. [P5]

Test one telephony-free, approved audio journey against a compatible customer deployment first. Capture actual model routing, first-audio and end-to-end response latency, interruptions, errors, capacity use and service-specific charges. Establish full speech-plus-model economics and regional support before expanding to telephony. Do not silently assume the stock accelerator already configures the documented BYOM path.

**Implementation reference added 16 September 2026 — ART (Azure Real-Time Agent Accelerator).** `Azure-Samples/art-voice-agent-accelerator`, MIT, pinned at `a2e1ce2e`. This is the concrete code path for the priority above: it supplies telephony, bidirectional media streaming and orchestration, and lets the audio path be switched by configuration between a separated speech pipeline and the managed voice-to-voice service. It is now catalog candidate 21.

It was added by **source review only**. Nothing was deployed, no call was placed and no model request was made, so no latency or quality figure is claimed. The reviewed Terraform provisions materially more than one application — a managed Redis cluster, a document cluster, a container registry, two container-app environments with five apps, two web apps, key vault, configuration, monitoring and communication services — and its checked-in model capacity defaults are roughly five to fifteen times the capacities used elsewhere in this evaluation. Managed Redis alone is **USD 0.23 per hour** at the smallest supported size (public retail rate, Canada Central, checked 16 September 2026), and there is no free option for it. PSTN telephony additionally requires **purchasing a phone number**, which carries rental and per-minute charges.

Consequently ART is recorded as **prerequisite-gated, not deployed**. A demonstration needs its own explicit budget approval and a reduced-capacity configuration; it does not fit inside the closed evaluation allowances. Treat it as the strongest available capacity-driver hypothesis to *test*, not as a proved one.

### Engineering enablement addition: agent tool security

**Sherpa — MCP security workshop.** `Azure-Samples/sherpa`, MIT, pinned at `12be921e`. Catalog candidate 22. This is deliberately **not** another application to sell: it is a staged, hands-on workshop for securing the Model Context Protocol servers through which agents reach tools and data, aligned to a published MCP risk list.

It matters commercially because almost every other candidate in this portfolio ultimately depends on agents calling tools. A customer that adopts multi-agent or tool-calling workloads without that competence acquires risk faster than value. It is a credible, low-cost engagement opener that does not require a capacity conversation.

Two boundaries must be stated plainly. First, it deploys intentionally vulnerable servers together with working exploits, so it must run only in a disposable, isolated environment with no production connectivity — it was **not** deployed here for that reason. Second, it consumes little or no model capacity, so it must never be presented as a PTU driver; its value is risk reduction and engineering credibility.

### Public implementation leads—not more products to sell

- **Microsoft GraphRAG:** configurable Azure model deployments and runnable indexing/query paths make it a candidate for connected evidence and change-impact analysis. Use it only if it improves evaluated outcomes over simpler retrieval. Deferred graph extraction and indexing still need a Batch comparison. [P10]
- **Azure-Samples Adaptive RAG Workbench:** a configured Azure chat service and deployment assets can inform drafting/verification workflows. Its template is marked `0.0.1-beta`, with active-development/breaking-change warnings. It is a research/build reference, not an additional production-ready bundle app. [P9]
- **Content Processing and MACAE:** already in the evaluated portfolio. Reuse their suitable components where tests justify doing so; do not count them again as newly found offerings. [P11–P12]
- **Bilingual drafting:** no dedicated, validated Microsoft accelerator was established in this review. The proposed workflow requires implementation and evaluation; it is not presented as an off-the-shelf product.

### The non-application addition that matters most

Provide a **PTU adoption and capacity-operations layer**:

- Per-app, per-model successful-task and provider-usage attribution.
- Admission control, prioritization and isolated queues to protect interactive users.
- Routing to compatible deployments, with approved and separately metered Standard spillover where supported.
- Outcome-quality evaluations and explicit model/version migration checks.
- Utilization, tail-latency and headroom views; chargeback/showback.
- A reviewed queue of useful background work, not synthetic token generation.

This does not itself create business demand. It makes multi-application adoption governable and gives the account team credible evidence for renewal or expansion.

## 7. Why customers would choose this over products they already own

Do not sell a custom build merely because Microsoft has a public repository.

| Existing capability | When the custom bundle earns its place |
|---|---|
| Microsoft 365 Copilot / SharePoint search | The required corpus, application workflow, evidence schema, integration or control requirement is not met by the licensed solution. Do not promise the custom app is automatically more secure. |
| Copilot Studio employee/service agents | A concrete requirement favors customer-managed inference/application control and the full lifecycle cost is justified. Otherwise use the existing product. |
| GitHub Copilot | Customer-selected endpoint capabilities fill a supported need. BYOK is not justification to replace functioning licensed experiences with something less capable. |
| Purview/eDiscovery | The new workflow augments authorized analysis and drafting; the records/compliance system remains authoritative. |
| Translator, OCR, speech, search and conventional analytics | Use the specialized service or deterministic code for what it does best. Add generative reasoning only where it improves the outcome. |

For some strategic accounts the right answer will be **a product subscription, Standard, or Batch—not PTUs**. Being explicit about that makes the PTU recommendation credible when demand actually warrants it.

### BYOK deserves a precise pilot—not a blanket yes or no

| Route | What current documentation supports | What not to promise |
|---|---|---|
| **VS Code local BYOK** | Customer Azure endpoint and deployment configuration. Current VS Code docs say BYOK models can work without a GitHub sign-in or Copilot plan; Business/Enterprise use is subject to organizational policy. Chat/agent support depends on model capabilities. [P3] | It does not automatically cover inline completion, semantic search or embedding-dependent features. Utility/background models have separate settings. Client-local credentials/routing do not prove the enterprise server-side path works. |
| **Enterprise Copilot BYOK** | Centrally configured Microsoft Foundry custom models, handled server-side through Copilot's API; applicable Business/Enterprise users need a Copilot license. This route is **public preview**. [P4] | No assumption that a private-only Azure endpoint is reachable from that service, that all Copilot features route there, or that all model/API combinations work. Those are customer-specific acceptance tests. |

The documented ability to select an Azure deployment makes a compatible PTU endpoint a legitimate target. Neither documentation nor our lab establishes an end-to-end pass for a particular customer configuration. Do not weaken an identity-only or private-network policy merely to make the demo work.

For adjacent platforms, **Copilot Studio** documents separate billing for BYOM/Foundry configurations, and **Fabric AI Functions** document customer endpoints outside Fabric model-call charges while Fabric compute remains billable. These are integration opportunities—not evidence that the inspected ESS/Fabric accelerators already route to customer PTUs. **Security Copilot SCUs remain a separate capacity construct**; no replacement by customer PTUs was verified here. [P6–P8]

## 8. DND-specific sales and deployment gates

The MCAPS environment is not an approved DND landing zone and does not demonstrate an authority to operate for any data classification.

Before quoting a production deployment:

1. Identify the accountable business owner, approved use, information classification, retention and human-decision boundaries.
2. Verify the selected model/version and deployment type against the required processing geography. A Canadian resource location or a private endpoint does not by itself establish Canadian-only model processing.
3. Validate the actual JDCP network/identity path and hosted-tool egress. The local JDCP guidance requires integration with centrally managed private DNS; do not copy the MCAPS spoke-local DNS topology into DND.
4. Confirm model capacity availability, permissions, licensing and any required consents with the appropriate owners.
5. Name the implementation and post-go-live support teams. Microsoft-authored accelerator code is not, by itself, a Microsoft product-support commitment.
6. Complete bilingual, privacy, accessibility and task-quality acceptance appropriate to the application. Begin with approved synthetic/unclassified material.

These are delivery gates—not arguments that PTUs themselves supply sovereignty, privacy or accreditation.

## 9. How I would run the sales motion

### First: sell a qualified outcome, not a capacity number

For each strategic account, select **one broad daily workflow and one complementary workflow**:

- DND/public-sector administration: knowledge/briefing plus procurement evidence.
- An enterprise with a large engineering program: knowledge plus SpecSuite/modernization.
- An enterprise with substantial service demand: knowledge plus a repaired, accepted service workflow.

Complementary does not mean “assume their peaks cancel.” Measure the overlap; many departments peak at the same time.

### Then: make the commitment evidence-based

| Gate | Deliverable | Commercial decision |
|---|---|---|
| Outcome fit | Sponsor, baseline, users, task frequency and overlap with existing licenses. | Is there an application worth deploying? |
| Functional acceptance | Representative evaluation set, end-to-end journey and error/permission checks. | Is the application good enough to pilot? |
| Demand and capacity proof | Per-model trace, quality, concurrency and Standard/provisioned comparison where justified and authorized. | Existing headroom, new PTUs, Standard or Batch? |
| Production ownership | Support, operations, network/data approvals, adoption plan and cost model. | Can the customer responsibly commit? |
| Expansion review | More adopted workflows/users, sustained useful demand and measured capacity constraints. | Expand capacity, retain, or rightsize? |

For an existing-PTU account, first demonstrate a valuable workload on available compatible capacity without disturbing current service objectives. For a new-PTU account, do not infer the answer from the existing-customer economics.

### Economics to show the buyer

Compare over the same period, quality level and service objective:

```text
Provisioned option =
  provisioned capacity cost at the applicable commitment/discount
  + spillover or other-model inference
  + application and supporting-service costs
  + implementation and operations

Alternative option =
  Standard inference for interactive work
  + Batch/specialized services for eligible work
  + comparable application, implementation and operations costs
```

Include minimum deployment sizes, duty cycle, model-specific cache/output treatment, headroom and realistic adoption. Do not quote a numerical PTU quantity or savings percentage from this lab.

An account team should report **production-accepted workflows, adoption, successful-task economics, PTU renewal/expansion and customer outcomes**. “We deployed twenty repositories” and “we generated more tokens” are not useful success metrics.

## 10. What to say to Scott, Hubert and the customer

### Internal recommendation

> Build a three-bundle field offer around Knowledge and Staff Work, Procurement and Document Operations, and Engineering Modernization. Use the lab to select and harden a small number of real workflows. Fund controlled drafting and evidence review before another accelerator sweep. Attach PTUs to proven, compatible production demand, and use an adoption program to turn existing idle capacity into useful outcomes and defensible renewals.

### Customer with existing PTUs

> “We will first check the models and capacity you already have. Then we will help deploy a small set of governed knowledge, document and engineering workflows that can use that capacity productively. We will show which work actually runs on your provisioned deployments, what other services cost, and the measurable value delivered. We will not recommend more capacity until adoption and performance justify it.”

### Customer considering PTUs

> “Start with the business problem: trusted knowledge, faster evidence review or controlled engineering modernization. We will prove the workflow and measure its demand. Where dedicated model capacity improves production predictability or economics, we will size the PTUs behind it. Where Standard or Batch is the better choice, we will say so.”

**Bottom line:** the hypothesis survives the exercise. The best sales asset is not a Swiss Army knife with twenty unverified blades; it is **a few useful, adopted applications with repeatable deployment, accountable support and credible capacity economics**.

## Evidence and source notes

### Local evidence reviewed

- `reports\ptu-bundle-evaluation.md` — first-pass dispositions, paused runtime state, inference mapping and limitations.
- `reports\capacity-and-billing-method.md` — model-specific capacity interpretation and separate charges.
- `reports\existing-apps-and-byok.md` — inventory-only status of protected apps and BYOK configuration limits.
- `reports\content.md` and `reports\conversation.md` — native workflow results and semantic/provider-quality qualifications.
- `PTU-Bundle-Continuation-Report.md` — continuation inspections and bounded tests, qualified where necessary in §2.
- `evidence\stepfly\tests\provider-ledger.jsonl` — twenty attempts, 249,144 prompt tokens and 178,944 cached tokens; not a production sizing study.
- `evidence\call-center-voice\tests\voicelive-probe*.json` — text response events; not a speech/telephony test.
- `evidence\video\tests\*.json` — per-test attempts/results.
- Original user-supplied M365 Researcher response — strategic hypotheses and attributed internal claims, not independently verified customer references.
- Local JDCP Cloud-Ops guidance — DND deployment considerations only; no JDCP resources were accessed or changed for this assessment.

The scores in the original researcher response are not reused: the available evidence does not justify precise 61–94 ranking scores, quantified customer savings, or verified internal ownership.

### Public sources checked on 12 September 2026

These establish documented capabilities, not a customer-specific deployment pass. Product status, prices, supported models and available regional capacity must be reconfirmed when quoting.

| Ref | Source | Decision supported |
|---|---|---|
| P1 | [Microsoft: provisioned throughput concepts](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput) | Standard/provisioned/Batch distinctions, model-specific processing capacity and geography. Apply cache guidance to the selected model; do not extrapolate a lab-wide multiplier. |
| P2 | [Microsoft: provisioned throughput billing](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput-billing) | Reservations are financial coverage, not deployable capacity or an all-model runtime pool. |
| P3 | [VS Code: language models and BYOK](https://code.visualstudio.com/docs/agent-customization/language-models) | Local BYOK endpoint/deployment support, current plan/policy distinctions and feature-routing limits. |
| P4 | [GitHub: bring your own key](https://docs.github.com/en/copilot/concepts/models/bring-your-own-key) | Local versus server-side enterprise BYOK; enterprise licensing and public-preview status. |
| P5 | [Microsoft: Voice Live bring your own model](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-bring-your-own-model) | Explicit documented support for customer PTU deployments. **This changes the earlier categorical exclusion.** |
| P6 | [Microsoft: Copilot Studio credits and billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management) | Native credits versus separately billed BYOM configurations. |
| P7 | [Microsoft: Security Copilot capacity](https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity) | SCUs are a different capacity/commercial construct. |
| P8 | [Microsoft: Fabric AI Functions billing](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/billing) | Built-in model calls versus custom endpoints; Fabric compute remains separate. |
| P9 | [Azure-Samples: Adaptive RAG Workbench](https://github.com/Azure-Samples/adaptive-rag-workbench) | Beta implementation reference, not a proven new product. |
| P10 | [Microsoft GraphRAG](https://github.com/microsoft/graphrag) | Configurable Azure inference for graph extraction/query; additional implementation/economic validation required. |
| P11 | [Microsoft Content Processing accelerator](https://github.com/microsoft/content-processing-solution-accelerator) | Existing multi-document implementation; source availability does not override the lab limitations. |
| P12 | [Microsoft MACAE accelerator](https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator) | Existing scenario engine and configurable model routing; not proof of a completed customer workflow. |
