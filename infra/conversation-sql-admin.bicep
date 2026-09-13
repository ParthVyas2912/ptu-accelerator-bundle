param adminId string
param adminName string
@allowed(['User', 'Application'])
param adminType string

resource server 'Microsoft.Sql/servers@2025-01-01' = {
  name: 'sql-ptu-conversation-7d804f70'
  location: 'canadacentral'
  tags: {
    workload: 'accelerator-eval'
    owner: 'parth'
    environment: 'mcaps-nonprod'
    accelerator: 'conversation'
    protected: 'false'
  }
  properties: {
    version: '12.0'
    publicNetworkAccess: 'Disabled'
    minimalTlsVersion: '1.2'
    administrators: {
      administratorType: 'ActiveDirectory'
      azureADOnlyAuthentication: true
      principalType: adminType
      login: adminName
      sid: adminId
      tenantId: subscription().tenantId
    }
  }
}
