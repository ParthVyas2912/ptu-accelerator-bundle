targetScope = 'resourceGroup'
param principalIds array
resource registry 'Microsoft.ContainerRegistry/registries@2025-04-01' existing = {
  name: 'acrptubundle7d804f70'
}
resource pullRoles 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for principal in principalIds: {
  name: guid(registry.id, principal, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: registry
  properties: {
    principalId: principal
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  }
}]
