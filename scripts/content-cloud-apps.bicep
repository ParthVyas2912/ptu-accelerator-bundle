targetScope = 'resourceGroup'
@allowed(['api', 'processor', 'workflow', 'web'])
param services array = ['api']
param imageRevision string = '659eaa1-scope-r1'
param apiImageRevision string = '659eaa1-scope-r1'
param processorImageRevision string = '659eaa1-scope-r2'
param warmForTest bool = false
param pauseWorkers bool = false
var settings = {
  api: { cpu: json('0.25'), memory: '0.5Gi', port: 80 }
  processor: { cpu: json('1.0'), memory: '2Gi', port: 8080 }
  workflow: { cpu: json('0.5'), memory: '1Gi', port: 8080 }
  web: { cpu: json('0.25'), memory: '0.5Gi', port: 3000 }
}
var imageVersions = {
  api: apiImageRevision
  processor: processorImageRevision
  workflow: imageRevision
  web: '659eaa1'
}
var queues = {
  api: []
  processor: ['content-pipeline-extract-queue', 'content-pipeline-map-queue', 'content-pipeline-evaluate-queue', 'content-pipeline-save-queue']
  workflow: ['claim-process-queue']
  web: []
}
resource identities 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = [for service in services: {
  name: 'id-ptu-content-${service}'
}]
var commonEnv = [
  { name: 'CONTENT_CONFIGURATION_REVISION', value: 'canonical-schemas-v1' }
  { name: 'APP_ENV', value: 'prod' }
  { name: 'APP_CONFIG_ENDPOINT', value: 'https://appcs-ptuv-content-260911.azconfig.io' }
  { name: 'APP_CONFIGURATION_URL', value: 'https://appcs-ptuv-content-260911.azconfig.io' }
  { name: 'APP_LOGGING_LEVEL', value: 'WARNING' }
  { name: 'OTEL_SDK_DISABLED', value: 'true' }
  { name: 'CONCURRENT_WORKERS', value: '1' }
  { name: 'MAX_RECEIVE_ATTEMPTS', value: '1' }
  { name: 'VISIBILITY_TIMEOUT_MINUTES', value: '15' }
  { name: 'MESSAGE_TIMEOUT_MINUTES', value: '20' }
  { name: 'RETRY_VISIBILITY_DELAY_SECONDS', value: '30' }
]
resource apps 'Microsoft.App/containerApps@2025-01-01' = [for (service, i) in services: {
  name: 'ca-ptu-content-${service}'
  location: 'eastus2'
  tags: { workload: 'accelerator-eval', owner: 'parth', environment: 'mcaps-nonprod', accelerator: 'content', protected: 'false' }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identities[i].id}': {} }
  }
  properties: {
    managedEnvironmentId: resourceId('rg-ptu-bundle-platform', 'Microsoft.App/managedEnvironments', 'cae-ptu-bundle')
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Multiple'
      maxInactiveRevisions: 100
      registries: [{
        server: 'acrptubundle7d804f70.azurecr.io'
        identity: identities[i].id
      }]
      ingress: contains(['api', 'web'], service) ? {
        external: false
        targetPort: settings[service].port
        transport: 'http'
        allowInsecure: true
      } : null
    }
    template: {
      containers: [{
        name: service
        image: service == 'web' ? 'acrptubundle7d804f70.azurecr.io/content/official-web:659eaa1' : 'acrptubundle7d804f70.azurecr.io/content/eval-${service}:${imageVersions[service]}'
        resources: { cpu: settings[service].cpu, memory: settings[service].memory }
        env: concat(commonEnv, [
          { name: 'AZURE_CLIENT_ID', value: identities[i].properties.clientId }
          { name: 'CONTENT_SERVICE', value: service }
        ], service == 'web' ? [
          { name: 'APP_API_BASE_URL', value: 'http://ca-ptu-content-api' }
          { name: 'APP_AUTH_ENABLED', value: 'false' }
          { name: 'APP_CONSOLE_LOG_ENABLED', value: 'false' }
        ] : [])
        probes: service == 'api' ? [{
          type: 'Startup'
          httpGet: { path: '/startup', port: 80 }
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
        }, {
          type: 'Readiness'
          httpGet: { path: '/health', port: 80 }
          periodSeconds: 10
          timeoutSeconds: 5
        }] : []
      }]
      scale: {
        minReplicas: warmForTest ? 1 : 0
        maxReplicas: 1
        cooldownPeriod: pauseWorkers ? 30 : 1800
        pollingInterval: 30
        rules: contains(['api', 'web'], service) ? [{
          name: 'http'
          http: { metadata: { concurrentRequests: '1' } }
        }] : (pauseWorkers ? [] : map(queues[service], queue => {
          name: take(queue, 63)
          custom: {
            type: 'azure-queue'
            identity: identities[i].id
            metadata: {
              accountName: 'stptuvcontent260911'
              queueName: queue
              queueLength: '1'
            }
          }
        }))
      }
    }
  }
}]
output appEndpoints array = [for (service, i) in services: {
  name: apps[i].name
  id: apps[i].id
  fqdn: contains(['api', 'web'], service) ? apps[i].properties.configuration.ingress.fqdn : ''
}]
