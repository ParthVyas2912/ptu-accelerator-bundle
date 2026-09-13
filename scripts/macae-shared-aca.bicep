// Prepared only. Parent supplies/owns environment, registry, identity, networking.
// Application logic and official image commands remain unchanged except the
// explicitly disclosed backend evaluation metering entrypoint.
targetScope = 'resourceGroup'

param location string = 'eastus2'
param managedEnvironmentId string
param runtimeIdentityResourceId string
param runtimeIdentityClientId string
param registryServer string
param frontendSiteName string
@description('Digest-pinned registry references after parent-authorized push.')
param backendImage string
param mcpImage string
param frontendImage string
@description('Mandatory single-client IPv4 /32 from current lab-ingress evidence.')
param clientCidr string
@description('Set true only after parent configures actual ACA Entra authentication.')
@allowed(['false', 'true'])
param frontendAuthEnabled string = 'false'
@minValue(0)
@maxValue(1)
param minReplicas int = 0
@description('Remain false until private dependencies and durable ledger verified.')
param liveRequestsEnabled bool = false

var foundryProject = 'https://ptumacae7d804f70.services.ai.azure.com/api/projects/ptu-macae-project'
var tags = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'macae'
  protected: 'false'
}
var backendSettings = {
  APP_ENV: 'prod'
  AZURE_CLIENT_ID: runtimeIdentityClientId
  AZURE_TENANT_ID: 'a600acd0-3028-4689-8402-3b471d7d924d'
  AZURE_AI_SUBSCRIPTION_ID: subscription().subscriptionId
  AZURE_AI_RESOURCE_GROUP: 'rg-ptu-macae-demo'
  AZURE_AI_PROJECT_NAME: 'ptu-macae-project'
  FRONTEND_SITE_NAME: frontendSiteName
  AZURE_AI_AGENT_ENDPOINT: foundryProject
  AZURE_AI_PROJECT_ENDPOINT: foundryProject
  AZURE_OPENAI_ENDPOINT: 'https://ptumacae7d804f70.openai.azure.com/'
  AZURE_OPENAI_DEPLOYMENT_NAME: 'gpt-5.4-mini'
  AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME: 'gpt-5.4-mini'
  AZURE_OPENAI_RAI_DEPLOYMENT_NAME: 'gpt-5.4'
  AZURE_OPENAI_API_VERSION: '2024-12-01-preview'
  ORCHESTRATOR_MODEL_NAME: 'gpt-5.4-mini'
  // Leading JSON whitespace prevents ARM from treating the copied JSON value
  // as a template expression. Native json.loads accepts it unchanged.
  SUPPORTED_MODELS: ' ["gpt-5.4-mini","gpt-5.4"]'
  COSMOSDB_ENDPOINT: 'https://ptu-macae-7d804f70-cosmos.documents.azure.com:443/'
  COSMOSDB_DATABASE: 'ptu-macae'
  COSMOSDB_CONTAINER: 'memory'
  MCP_SERVER_ENDPOINT: 'http://127.0.0.1:9000/mcp'
  MCP_SERVER_NAME: 'MacaeMcpServer'
  MCP_SERVER_DESCRIPTION: 'MACAE isolated native MCP tools'
  AZURE_AI_SEARCH_ENDPOINT: 'https://ptu-macae-7d804f70-srch.search.windows.net'
  AZURE_STORAGE_BLOB_URL: 'https://ptumacae7d804f70st.blob.${environment().suffixes.storage}/'
  AZURE_BASIC_LOGGING_LEVEL: 'WARNING'
  AZURE_PACKAGE_LOGGING_LEVEL: 'WARNING'
  MACAE_STATE_DIR: '/tmp/macae-state'
  MACAE_EVIDENCE_DIR: '/tmp/macae-evidence'
  // ARM string(bool) returns "True"/"False"; the evaluation gate expects lowercase.
  MACAE_LIVE_REQUESTS_ENABLED: liveRequestsEnabled ? 'true' : 'false'
}

resource app 'Microsoft.App/containerApps@2025-01-01' = {
  name: 'ptu-macae'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${runtimeIdentityResourceId}': {} }
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [{
        server: registryServer
        identity: runtimeIdentityResourceId
      }]
      ingress: {
        external: true
        targetPort: 3000
        transport: 'auto'
        allowInsecure: false
        ipSecurityRestrictions: [{
          name: 'lab-client-only'
          ipAddressRange: clientCidr
          action: 'Allow'
        }]
      }
    }
    template: {
      scale: { minReplicas: minReplicas, maxReplicas: 1 }
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: [
            { name: 'PROXY_API_REQUESTS', value: 'true' }
            { name: 'BACKEND_API_URL', value: 'http://127.0.0.1:8000' }
            { name: 'AUTH_ENABLED', value: frontendAuthEnabled }
          ]
          probes: [{
            type: 'Liveness'
            httpGet: { path: '/health', port: 3000 }
            initialDelaySeconds: 30
            periodSeconds: 15
          }]
        }
        {
          name: 'backend'
          image: backendImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [for setting in items(backendSettings): { name: setting.key, value: setting.value }]
          probes: [
            {
              type: 'Startup'
              httpGet: { path: '/healthz', port: 8000 }
              periodSeconds: 5
              failureThreshold: 60
            }
            {
              type: 'Liveness'
              httpGet: { path: '/healthz', port: 8000 }
              periodSeconds: 15
            }
            {
              type: 'Readiness'
              httpGet: { path: '/healthz', port: 8000 }
              periodSeconds: 10
            }
          ]
        }
        {
          name: 'mcp'
          image: mcpImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: [
            { name: 'BACKEND_URL', value: 'http://127.0.0.1:8000' }
            { name: 'ENABLE_AUTH', value: 'false' }
            // Native uv run otherwise rebuilds the project and fetches hatchling.
            { name: 'UV_NO_SYNC', value: 'true' }
            { name: 'FASTMCP_ENABLE_TELEMETRY', value: 'false' }
          ]
          // Official /health currently returns 404. Do not copy its bad HTTP probe.
          probes: [
            { type: 'Liveness', tcpSocket: { port: 9000 }, initialDelaySeconds: 30, periodSeconds: 15 }
            { type: 'Readiness', tcpSocket: { port: 9000 }, initialDelaySeconds: 10, periodSeconds: 10 }
          ]
        }
      ]
    }
  }
}
output appResourceId string = app.id
output frontendUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
