# PTU Accelerator - internal meeting talking points

**Meeting:** 14 September 2026, 2:00 PM. **Audience:** Microsoft internal account, solution and delivery stakeholders.
**Format:** 13-slide main story (about 13 minutes), optional 2-minute static website walkthrough, then discussion. Slides 14-16 are appendix.
**Evidence:** Recorded 12 September 2026 results; no new deployment, inference, customer reference validation or PTU benchmark.
**Internal only:** Do not publish this document or the deck in the website.

## 60-second opening

We are not offering twenty production-ready apps with a PTU purchase. We are building a focused way to help customers solve recurring knowledge, document and engineering problems on Azure. Our evaluation identified useful building blocks, tested selected workflows and made the remaining gaps explicit. The commercial path is to prove the outcome, get it adopted and attach the capacity its real demand supports. For customers with existing PTUs, that starts with value realization and renewal; for new buyers, it starts with functional proof and a fair Standard, Batch and provisioned comparison. Today I want alignment on the three-bundle offer, two candidate account motions and the delivery owners to take the next gated step.

## Meeting preparation

- Open `PTU-Accelerator-Internal-2026-09-14.pptx`; use PowerPoint Presenter View for the embedded notes.
- Keep `PTU-Accelerator-Internal-2026-09-14.pdf` as the slide-only backup.
- Open `..\site\dist\index.html` for the updated local website. The hosted URL may still show the previous version until the normal publication workflow runs.
- Show only the static site and this deck. No live model calls, lab restart, raw operational evidence or resource inventory.
- If time is reduced to five minutes, use slides 1, 3, 4, 8 and 13.
- End by assigning roles and next outputs, not by asking for a capacity purchase today.

## Slide-by-slide delivery

### 1. Useful AI first. Capacity that earns its place.

**Timing:** 1 minute

Opening: We are not proposing that customers buy PTUs and receive twenty production-ready applications. We are proposing a repeatable way to solve a few important business problems, get those workflows adopted on Azure, and then attach the model capacity the evidence supports.

The engineering exercise gave us useful building blocks and, just as importantly, a clear view of what is not ready. Today I want alignment on the focused offer, two candidate-account motions, and the delivery owners needed to turn this into a credible customer engagement.

This is internal working material, not an official Microsoft SKU, support promise or approved customer case study.

**Transition:** Start with the customer friction, not the technology list.

**Sources / qualifications:** PTU-Bundle-Commercial-Recommendation.md, sections 1 and 10; evidence snapshot 12 September 2026.

### 2. Customers need finished work, not another AI demo.

**Timing:** 1 minute

The entry point is an unfinished business task. A policy analyst needs a trustworthy comparison and briefing. A procurement reviewer needs a defensible evidence package. An application owner needs a change that survives execution tests.

Ask who owns the task, how often it happens, what the current process costs, what makes an output acceptable, and why existing Microsoft 365 Copilot, Copilot Studio, GitHub Copilot or conventional search does not already meet the requirement. These are target problems, not verified customer savings claims.

A high-value task does not automatically have enough sustained traffic to justify PTUs.

**Transition:** Package those needs into three understandable outcomes, not twenty separate products.

### 3. Three outcome bundles. One governed foundation.

**Timing:** 1 minute

Knowledge and Staff Work is the broad adoption anchor. Procurement and Document Operations turns document intelligence into reviewer-ready evidence. Engineering Modernization is a strong program-led motion when there is an engineering sponsor.

CWYD means Chat With Your Data; DKM means Document Knowledge Mining. These are building blocks, not a promise that the entire bundle is already implemented. Controlled drafting and contract/RFP review need implementation and acceptance. SpecSuite remains conditional on its owner, licensing and delivery/support agreement; we did not retest it.

The common foundation should reuse the customer's approved platform where practical. We should not create twenty disconnected frontends or a large new landing zone for every small use case.

