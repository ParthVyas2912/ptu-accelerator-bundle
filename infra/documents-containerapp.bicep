// Approved hosting adaptation only: original DKM images/services, no new data/model services.
@allowed(['backend', 'kernelmemory', 'frontend'])
param component string
param image string
param environmentId string
param runtimeIdentityId string
param runtimeClientId string
param registryServer string
param clientCidr string
@allowed([0, 1])
param minimumReplicas int = 0
@description('Explicit lab-only SDK retry control. Empty preserves repository defaults.')
@allowed(['', '0', '1', '2', '3'])
param evaluationMaxModelRetries string = ''

var settings = {
  backend: { name: 'ca-dkm-api', memory: '2Gi', port: 9001 }
  kernelmemory: { name: 'ca-dkm-kernel', memory: '2Gi', port: 9001 }
  frontend: { name: 'ca-dkm-web', memory: '2Gi', port: 5900 }
}
var selected = settings[component]
var publicIngress = component == 'frontend'
var appConfigEndpoint = 'https://appcs-dkmeval0911a.azconfig.io'
var commonEnv = [
  { name: 'AZURE_CLIENT_ID', value: runtimeClientId }
  { name: 'ConnectionStrings__AppConfig', value: appConfigEndpoint }
  { name: 'Logging__LogLevel__Default', value: 'Information' }
  { name: 'Logging__LogLevel__Microsoft.AspNetCore', value: 'Warning' }
]
var frontEnv = [
  { name: 'VITE_API_ENDPOINT', value: '/backend' }
  { name: 'BACKEND_PROXY_TARGET', value: 'http://ca-dkm-api' }
  { name: 'DISABLE_AUTH', value: 'true' }
  { name: 'VITE_ENABLE_UPLOAD_BUTTON', value: 'true' }
]
var kernelEnv = [
  { name: 'KernelMemory__Services__AzureOpenAIEmbedding__MaxRetries', value: '0' }
  { name: 'KernelMemory__Services__AzureOpenAIText__MaxRetries', value: '0' }
  { name: 'KernelMemory__Services__AzureQueues__MaxRetriesBeforePoisonQueue', value: '1' }
]
var evaluationEnv = empty(evaluationMaxModelRetries) ? [] : [
  { name: 'DKM_EVAL_MAX_MODEL_RETRIES', value: evaluationMaxModelRetries }
]

resource app 'Microsoft.App/containerApps@2025-01-01' = {
  name: selected.name
  location: 'eastus2'
  tags: {
    workload: 'accelerator-eval'
    accelerator: 'dkm'
    environment: 'mcaps-nonprod'
    owner: 'parth'
    hostingAdaptation: 'original-dkm-services-on-shared-consumption-aca'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${runtimeIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [
        { server: registryServer, identity: runtimeIdentityId }
      ]
      ingress: {
        external: publicIngress
        targetPort: selected.port
        transport: 'http'
        allowInsecure: !publicIngress
        ipSecurityRestrictions: publicIngress ? [
          {
            name: 'lab-client-only'
            description: 'Explicit approved lab client; all other client IPs denied'
            action: 'Allow'
            ipAddressRange: clientCidr
          }
        ] : []
      }
    }
    template: {
      containers: [
        {
          name: component
          image: image
          env: publicIngress ? frontEnv : concat(commonEnv, component == 'kernelmemory' ? kernelEnv : [], evaluationEnv)
          resources: {
            cpu: json('1.0')
            memory: selected.memory
          }
          probes: [
            {
              type: 'Startup'
              tcpSocket: { port: selected.port }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 3
              failureThreshold: 30
            }
            {
              type: 'Readiness'
              tcpSocket: { port: selected.port }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 3
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minimumReplicas
        maxReplicas: 1
      }
    }
  }
}

output resourceId string = app.id
output fqdn string = app.properties.configuration.ingress.fqdn
