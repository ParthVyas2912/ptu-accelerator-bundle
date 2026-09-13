targetScope = 'resourceGroup'

@allowed(['canadacentral', 'canadaeast', 'eastus', 'westus2', 'centralus'])
param location string = 'canadacentral'

// Use the native full-config module so PNA is disabled on the initial PUT.
module search './bicep/modules/ai/ai-search-identity.bicep' = {
  name: 'ptu-chatbot-search-private-resource'
  params: {
    name: 'srch-ccptu1feb0911'
    location: location
    tags: {
      workload: 'accelerator-eval'
      accelerator: 'chatbot'
      environment: 'mcaps-nonprod'
      owner: 'parth'
      protected: 'false'
    }
    skuName: 'basic'
    replicaCount: 1
    partitionCount: 1
    semanticSearch: 'free'
    disableLocalAuth: true
    publicNetworkAccess: 'Disabled'
  }
}

output resourceId string = resourceId('Microsoft.Search/searchServices', 'srch-ccptu1feb0911')
output endpoint string = 'https://srch-ccptu1feb0911.search.windows.net'
output principalId string = search.outputs.systemAssignedMIPrincipalId