**Transition:** The lab has given us a useful starting point, with a very specific evidence boundary.

### 4. We turned a broad catalog into an evidence-led shortlist.

**Timing:** 1 minute

The combined review assessed all twenty original candidates, but that is not twenty successful deployments. Seven accelerator repositories were assigned to first-pass implementation tracks. Existing SpecSuite and Planetary Explorer applications were protected and inventoried rather than retested.

We exercised selected native workflows, retained reusable adaptations and evaluation evidence, and separated customer-safe messaging into a static website. The strongest first-pass results were selected CWYD, DKM and Modernize workflows; Content had a limited missing-document success.

No provisioned throughput or reservations were purchased. Standard and GlobalStandard results tell us about selected functionality and model demand, not provisioned utilization, customer economics or production scale. Historical inference allowances are closed.

**Transition:** That gives us enough to focus delivery, not enough to promise a turnkey bundle.

**Sources / qualifications:** reports/ptu-bundle-evaluation.md sections 1-3; PTU-Bundle-Commercial-Recommendation.md section 4; adaptations/README.md and root README.md.

### 5. Show the selected passes. Fund the gaps.

**Timing:** 1 minute

Be explicit if anyone asks what can be demonstrated today. CWYD passed eight selected criteria in an adapted local runtime; it was not a hosted production acceptance. DKM demonstrated ingestion, cited QA and comparison on two of ten fixtures, with no full browser journey. Modernize passed a selected upload/process/download API flow, not actual source-to-target database equivalence.

Content correctly flagged missing evidence but its full happy path did not pass. MACAE final synthesis, the chatbot grounded answer, and Conversation semantics still had important failures. We should not demonstrate those as ready-to-run customer solutions.

Today use the static website and an honest evidence walkthrough. The lab is paused/disarmed and no new inference has been authorized. A future live demo needs a separately approved run, a fixed scenario and a verified starting state.

**Transition:** Here is the business workflow we should build next.

### 6. From approved sources to a reviewer-ready briefing.

**Timing:** 1 minute

Tell a simple hypothetical story: a policy analyst needs to compare two approved policy versions and prepare an options briefing. Instead of searching several systems and pasting into a blank chat, they select approved sources and a governed template. The application retrieves the relevant evidence, produces a cited draft, exposes uncertainties and changes, and routes it for human approval.

The business outcome is the approved work product, not the generated text. Measure accepted drafts, reviewer effort and factual corrections against the current process. This is a proposed next build extending knowledge-workbench components, not an implemented capability or a customer case study. The compiled marketing-content repository is not evidence that this controlled drafting workflow exists.

The reviewer retains the decision, and export must preserve citations and document/version provenance.

**Transition:** The workflow creates demand; the platform must route and govern it correctly.

**Sources / qualifications:** PTU-Bundle-Commercial-Recommendation.md section 6, priority addition 1.

### 7. One experience. Clear routes. Separate costs.

**Timing:** 1 minute

PTUs cover compatible model inference, not the whole application. We need to verify the actual provider endpoint, model and version, API, deployment type and processing geography. Two applications using different models or trust boundaries may need separate capacity groups.

The platform layer should attribute successful tasks and model demand per application, protect interactive service objectives with admission control, and use only approved, separately metered alternatives or spillover. No automatic routing or fallback is implied by this conceptual diagram.

Search, hosting, OCR, speech, embeddings on other deployments, storage and implementation remain separate cost lines. Azure adoption can grow through useful application services even when the right model option remains Standard or Batch. Do not double-count provider usage, billable spend or already committed capacity.

Reservations provide matching financial coverage, not a guarantee of deployable capacity or one runtime pool.

**Transition:** That is why customers who already have PTUs need a different motion from new buyers.

### 8. Two capacity situations. Two sales motions.

**Timing:** 1 minute

