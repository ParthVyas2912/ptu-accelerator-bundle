targetScope = 'resourceGroup'
param principalIds array
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: 'acrptubundle7d804f70'
}
resource pull 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for principal in principalIds: {
  scope: acr
  name: guid(acr.id, principal, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  properties: {
    principalId: principal
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  }
}]
