targetScope = 'resourceGroup'

param endpoints array
param location string = 'eastus2'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' existing = {
  name: 'vnet-ptu-bundle'
}

resource privateEndpoints 'Microsoft.Network/privateEndpoints@2024-05-01' = [for endpoint in endpoints: {
  name: endpoint.name
  location: location
  tags: {
    workload: 'accelerator-eval'
    owner: 'parth'
    environment: 'mcaps-nonprod'
    accelerator: endpoint.app
    protected: 'false'
  }
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/snet-private-endpoints'
    }
    privateLinkServiceConnections: [
      {
        name: endpoint.name
        properties: {
          privateLinkServiceId: endpoint.resourceId
          groupIds: [endpoint.groupId]
        }
      }
    ]
  }
}]

resource dnsGroups 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = [for (endpoint, i) in endpoints: {
  parent: privateEndpoints[i]
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [for (zoneName, index) in (endpoint.?zoneNames ?? [endpoint.zoneName]): {
        name: contains(endpoint, 'zoneNames') ? 'service-${index}' : 'service'
        properties: {
          privateDnsZoneId: resourceId('Microsoft.Network/privateDnsZones', zoneName)
        }
    }]
  }
}]

output privateEndpointIds array = [for (endpoint, i) in endpoints: privateEndpoints[i].id]
