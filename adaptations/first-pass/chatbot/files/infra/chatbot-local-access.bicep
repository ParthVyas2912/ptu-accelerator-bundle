// Deploy only the already-approved local operator roles while Search is blocked.
// Uses the native deterministic names so the later complete deployment converges.
targetScope = 'resourceGroup'

module roles './bicep/modules/identity/role-assignments.bicep' = {
  name: 'ptu-chatbot-local-access'
  params: {
    solutionName: 'ccptu1feb0911'
    aiFoundryResourceId: resourceId('Microsoft.CognitiveServices/accounts', 'aif-ccptu1feb0911')
    cosmosDbAccountName: 'cosmos-ccptu1feb0911'
    deployerPrincipalId: '87ccaa4c-8da9-4d6a-a626-d0da9b2e25ed'
    appServicePrincipalIds: {
      chatBackendApp: ''
      chatFrontendApp: ''
      scenarioBackendApp: ''
      scenarioFrontendApp: ''
    }
  }
}
