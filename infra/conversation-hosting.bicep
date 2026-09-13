// CKM component-only hosting on the parent's existing Consumption platform.
// No data/model endpoints, secrets, PaaS services, or networking resources.
// Historical bootstrap only. Durable read-only serving now uses Set-ConversationServing.ps1;
// do not redeploy this template over the verified serving configuration.
targetScope = 'resourceGroup'

param environmentId string
param registryServer string
param identityResourceId string
param identityClientId string
param clientCidr string
param apiImage string
param uiImage string

var tags = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'conversation'
  protected: 'false'
  phase: 'component-only'
}
var userIdentity = {
  type: 'UserAssigned'
  userAssignedIdentities: {
    '${identityResourceId}': {}
  }
}
var registries = [
  {
    server: registryServer
    identity: identityResourceId
  }
]

resource api 'Microsoft.App/containerApps@2025-01-01' = {
  name: 'ca-ptu-conversation-api'
  location: 'eastus2'
  tags: tags
  identity: userIdentity
  properties: {
    managedEnvironmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: registries
      ingress: {
        external: false
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_CLIENT_ID', value: identityClientId }
            { name: 'APP_ENV', value: 'development' }
            { name: 'SOLUTION_SUFFIX', value: 'ptu-conversation' }
            { name: 'ENABLE_AUTO_PIPELINE_SELECTION', value: 'false' }
            { name: 'ENABLE_EXTERNAL_DATA_SOURCES', value: 'false' }
            { name: 'MAX_JSON_DOCUMENTS_PER_UPLOAD', value: '3' }
            { name: 'MAX_CONCURRENT_UPLOADS', value: '1' }
            { name: 'AZURE_FOUNDRY_ENDPOINT', value: '' }
            { name: 'AZURE_OPENAI_ENDPOINT', value: '' }
            { name: 'AZURE_AI_AGENT_ENDPOINT', value: '' }
            { name: 'AZURE_SEARCH_ENDPOINT', value: '' }
            { name: 'AZURE_SQL_SERVER', value: '' }
            { name: 'AZURE_STORAGE_ACCOUNT', value: '' }
            { name: 'AZURE_COSMOS_ENDPOINT', value: '' }
            { name: 'AZURE_CONTENT_UNDERSTANDING_ENDPOINT', value: '' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '5'
              }
            }
          }
        ]
      }
    }
  }
}

resource ui 'Microsoft.App/containerApps@2025-01-01' = {
  name: 'ca-ptu-conversation-ui'
  location: 'eastus2'
  tags: tags
  identity: userIdentity
  properties: {
    managedEnvironmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: registries
      ingress: {
        external: true
        targetPort: 80
        transport: 'auto'
        allowInsecure: false
        // Applied atomically with external ingress, never after public exposure.
        ipSecurityRestrictions: [
          {
            name: 'approved-lab-client'
            description: 'Single evaluator CIDR from lab-ingress.json'
            action: 'Allow'
            ipAddressRange: clientCidr
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'ui'
          image: uiImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            { name: 'APP_API_BASE_URL', value: '/api' }
            { name: 'BACKEND_API_HOST', value: api.properties.configuration.ingress.fqdn }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '5'
              }
            }
          }
        ]
      }
    }
  }
}

output apiResourceId string = api.id
output uiResourceId string = ui.id
output apiInternalFqdn string = api.properties.configuration.ingress.fqdn
output uiFqdn string = ui.properties.configuration.ingress.fqdn
output allowedClientCidr string = clientCidr
output phase string = 'component-only-no-Azure-data-or-model-endpoints'
