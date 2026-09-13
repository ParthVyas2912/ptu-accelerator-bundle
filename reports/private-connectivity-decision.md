# MCAPS private connectivity decision

The MACAE native application reached a real Cosmos data-plane denial while onboarding: the new Cosmos and Blob resources have public network access disabled. The app agent recorded policy-modification events. Entra permissions do not override a service firewall or create a private network route.

The corrective path is **private endpoints plus in-VNet application compute**, not enabling public access, adding policy exemptions, exposing credentials, or treating a failed model-independent prerequisite as successful AI functionality.

## Approved shared platform

- Resource group: `rg-ptu-bundle-platform`, East US 2, MCAPS subscription `1feb53b2-854a-4ea7-b5a6-709b7d804f70`.
- Dedicated VNet: `vnet-ptu-bundle`, `10.246.0.0/16`; no peering or modification to existing app networks.
- Subnets: Container Apps `10.246.0.0/23`; private endpoints `10.246.2.0/24`.
- Container Apps environment: `cae-ptu-bundle`, Consumption workload profile only, no dedicated workers or GPUs.
- Registry: `acrptubundle7d804f70`, Basic; admin credentials disabled.
- Private endpoints/DNS: connect only approved new lab data services; keep their public access disabled.
- Application identity: per-app managed identity, scoped data access; any approved shared Foundry access uses documented Entra roles, not model/network changes.
- Public demo endpoints: authentication or a single-client IP restriction must be present before model-consuming operations are reachable. Local egress can change; the evidence file records the observed CIDR and timestamp.
- Scaling: maximum one replica per service, minimum zero where compatible. Always-on processing workers must have explicit pause/restart instructions and their continuing cost disclosed.

The infrastructure source is `infra\lab-network.bicep`. Deployment outputs, endpoint connection approval, DNS resolution **from inside the VNet**, and real data-plane access must be verified before calling this path functional. Template validation or a provisioned environment alone is insufficient.

## Observed verification

The shared platform deployment succeeded. From a real Container Apps replica in the new VNet, an authenticated Azure management execution returned:

| Target | Resolved address | Anonymous HTTPS response |
|---|---|---|
| MACAE Blob service | 10.246.2.6 | 400 |
| MACAE Cosmos service | 10.246.2.4 | 401 |

Both addresses are within the private-endpoint subnet. These results establish private DNS and HTTPS reachability; **they do not establish authorized application data access**. Each app must still prove its managed identity and workflow. No model requests were made by this probe.

The temporary public probe had an explicit single-client CIDR restriction, but the coordinator's HTTP request returned `403 RBAC: access denied`, including on an IPv4 retry. The rule was not widened. The result was collected instead through authorized `az containerapp exec`. Public browser access must therefore be evaluated separately, not inferred from the successful cloud-side check.

After recording the result, the diagnostic ingress was disabled and its active revision deactivated. It is not a demo app and should not remain as an always-on charge. Evidence: `evidence\preflight\private-network-probe-result.json` and `private-network-probe-exec.txt`.

## Additional cost exposure

Private endpoints, DNS zones/queries, Basic ACR, networking and actual Container Apps compute are additional Azure charges; none are covered by PTUs. The initial native-only estimates therefore do not represent the final network-compliant deployment cost. No new PTUs, reservations, dedicated compute, VPN gateway or Bastion host is part of this platform.

The exact active resource inventory and per-app allocation belong in the final report. A platform shared by several apps should not be counted once per app in the portfolio total.

The Azure Retail Prices API returned **USD $0.01 per private-endpoint hour** for the Global Standard Private Endpoint meter. This is a list-price reference, not the subscription's invoice; data processing, DNS, registry, networking and compute remain additional. The raw price response is retained under `evidence\preflight\private-link-retail-prices.json`.

## Important DND boundary

This implementation is in **MCAPS**, not the JDCP/DND hub-and-spoke tenant. Its Azure-provided DNS and newly isolated network permit lab-local private DNS zones.

For a future JDCP deployment, follow the current JDCP Cloud Ops private-endpoint SOP: integrate with centrally owned hub DNS, obtain required hub-zone permissions and approved network flows, and validate from the relevant in-VNet host. Do **not** copy this MCAPS-local DNS ownership arrangement into a JDCP spoke. Residency, classification, support ownership and authorization-to-operate remain separate production gates.
