targetScope = 'resourceGroup'
param appName string
param image string
param targetPort int
param cpu string = '0.5'
param memory string = '1Gi'
param external bool = false
param minimumReplicas int = 0
param clientCidr string
param environmentVariables array = []

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: 'mi-${appName}'
}
resource environment 'Microsoft.App/managedEnvironments@2025-01-01' existing = {
  name: 'cae-ptu-bundle'
  scope: resourceGroup('rg-ptu-bundle-platform')
}
resource app 'Microsoft.App/containerApps@2025-01-01' = {
  name: appName
  location: 'eastus2'
  tags: {
    workload: 'accelerator-eval'
    accelerator: 'chatbot'
    environment: 'mcaps-nonprod'
    owner: 'parth'
    protected: 'false'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [{
        server: 'acrptubundle7d804f70.azurecr.io'
        identity: identity.id
      }]
      ingress: {
        external: external
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
        ipSecurityRestrictions: external ? [{
          name: 'approved-client'
          description: 'Parent-approved single client; deny all other external sources.'
          action: 'Allow'
          ipAddressRange: clientCidr
        }] : []
      }
    }
    template: {
      containers: [{
        name: appName
        image: image
        env: concat([
          { name: 'APP_ENV', value: 'prod' }
          { name: 'AZURE_CLIENT_ID', value: identity.properties.clientId }
          { name: 'DEPLOYMENT_SCENARIO', value: 'ecommerce' }
          { name: 'PYTHON_DOTENV_DISABLED', value: '1' }
          { name: 'COSMOS_DB_ENDPOINT', value: 'https://cosmos-ccptu1feb0911.documents.azure.com:443/' }
          { name: 'COSMOS_DB_DATABASE_NAME', value: 'ecommerce_db' }
          { name: 'AZURE_COSMOSDB_DATABASE', value: 'ecommerce_db' }
        ], environmentVariables)
        resources: {
          cpu: json(cpu)
          memory: memory
        }
        probes: [
          {
            type: 'Startup'
            httpGet: { path: targetPort == 80 ? '/' : '/health', port: targetPort }
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 30
            timeoutSeconds: 5
          }
          {
            type: 'Readiness'
            httpGet: { path: targetPort == 80 ? '/' : '/health', port: targetPort }
            periodSeconds: 15
            failureThreshold: 3
            timeoutSeconds: 5
          }
          {
            type: 'Liveness'
            httpGet: { path: targetPort == 80 ? '/' : '/health', port: targetPort }
            initialDelaySeconds: 30
            periodSeconds: 30
            failureThreshold: 3
            timeoutSeconds: 5
          }
        ]
      }]
      scale: {
        minReplicas: minimumReplicas
        maxReplicas: 1
        rules: [{
          name: 'bounded-http'
          http: { metadata: { concurrentRequests: '5' } }
        }]
      }
    }
  }
}
output fqdn string = app.properties.configuration.ingress.fqdn
output resourceId string = app.id
output latestRevision string = app.properties.latestRevisionName