For an existing-PTU customer, start by understanding actual deployments, workloads, renewal timing and headroom. A compatible additional request within headroom generally does not add another PTU-hour when that capacity remains allocated anyway, but application and other service costs still apply. Protect current users and measure useful outcomes.

For a new buyer, the hurdle is different. Prove the application, capture realistic per-model demand and compare equivalent quality and service objectives across provisioned, Standard and eligible Batch. Do not force PTUs into a small pilot.

Adopting idle capacity is not the same as selling additional capacity. It can support renewal, but an oversized allocation should still be rightsized. Expansion is justified only by sustained additional valuable demand or a demonstrated capacity constraint.

**Transition:** This is how customer value translates into credible Azure growth.

### 9. Turn customer value into Azure growth.

**Timing:** 1 minute

There are three distinct commercial effects. First, a useful application can create Azure service usage and appropriate model consumption. Second, adoption on existing compatible PTUs can improve value realization and renewal confidence. Third, additional adopted demand may justify a new or expanded provisioned deployment.

Do not add those up as if they were all incremental PTU revenue. The lab does not support a dollar forecast, a savings percentage or a PTU quantity. Partners can provide scoped implementation and operations, but those services are not an automatic Microsoft support commitment.

Our internal scorecard should connect each account to a successful workflow and an evidence-based next decision. More repositories, more agents and more tokens are not business success metrics.

**Transition:** We win by being more specific about outcomes and more credible about proof.

### 10. Win with useful workflows and inspectable proof.

**Timing:** 1 minute

Do not pitch custom development as inherently better than Microsoft 365 Copilot, Copilot Studio, GitHub Copilot or Purview. Qualify an unmet workflow, integration, corpus, evidence schema or operational-control requirement. If an existing product meets the need with lower lifecycle cost, use it.

Our differentiation is a focused business workflow with inspectable evidence, an accountable delivery model and a capacity decision tied to reality. For procurement, people retain award and legal decisions. For engineering, tests and human review retain change authority. For regulated accounts, data classification, network and identity approvals, processing geography and retention remain separate gates; PTUs confer none of those approvals.

Name the implementer and the operator before promising a production engagement.

**Transition:** A short gated engagement is the practical way to prove this, not another portfolio sweep.

### 11. A 30-day qualification sprint, with decision gates.

**Timing:** 1 minute

This is a proposed engagement sequence, not a guaranteed delivery date or a funded plan. In week one, qualify the problem and the existing-product gap with a sponsor. In week two, agree a representative evaluation set and demonstrate the end-to-end journey, including error and permission cases. In week three, measure actual model-specific demand and compare alternatives at the same service objective and quality. Week four produces a documented capacity recommendation, pilot scope and operating owner.

Every gate can produce a no-go, more engineering work, or a Standard/Batch recommendation. If data or landing-zone approvals are missing, the work remains prerequisite-gated; do not work around them. Any new lab inference or capacity test needs explicit authorization and a bounded cost allowance.

Start with one broad daily workflow and one complementary workflow, not all three bundles at once.

**Transition:** Make success visible in one shared scorecard.

### 12. Measure business success before capacity expansion.

**Timing:** 1 minute

Agree the baseline and thresholds with the customer before a pilot. Track time to an accepted artifact, task quality and reviewer corrections. Then track repeat use and accepted workflows, rather than registrations or raw requests.

Operational measurement must be per model, with actual input/output lengths, cache behavior, calls per task, retries, peak concurrency and tail latency. Capture supporting-service and operating costs as well as model costs. Cost per successful task should use accepted tasks as the denominator, not all generated answers.

For commercial tracking, separate new Azure usage from already committed PTU spend. Record the decision and why it follows from the evidence: retain, expand, rightsize, or continue on Standard/Batch. These are proposed measures, not achieved customer results.

**Transition:** Close with a concrete decision request for this group.

### 13. Back the focused offer. Give the first two motions owners.

**Timing:** 1 minute

