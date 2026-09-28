// Customer walkthroughs complement the pinned manuals; they do not certify deployments.
export const deploymentReviewDate = '2026-09-25';
export const deploymentGuides = {
  1: {
    route: 'Azure application', source: 'deployment',
    steps: [
      ['Prepare the environment', 'Use the guide\'s local environment or reopen the pinned checkout in its dev container. Local setup needs Python 3.11, Node LTS, PowerShell and azd; the data setup script requires Azure CLI 2.87+. Avoid azd 1.23.9 rather than disabling preflight checks.'],
      ['Configure before provisioning', 'Review infra\\main.parameters.json and the linked parameter guide. Explicitly choose databaseType: the guide and top-level template disagree on its default. Confirm chat and embedding deployments, identity, region and approved network access. Resource reuse is not proof of PTU routing.'],
      ['Provision infrastructure', 'Sign in to both CLIs, select the approved subscription and choose a new environment when prompted. This leaves placeholder images, not a working application.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Install the application and data plane', 'From the repository root, run these in order with the resource group produced above. The image script can temporarily open registry access: stop and arrange an approved private build path if policy prohibits that behavior.', '.\\infra\\scripts\\post-provision\\acr_build_push_update.ps1 -ResourceGroupName "<resource-group>"\n.\\infra\\scripts\\post-provision\\post_deployment_setup.ps1 -ResourceGroupName "<resource-group>"'],
      ['Require sign-in and ingest a small collection', 'Complete the authentication instructions in Step 5.3 of the pinned guide before sharing. Open the frontend URL, go to /admin, choose Ingest Data and upload permitted sample documents. Wait for ingestion; sign-in alone does not implement document-level authorization.'],
    ],
    verify: 'Ask a question with a known answer, open its citations and test an unanswerable question. Check user/history separation and document access with two test identities; verify the actual model deployment in provider telemetry.',
  },
  2: {
    route: 'Azure application', source: 'deployment',
    steps: [
      ['Prepare tools and model configuration', 'Use PowerShell 7+, Azure CLI, compatible azd, Bicep CLI 0.33+ and Python. Review infra\\main.parameters.json and the guide\'s Foundry reuse instructions. Match deployment names in team configurations; existing-project reuse can still create separately billed models.'],
      ['Provision the selected environment', 'Select the approved subscription, environment, infrastructure region and AI region. Do not reuse an unrelated .azure environment or bypass failed preflight checks.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Build all runtime images', 'Run from the repository root. This installs frontend, backend and MCP server images; provisioning alone does not install them.', '.\\infra\\scripts\\post-provision\\Build-And-Push-Images.ps1'],
      ['Initialize one scenario', 'Run the setup menu, select the agreed content pack and allow its data, indexes and team configurations to finish. Inspect persisted agent model selections after initialization.', '.\\infra\\scripts\\post-provision\\post_deploy.ps1'],
      ['Configure access and open the application', 'Complete the guide\'s App Authentication Configuration before sharing. In the resource group, open the frontend App Service Default domain, sign in and select the initialized use case.'],
    ],
    verify: 'Run a known multi-agent task through the final combined answer, not only individual agents. Final synthesis failed in the historical evaluation; require remediation and a successful end-to-end result before adoption.',
  },
  3: {
    route: 'Private package - access required', source: null,
    steps: [
      ['Request the approved package', 'Ask the program team to coordinate owner-approved repository access or a code handoff for SpecSuite. Obtain the revision, license, support owner and a real product walkthrough.'],
      ['Obtain the missing installation runbook', 'The owner must supply tool versions, dependency restore instructions, configuration names, graph/storage initialization, deployment commands, authentication setup and upgrade/rollback steps. These are not verified publicly; stop here until supplied.'],
      ['Review the target design', 'Confirm supported languages/frameworks, model endpoints, knowledge-graph hosting, data retention, identity and network requirements with the owner. Approve costs and source-code access before installation.'],
      ['Install with the owner', 'Follow the supplied revision-specific runbook in the approved environment. Record commands, configuration and outputs without credentials; require a clean-environment reproduction before describing it as self-service.'],
      ['Load one permitted module', 'Run code-to-spec, inspect graph relationships and generated specifications, then scope one spec-to-code change. Keep generated changes on a review branch.'],
    ],
    verify: 'The owner demonstrates sign-in, code ingestion, graph/specification output and a reviewed generated change passing the project\'s regression checks. Until then, this is an access-and-validation path, not full deployment instructions.',
  },
  4: {
    route: 'Azure application - maintenance gate', source: 'deployment',
    steps: [
      ['Resolve maintenance and tooling', 'This upstream is no longer maintained. Obtain an accountable maintenance owner or choose a replacement first. Prepare the guide\'s PowerShell, Azure CLI, azd and Kubernetes deployment prerequisites.'],
      ['Review configuration and provision', 'Review infra\\main.parameters.json, model/embedding deployments, AKS sizing and network settings. Sign in, select the approved subscription and run the infrastructure stage; do not relax filters or increase quotas as a shortcut.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Install Kubernetes application components', 'From the repository root, enter Deployment and run the application installer. With an azd deployment it discovers configuration; inspect every prompt and stop on errors.', 'Set-Location Deployment\n.\\resourcedeployment.ps1'],
      ['Configure authorized access and load data', 'Use the installer\'s final application URL and complete the guide\'s authentication/data-upload steps. Load only the approved small corpus and wait for processing. Do not copy upstream suggestions to weaken content filters.'],
      ['Open document and collection chat', 'Use Chat with documents, then open a document\'s Details and chat view. Check the extracted material before relying on an answer.'],
    ],
    verify: 'Compare extracted fields and answers with source documents, including empty/unsupported documents and a second user\'s access. The historical limited-corpus result is not acceptance of a new installation.',
  },
  5: {
    route: 'Platform configuration', source: 'deployment',
    steps: [
      ['Choose the client and route', 'Agree whether the pilot uses centrally managed enterprise custom models or local VS Code BYOK. Record client version, licensing, policy owner and required chat/tool-calling features; this does not replace inline completions.'],
      ['Prepare the approved model endpoint', 'The Azure owner supplies the deployment URL, deployment/model ID, supported API and authentication through an approved secret channel. Verify geography and PTU deployment type; a Foundry account name alone is insufficient.'],
      ['Configure enterprise custom models', 'An enterprise administrator follows the linked guide: open enterprise AI controls, add the provider credential and models, then grant the intended organizations access. Enable applicable custom-model policies; do not distribute the provider key in source code.'],
      ['Or configure local VS Code', 'In Chat, open the model picker and Manage Language Models, select the provider and enter its required endpoint/model/authentication settings. Use the linked VS Code guide for provider-specific fields. Local configuration remains subject to organization policy.'],
      ['Select the model and perform a bounded task', 'Reopen the client if needed, select the configured model and use a permitted repository for chat and one reviewed agent/tool task. If the model is absent, resolve policy, provider or API compatibility rather than claiming setup succeeded.'],
    ],
    verify: 'Correlate the task with usage on the intended Azure deployment. Test organization restrictions and credential rotation. Record which client features worked; do not infer all Copilot features or offline operation.',
  },
  6: {
    route: 'Azure application', source: 'deployment',
    steps: [
      ['Prepare configuration', 'Use the pinned guide\'s local toolchain or dev container. Review infra\\main.parameters.json, extraction model availability, Foundry reuse, identity, network settings and schema requirements. Use compatible azd rather than disabling preflight.'],
      ['Provision infrastructure', 'Select the approved subscription and a new lowercase alphanumeric environment. This is only the infrastructure stage.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Install images, then initialize schemas', 'Run from the repository root in this order. Check the API is ready and the Auto Claim schema set exists. The guide mentions automatic registration, but the pinned manifest has no post-provision hook; do not assume these steps ran.', '.\\infra\\scripts\\acr_build_push.ps1\n.\\infra\\scripts\\post_deployment.ps1'],
      ['Configure application authentication', 'Complete ConfigureAppAuthentication.md, linked from Step 5 of the manual: register the required applications, configure the frontend/API identity settings and callback URLs, and apply consent as documented. Authentication is required for access.'],
      ['Upload and inspect a sample', 'Open the Web App Endpoint from deployment output, sign in, select Auto Claim and the matching schema, then Import Content. Use the permitted sample files under src\\ContentProcessorAPI\\samples before designing customer schemas.'],
    ],
    verify: 'Open a completed row and compare every required field with its source. Exercise missing fields, invalid input and authorization failures; capture extraction errors rather than treating a completed status as accuracy.',
  },
  7: {
    route: 'Azure application', source: 'deployment',
    steps: [
      ['Select a scenario before deployment', 'Prepare the README\'s tools and review infra\\main.parameters.json. Use one environment per scenario: ecommerce, healthcare or banking. The example selects ecommerce; change it before the first provision, not after seeding.', 'azd env new "<environment-name>"\nazd env set AZURE_ENV_SCENARIO ecommerce'],
      ['Authenticate and provision', 'Review model deployments, search indexes, application permissions and network access for the selected scenario, then select the approved subscription.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Build the application images', 'From the repository root, run the image command printed by the pinned manifest. Wait for the web apps to use the new images.', '.\\infra\\scripts\\post-provision\\build_push_images.ps1'],
      ['Load data and create agents', 'Run both stages together. Confirm the scenario\'s catalog/policy indexes and Foundry agents were created and that their model assignments match the approved deployment.', '.\\infra\\scripts\\post-provision\\postprovision_data_agents.ps1'],
      ['Open the scenario experience', 'Open Scenario Web App URL from deployment output and its embedded chat widget; Chat Web App URL is the separate chat surface. Review access, CORS and allowed origins before exposing the customer-facing host.'],
    ],
    verify: 'Ask a policy question and a catalog question against seeded facts, then an unsupported question. Require grounded answers, correct citations and a safe fallback; the historical grounded-answer requirement was not met.',
  },
  8: {
    route: 'Azure application', source: 'deployment',
    steps: [
      ['Prepare the deployment and privacy controls', 'Use the pinned tool prerequisites; review infra\\main.parameters.json, model, SQL and search configuration. Approve transcript redaction/retention. Some private-network hooks temporarily open data-plane access: stop if tenant policy forbids this and arrange an approved build/data path.'],
      ['Run the complete hook-driven deployment', 'Sign in to both CLIs. Select the approved environment, subscription and region. Unlike several other entries, this package automatically builds images, configures SQL roles and launches data setup through its hooks.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Complete the interactive data menu', 'Select the agreed scenario when prompted; wait for sample upload, search setup and Foundry agent creation. For bring-your-own-data options, obtain index/table/workspace settings and permissions from ConnectDataSource.md first. Keep the generated .env private.'],
      ['Verify access and application startup', 'Use the frontend Open URL printed by the hook or its App Service Default domain. Complete the guide\'s authentication steps and confirm the signed-in user can access only the permitted conversation dataset.'],
      ['Inspect analytical outputs', 'Run a known query and inspect summaries, sentiment and aggregate results against a small, manually reviewed transcript set. Check SQL/search/agent errors rather than rerunning unrelated deployment stages.'],
    ],
    verify: 'Confirm record counts, SQL joins, sentiment interpretation and grounded answers. Historical semantic defects remain relevant; a successful data pipeline does not establish trustworthy analytics.',
  },
  9: {
    route: 'Azure application - maintenance gate', source: 'deployment',
    steps: [
      ['Resolve maintenance and conversion scope', 'Require a maintenance owner or supported replacement. This package converts Informix SQL to T-SQL, not arbitrary application languages. Prepare the guide\'s tooling and an isolated test database.'],
      ['Configure and provision', 'Review infra\\main.parameters.json, model deployment, hosting and network requirements. Select the approved subscription and a fresh environment.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Install application images', 'From the repository root, run the separate ACR image installation stage; provisioning only prints this next step.', '.\\scripts\\build_and_push_images.ps1'],
      ['Require sign-in', 'Complete AddAuthentication.md from the pinned deployment guide. Open the frontend Container App Application URI and verify authorized sign-in before uploading source.'],
      ['Convert a sample batch', 'Start with permitted files under data\\informix. Upload, select Start Processing, inspect batch status and download the translated files and reports using Download all as .zip.'],
    ],
    verify: 'Review the SQL and execute representative original/translated queries on isolated test data. Compare results and error behavior; generated syntax alone does not establish behavioral equivalence.',
  },
  10: {
    route: 'GitHub Actions application deployment', source: 'deployment',
    steps: [
      ['Prepare an approved fork and deployment identity', 'Use QUICK_DEPLOY.md with Azure CLI and GitHub Actions access. In your fork create a deployment branch at the pinned revision. Have the Azure administrator approve the OIDC identity and minimum deployment/RBAC scope; do not automatically grant broad subscription rights.'],
      ['Configure the GitHub environment', 'Create the dev environment matching the federated credential subject. Add AZURE_CLIENT_ID, AZURE_TENANT_ID and AZURE_SUBSCRIPTION_ID using its secret settings. Set an approved RESOURCE_GROUP variable; keep ENABLE_AUTO_DEPLOY off during review.'],
      ['Configure sign-in and infrastructure inputs', 'Register the single-tenant authentication application and provide AUTH_CLIENT_ID as described in Step 8.3. Confirm the callback URL, allowed users and network posture. Review model creation/routing; leave Fabric capacity, weather services and other paid extensions disabled unless separately approved.'],
      ['Run the reviewed workflow', 'In your fork, open Actions > Deploy Planetary Explorer > Run workflow. Select the branch at the reviewed revision and Force deploy all components. Select only approved model and networking inputs. Do not run a mutable default branch or assume the default model uses existing PTUs.'],
      ['Open the deployed frontend', 'Wait for all required workflow jobs and runtime services to succeed. Use the application URL from workflow output; test Entra sign-in, map loading and one permitted satellite-search question. Resolve missing permissions or model quota without bypasses.'],
    ],
    verify: 'Confirm actual imagery/catalog results, grounded explanation and denied access for an unauthorized user. Verify provider routing and independently record any optional features that were not deployed.',
  },
  11: {
    route: 'Voice API integration', source: 'deployment',
    steps: [
      ['Prepare the baseline client', 'Open the official quickstart and choose Python plus your operating system and keyless authentication. Use Python 3.10+, the listed audio dependencies, a microphone and a supported Foundry resource. Obtain the documented Cognitive Services User permission.'],
      ['Run the documented quickstart', 'Create the quickstart\'s Python environment using approved package feeds, save its sample as voice-live-quickstart.py and set its documented endpoint/authentication configuration. Sign in with Azure CLI and confirm audio input/output before adding business tools. A managed baseline is not yet your PTU route.'],
      ['Grant model access', 'In the Voice Live Foundry resource, enable its system-assigned identity. On the model resource, grant that identity the current documented Foundry User role. Cross-resource BYOM needs this even with key authentication; verify the real role definition, not a placeholder ID in an example.'],
      ['Apply the BYOM client changes', 'Follow the linked BYOM guide\'s Python changes: add the profile and optional resource-override arguments, pass them into BasicVoiceAssistant, and send profile/resource override in the connection query. Use the deployment name, not just a model family.'],
      ['Run against the chosen deployment', 'After applying those changes, use the chat-completion profile for a compatible text-model deployment. For a different Foundry resource add the documented --foundry-resource-override argument. Confirm API/SDK compatibility.', 'python voice-live-quickstart.py --byom "byom-azure-openai-chat-completion" --model "<deployment-name>"'],
    ],
    verify: 'Measure a complete conversation, interruptions and long-session authentication; correlate it with the intended model deployment. Speech/Voice Live charges remain separate. Hosting a business client, tools and handoff requires additional implementation.',
  },
  12: {
    route: 'Custom implementation required', source: null,
    steps: [
      ['Agree the review contract', 'Choose RFP evaluation or contract compliance, appoint the human decision-maker and define required evidence, scoring limits and prohibited automated decisions. Create a synthetic reference set with expected findings.'],
      ['Select the implementation base', 'Review the separately pinned MACAE RFP and contract packs in Code & sources. If choosing MACAE, use solution 2\'s deployment walkthrough for its base runtime; pack availability is not a working RFP application.'],
      ['Reconcile the package versions', 'The reviewed content packs and base application have different pins. An engineer must verify their schemas, dependencies and model selections together, record a compatible revision/overlay and supply the actual initialization commands. Do not copy a newer pack blindly into the older runtime.'],
      ['Implement evidence and reviewer controls', 'Configure approved extraction/retrieval, document versions, authorized access and source-linked findings. Add the reviewer workflow and retention controls. Remediate the known final-synthesis failure before acceptance.'],
      ['Publish a reproducible runbook', 'Record the chosen revision, tools, parameters, deployment and data-loading commands, sign-in setup, expected outputs and recovery procedure. Reproduce it in a clean approved environment before offering self-service deployment.'],
    ],
    verify: 'A reviewer checks final synthesis, material findings, missing evidence and false positives against the reference set. Until the integration and runbook exist, this remains a proposed workflow rather than an installable package.',
  },
  13: {
    route: 'Azure application', source: 'deployment-azd',
    steps: [
      ['Prepare text and image dependencies', 'Use the linked azd guide\'s tool versions. Review infra\\main.parameters.json and the text/image deployment settings; both model types must be available. Approve brand inputs, image rights and the backend network route.'],
      ['Provision the environment', 'Sign in to both CLIs and select the approved subscription. Infrastructure uses placeholder images; do not stop at azd success.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Build images, then load sample data', 'From the root, activate the Python environment before running the two scripts in order. Review approved feed settings and sample-loading behavior first.', 'python -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\n.\\infra\\scripts\\build_and_deploy_images.ps1\n.\\infra\\scripts\\process_sample_data.ps1'],
      ['Configure authentication', 'Complete AppAuthentication.md linked by the deployment manual. Open the App Service Default domain after its application and backend are healthy; test allowed and denied sign-ins.'],
      ['Generate a reviewed draft', 'Enter an approved creative brief, select Confirm Brief, choose a product and Generate Content. Inspect generated text, images and brand feedback before any publishing.'],
    ],
    verify: 'Verify product claims against source facts, check image generation and rights, and require editorial approval. Text PTUs do not include image generation, hosting or storage.',
  },
  14: {
    route: 'Infrastructure foundation - maintenance gate', source: 'deployment',
    steps: [
      ['Resolve ownership and initialize pinned submodules', 'Prefer the tenant\'s existing foundation. If this unmaintained reference is approved, assign a maintenance owner and use PowerShell 7+, Azure CLI, azd and Bicep. Initialize the recorded submodule commits; never pull their latest main.', 'git submodule update --init --recursive'],
      ['Initialize the approved environment', 'Sign in to both CLIs. Use the intended tenant, subscription and approved principal; the principal value is an Entra object ID, not an application client ID.', 'azd auth login\naz login\nazd env new "<environment-name>"\nazd env set AZURE_TENANT_ID "<tenant-id>"\nazd env set AZURE_PRINCIPAL_ID "<principal-object-id>"\nazd env set AZURE_SUBSCRIPTION_ID "<subscription-id>"'],
      ['Review active feature flags', 'Edit infra\\main.bicepparam and review hooks. Explicitly choose Fabric capacity/workspace presets (none or approved existing resources where appropriate), optional Purview and database integrations. Check PostgreSQL networking separately from general network isolation.'],
      ['Provision and inspect hook results', 'Run only after cost/network approval. Validate every enabled hook, not just Azure resource creation. Use an authorized private-network workstation for private data-plane operations; do not temporarily open protected services.', 'azd up'],
      ['Validate the selected onboarding path', 'Use the manual\'s post_deployment_steps.md. For an enabled Fabric/Search route, load approved PDFs into the bronze lakehouse Files/documents location, check indexing and configure the Foundry playground data connection. Application publishing is a separate linked step.'],
    ],
    verify: 'Check identity, connectivity, indexing and enabled integrations. Record disabled features explicitly. This delivers an infrastructure foundation, not a completed business application or production certification.',
  },
  15: {
    route: 'Copilot Studio customization kit', source: 'maker-setup',
    steps: [
      ['Confirm platform access and licensing', 'Obtain the required ESS/Copilot Studio entitlements, a permitted Dataverse environment and an existing agent or approved agent-creation path. This kit customizes agents; installing developer tools does not deploy an ESS service.'],
      ['Set up the pinned maker workspace', 'Use setup\\README.md for the tool/dependency prerequisites and open solutions\\ess-maker-skills in VS Code. Review installer telemetry and feed settings. Avoid the one-line bootstrap against main; it can replace the reviewed checkout with a newer revision.'],
      ['Connect and check prerequisites', 'In the maker workspace, run /setup in Copilot Chat, sign in and select the intended Dataverse environment/agent. Run FlightCheck and resolve licensing, permission and configuration failures before pushing changes.', 'python scripts\\flightcheck\\cli.py --scope full'],
      ['Customize a bounded topic', 'Use the maker guide to pull the agent and create a checkpoint. Generate or edit one topic/workflow locally, run its error scan and inspect the dry-run diff. Keep connection credentials out of generated files.'],
      ['Push, verify and publish deliberately', 'Push only the reviewed changes to the selected development agent using the kit\'s documented workflow. Test in Copilot Studio, complete connection/consent configuration and publish only after the environment owner approves the intended channel and audience.'],
    ],
    verify: 'An authorized employee completes the selected task and an unauthorized identity is denied. Confirm licensing and service billing separately: Copilot Studio usage does not demonstrate Azure OpenAI PTU consumption.',
  },
  16: {
    route: 'Azure and Fabric application', source: 'deployment',
    steps: [
      ['Prepare Fabric and application settings', 'Use the guide\'s Fabric workspace setup and required tenant/capacity permissions. Prepare the local Python, PowerShell, azd and Azure CLI tools. Review infra\\main.parameters.json and choose the scenario/runtime, network flavor and model route.'],
      ['Reuse approved capacity and provision', 'Set the approved existing Fabric workspace before provisioning to avoid automatic capacity creation. Select the intended subscription and environment; use a new capacity only with explicit purchasing approval.', 'azd auth login\naz login\nazd env new "<environment-name>"\nazd env set FABRIC_WORKSPACE_ID "<workspace-id>"\nazd up'],
      ['Build and install application images', 'From the repository root, run the separate API/frontend image stage.', '.\\infra\\scripts\\build\\build-and-push-acr.ps1'],
      ['Initialize the Fabric solution', 'Create/activate .venv and install the pinned post-provision requirements through approved feeds as described in the manual. Then run the build orchestrator and agent check. The default is retail; use its documented scenario option for insurance.', 'python infra\\scripts\\post-provision\\00_build_solution.py --from 01\npython infra\\scripts\\post-provision\\06_test_agent.py'],
      ['Configure delegated access and open the app', 'Complete SetupOBOAuthentication.md for the selected user-access route, including app registration, consent and connection settings. Open the frontend App Service Default domain and sign in as a permitted user.'],
    ],
    verify: 'Ask a known data question and reconcile the answer/chart with underlying tables. Test delegated access with another user; a working Fabric data agent is not proof that its model calls use the customer\'s PTUs.',
  },
  17: {
    route: 'Fabric operations solution', source: 'deployment',
    steps: [
      ['Prepare Fabric permissions and scope', 'Use the manual\'s Azure and Fabric prerequisites, Python, Azure CLI, azd and Bicep. Obtain an approved Fabric capacity/workspace and tenant permissions for the deploying identity. Define synthetic event scope and alert recipients.'],
      ['Configure reuse before provisioning', 'Create a new environment and set the approved existing capacity and workspace names. Review the manual\'s region, administrator and optional Event Hub reuse settings; do not default to buying capacity.', 'azd env new "<environment-name>"\nazd env set EXISTING_FABRIC_CAPACITY_NAME "<capacity-name>"\nazd env set FABRIC_WORKSPACE_NAME "<workspace-name>"'],
      ['Deploy both phases', 'Authenticate, select the approved subscription and run the Azure infrastructure plus Fabric setup workflow. Inspect Eventhouse, KQL database, Eventstream, dashboard and Activator results individually.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Complete data-agent setup', 'Open the Fabric workspace and follow FabricDataAgentGuide.md from Step 5 of the manual. If its preview setup fails, report that component as incomplete even if the dashboard works.'],
      ['Start bounded events and configure alerts', 'Follow EventSimulatorGuide.md for the separate simulator, with an agreed duration/rate. Use ActivatorGuide.md to enable only approved alerts. Inspect incoming events and dashboard refresh before testing the data agent.'],
    ],
    verify: 'Reconcile event counts and time windows, trigger one synthetic alert and check an agent answer against KQL results. Stop the simulator afterward; event volume is not model demand and Fabric costs are separate.',
  },
  19: {
    route: 'Aspire / Blazor application', source: 'deployment',
    steps: [
      ['Prepare the selected sample', 'Use the pinned guide\'s .NET/Aspire SDK, azd, Azure CLI and container tooling. Review AppHost configuration and the API\'s OpenCV-compatible base image. The Blazor path is distinct from console samples; review and pin external images/dependencies before deployment.'],
      ['Initialize from the AppHost', 'From the repository root, enter the AppHost directory and initialize azd. Choose Use code in the current directory, not a new remote template.', 'Set-Location srcBlazor\\AspireVideoAnalyserBlazor.AppHost\nazd init'],
      ['Configure and deploy', 'Review the generated configuration, model deployment and approved Azure subscription before continuing. Default model creation is not reuse of existing PTUs.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Open the frontend and check connectivity', 'Use deployment output to open the Container Apps/Aspire dashboard and webfrontend endpoint. Confirm API access, exact allowed CORS origin and model identity permissions. Do not enable anonymous dashboard access or wildcard origins as a fix.'],
      ['Analyze permitted media', 'Upload one short authorized video in Blazor, set the frame count and prompts, then submit analysis. Inspect the description, reported frames and representative image.'],
    ],
    verify: 'Compare the description with the full clip, including brief events between sampled frames. Confirm image-capable model routing; audio transcription and complete event detection are not provided by this sample.',
  },
  21: {
    route: 'Voice application - Bash workflow', source: 'deployment',
    steps: [
      ['Prepare the full toolchain', 'Use the linked prerequisites with a Bash-compatible shell (WSL/Git Bash on Windows), Terraform, azd, Azure CLI, containers, Python and Node. Review infra/terraform defaults and all three services in azure.yaml, including cardapi-mcp.'],
      ['Approve capacity and integration choices', 'Price and reduce the model/hosting defaults before provisioning. Select the intended speech/reasoning path, identity and network settings. Start with browser audio: a phone number is required only for a separately approved PSTN test.'],
      ['Deploy from the repository root', 'In Bash, sign in to both CLIs and select the approved subscription. azd invokes Terraform, provisioning hooks and container deployment; require each service to become healthy.', 'azd auth login\naz login\naz account set --subscription "<subscription-id>"\nazd up'],
      ['Open and configure a browser scenario', 'Open the frontend URL, allow microphone access and use synthetic demo profile data only. In Agent Builder select one agent/template, configure a narrow scenario and expose only approved tools. Review authentication before sharing the endpoint.'],
      ['Add telephony only if approved', 'For a phone pilot, follow the separately linked number-setup guide to obtain/configure the ACS number and call/event routing. Number purchase and recurring charges require separate approval; verify consent and human handoff first.'],
    ],
    verify: 'Run realistic audio with interruptions, silence, noise and out-of-scope questions. Measure latency and handoff, inspect tool permissions and verify the actual model route. No calls or performance measurements are established by source review.',
  },
  22: {
    route: 'Isolated training environment', source: 'workshop-setup',
    steps: [
      ['Verify isolation before setup', 'Use a disposable environment with synthetic data and no production connectivity. The workshop intentionally contains vulnerable servers. Prepare the pinned prerequisites, including Python 3.10+, uv and an MCP-capable editor; later Azure camps need their own permissions/budget.'],
      ['Prepare Base Camp', 'From the repository root, enter camps\\base-camp and use its shared uv environment. Review package feeds first; do not start any vulnerable server on a shared/public host.', 'Set-Location camps\\base-camp\nuv sync'],
      ['Run the local exercise', 'Use the linked Base Camp Setup instructions to start the vulnerable server and its provided test in separate terminals inside the isolated environment. Keep the exercise target local and use only its synthetic fixtures.'],
      ['Apply the secure counterpart', 'Stop the vulnerable process, configure secure-server from its .env.example as documented, start it and run the supplied secure validation. Keep tokens in the isolated environment, not in source or reports.'],
      ['Continue and close deliberately', 'Proceed camp by camp using each README and its Azure setup instructions. Record the before/after control result; stop local processes and have the teardown owner remove only the authorized exercise resources when the session ends.'],
    ],
    verify: 'Show that the intended attack fails after the control, then confirm no vulnerable endpoint or billable exercise resource remains. Workshop completion is training evidence, not production security certification or a PTU workload.',
  },
};
