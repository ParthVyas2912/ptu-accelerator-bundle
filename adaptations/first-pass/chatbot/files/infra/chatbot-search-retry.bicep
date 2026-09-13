// One bounded retry of the originally approved East US 2 envelope.
// No model, Cosmos, network, or existing shared-resource changes.
targetScope = 'resourceGroup'
module search './bicep/modules/ai/ai-search.bicep' = {
  name: 'ptu-chatbot-search-resource'
  params: {
    solutionName: 'ccptu1feb0911'
    location: 'eastus2'
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
  }
}
output resourceId string = search.outputs.resourceId
output endpoint string = search.outputs.endpoint