Close: My ask is not approval to buy capacity today. It is alignment on a focused three-bundle offer, two candidate account motions and the accountable people to execute them. Lead with knowledge and controlled drafting. Nominate one account with compatible existing PTUs and one account where a new production demand case can be measured.

Name an account lead, an engineering or delivery partner lead, an operating owner and a capacity/economics lead. Those are roles to assign, not people already committed. The next deliverable is an account-specific pilot scope with acceptance gates, a costed operating model and a defensible capacity recommendation.

Final line: We earn the capacity conversation by solving the customer's problem first.

**Transition:** Open discussion; use the appendix for readiness, economics and source questions.

### 14. What the strongest recorded tests actually establish.

**Timing:** Appendix / as needed

Use this page if asked whether the bundle is production-ready. The answer is no: selected scopes passed, and the limitations matter. CWYD ran in an adapted local runtime. DKM tested only two fixtures and had no full browser journey. Modernize's selected translation flow is not source-to-target execution equivalence. Content had a limited negative/missing-document success, not its complete happy path.

The other first-pass apps retained central workflow or semantic failures. Existing SpecSuite and Planetary were inventory-only. Voice Live has a documented customer-PTU BYOM route, but our four managed-model probes were text-mode component checks, not speech, telephony or PTU BYOM acceptance.

Do not reuse the earlier categorical claim that Voice Live cannot use customer PTUs. The commercial recommendation qualifies and corrects that claim.

**Transition:** If the question is PTU sizing or savings, use the economics gates instead of extrapolating these tests.

**Sources / qualifications:** reports/ptu-bundle-evaluation.md sections 1-3; PTU-Bundle-Commercial-Recommendation.md sections 2 and 4; Voice Live source listed in Appendix C.

### 15. No fixed PTU quantity or savings claim from this lab.

**Timing:** Appendix / as needed

There is no reliable portfolio-wide token-to-PTU multiplier. Use model-specific output weighting, caching, minimum deployment sizes, duty cycle, peak overlap and headroom. The StepFly cache sample is not a general sizing correction. Measure useful demand and compare at a consistent quality and service objective.

A reservation is financial coverage subject to the current matching rules; it does not guarantee capacity availability. Confirm deployment availability and current commercial terms before recommending matching coverage. Do not quote a price, savings percentage or fixed PTU number from this presentation.

PTUs do not improve the same model's inherent answer quality, guarantee end-to-end application latency, repair retrieval, replace identity controls or provide security accreditation. Where Batch or Standard is better, recommend it.

**Transition:** Refer to current product documentation at quotation time.

**Sources / qualifications:** PTU-Bundle-Commercial-Recommendation.md sections 2, 3 and 9; Microsoft provisioned throughput concepts and billing documentation.

### 16. Evidence behind the story. A safe way to show it.

**Timing:** Appendix / optional 2-minute walkthrough

Use the rebuilt local site for the updated design unless publication has separately been confirmed. From this presentation folder, open ..\site\dist\index.html. Website source changes are not automatically evidence that the hosted site has changed.

Walk through Overview, open Solutions and inspect one selected-pass candidate, then use the PTU guide to explain existing versus new capacity. Finish on Next steps and make clear that controlled drafts are a proposed implementation. This is an informational portfolio demonstration, not a live accelerator execution.

If the browser is unavailable, use slides 3, 5 and 8. Do not open raw evidence, deployment inventories or operational consoles on the shared screen. Keep the deck and talking points outside site\dist.

**Transition:** Return to slide 13 for the decision.

**Sources / qualifications:** Internal: PTU-Bundle-Commercial-Recommendation.md (12 September 2026), especially sections 1-6 and 9-10.
Internal: reports\ptu-bundle-evaluation.md (12 September 2026), sections 1-3.
Internal: PTU-Bundle-Continuation-Report.md; interpret with the commercial recommendation's corrections.
Public: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput
Public: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput-billing
Public: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-bring-your-own-model
Website: https://blue-beach-0fb8cd70f.5.azurestaticapps.net/
Public documentation was recorded as checked on 12 September 2026 by the recommendation; not independently refreshed for this deck. Reconfirm at quotation time.

