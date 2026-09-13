targetScope = 'resourceGroup'

param location string = 'eastus2'
param environmentId string
param registryServer string
param backendIdentityId string
param backendClientId string
param frontendIdentityId string
param clientCidr string
param backendImage string
param frontendImage string
param deployFrontend bool = true
@minValue(0)
@maxValue(1)
param backendMinReplicas int = 1

var rules = [
  {
    name: 'approved-single-client'
    description: 'Parent-approved MCAPS evaluator client only'
    action: 'Allow'
    ipAddressRange: clientCidr
  }
]
var backendEnv = [
  { name: 'APP_ENV', value: 'prod' }
  { name: 'AZURE_CLIENT_ID', value: backendClientId }
  { name: 'AI_PROJECT_ENDPOINT', value: 'https://edcfoundryhack01.services.ai.azure.com/api/projects/edc-hack-proj' }
  { name: 'COSMOSDB_ENDPOINT', value: 'https://cosmos-ptu-modernize-eus20911.documents.azure.com:443/' }
  { name: 'COSMOSDB_DATABASE', value: 'ptu-modernize' }
  { name: 'COSMOSDB_BATCH_CONTAINER', value: 'ptu-modernize-batches' }
  { name: 'COSMOSDB_FILE_CONTAINER', value: 'ptu-modernize-files' }
  { name: 'COSMOSDB_LOG_CONTAINER', value: 'ptu-modernize-logs' }
  { name: 'AZURE_BLOB_ACCOUNT_NAME', value: 'stptumodernize0911pv' }
  { name: 'AZURE_BLOB_CONTAINER_NAME', value: 'ptu-modernize-files' }
  { name: 'MIGRATOR_AGENT_MODEL_DEPLOY', value: 'gpt-5.1' }
  { name: 'PICKER_AGENT_MODEL_DEPLOY', value: 'gpt-5.1' }
  { name: 'SYNTAX_CHECKER_AGENT_MODEL_DEPLOY', value: 'gpt-5.1' }
  { name: 'FIXER_AGENT_MODEL_DEPLOY', value: 'gpt-5.1' }
  { name: 'SEMANTIC_VERIFIER_AGENT_MODEL_DEPLOY', value: 'gpt-5.1' }
]

resource backend 'Microsoft.App/containerApps@2025-01-01' = {
  name: 'ca-ptu-modernize-api'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${backendIdentityId}': {} }
  }
  properties: {
    managedEnvironmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [{ server: registryServer, identity: backendIdentityId }]
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
        ipSecurityRestrictions: rules
      }
    }
    template: {
      containers: [{
        name: 'api'
        image: backendImage
        env: backendEnv
        resources: { cpu: json('0.5'), memory: '1Gi' }
      }]
      scale: {
        minReplicas: backendMinReplicas
        maxReplicas: 1
        rules: [{ name: 'one-client-http', http: { metadata: { concurrentRequests: '1' } } }]
      }
    }
  }
}

resource frontend 'Microsoft.App/containerApps@2025-01-01' = if (deployFrontend) {
  name: 'ca-ptu-modernize-ui'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${frontendIdentityId}': {} }
  }
  properties: {
    managedEnvironmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [{ server: registryServer, identity: frontendIdentityId }]
      ingress: {
        external: true
        targetPort: 3000
        transport: 'auto'
        allowInsecure: false
        ipSecurityRestrictions: rules
      }
    }
    template: {
      containers: [{
        name: 'ui'
        image: frontendImage
        env: [
          { name: 'API_URL', value: 'https://${backend.properties.configuration.ingress.fqdn}' }
          { name: 'ENABLE_AUTH', value: 'false' }
        ]
        resources: { cpu: json('0.25'), memory: '0.5Gi' }
      }]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [{ name: 'one-client-http', http: { metadata: { concurrentRequests: '1' } } }]
      }
    }
  }
}
output apiUrl string = 'https://${backend.properties.configuration.ingress.fqdn}'
output uiUrl string = deployFrontend ? 'https://${frontend.properties.configuration.ingress.fqdn}' : ''
output backendId string = backend.id
output frontendId string = deployFrontend ? frontend.id : ''