## Acronyms to explain once

PTU: Provisioned Throughput Unit, a unit of compatible model-serving capacity.
CWYD: Chat With Your Data. DKM: Document Knowledge Mining.
SLO: service-level objective, such as a target response time under a defined load.
CSA: Cloud Solution Architect. BYOM / BYOK: bring your own model / key; actual routing depends on the product path.

## Likely questions and recommended answers

**Is this an official Microsoft SKU or a supported turnkey bundle?**
No. It is a proposed field-and-partner delivery offer using selected accelerator components. Scope, licensing, ownership and post-go-live support must be explicitly agreed.

**What can we actually show today?**
The static portfolio and a walkthrough of recorded selected CWYD, DKM and Modernize results, with limits. The lab is paused/disarmed. A fresh live application demo requires separate approval and a verified setup. Do not describe the website as running the accelerators.

**Why not Microsoft 365 Copilot, Copilot Studio or GitHub Copilot?**
Use those when they meet the need. Qualify an unmet workflow, corpus, evidence, integration or operating-control requirement before recommending a custom application. Accelerator source availability alone is not a reason to rebuild.

**How does this increase Azure usage and PTU purchases?**
Useful deployed workflows can create application-service and model usage. Existing-PTU adoption improves value realization and may support renewal. Additional PTU purchases follow only when adopted, compatible workloads justify added capacity. These are distinct effects, not a forecast and not interchangeable revenue.

**Why not simply fill all idle PTUs with background jobs?**
Only admit useful approved work within measured headroom, priorities and cost budgets. Protect interactive users. Delay-tolerant work needs a Batch comparison; rightsizing may be the right renewal decision. Artificial token generation is not customer value.

**How much capacity or savings can we quote?**
None from this lab. Measure per-model workload, quality, cache and output treatment, peaks, concurrency, duty cycle, headroom and full-stack costs. Compare equivalent Standard, eligible Batch and provisioned options, then confirm capacity availability and current terms.

**Does a PTU purchase make the apps free or more accurate?**
No. It is model-serving capacity, not the application, search, OCR, speech, other model deployments, licensing or delivery. It does not inherently improve the same model's answer quality or guarantee end-to-end latency.

**Can all apps use one PTU pool?**
Only compatible requests can share a deployed model endpoint. Different models, API requirements, processing geography or trust boundaries can require separate groups. Reservation financial coverage is not one all-model runtime pool.

**What about Voice Live and developer BYOK?**
The recommendation records a documented Voice Live customer-PTU BYOM path, but the lab did not test it; managed text probes do not establish an audio journey. BYOK paths depend on the client, feature, licensing, policy, network and model configuration. Neither is a blanket customer-PTU routing guarantee.

**What would we build first?**
A controlled, source-backed drafting workflow on the selected knowledge workbench. Pair it with procurement evidence review or engineering work only where a sponsor and acceptance criteria exist. These are proposed builds, not currently demonstrated complete workflows.

**What about regulated customers and Canadian residency?**
Data classification, processing geography, identity/network approvals, retention, bilingual/accessibility needs and an accountable operating model are prerequisites. A Canadian resource address or private endpoint is not proof of Canadian-only model processing. This synthetic lab is not a customer accreditation.

## Close and record decisions

1. Agree whether the three-bundle framing and knowledge/drafting priority are the right focused offer.
2. Nominate one existing-PTU and one new-demand candidate account; these are nominations, not confirmed customers.
3. Assign account, engineering/partner, operations and capacity/economics roles.
4. Agree the next output: account-specific scope, prerequisites, acceptance thresholds and a costed capacity decision.

**Closing line:** We earn the capacity conversation by solving the customer's problem first.
