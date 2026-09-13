@description('Name of the informational stakeholder site.')
param siteName string = 'ptu-bundle-portal'

@description('Static Web Apps supports a limited set of regions. Public-safe content only.')
param location string = 'eastus2'

param tags object = {
  workload: 'accelerator-eval'
  owner: 'parth'
  environment: 'mcaps-nonprod'
  accelerator: 'stakeholder-site'
  protected: 'false'
}

resource site 'Microsoft.Web/staticSites@2023-12-01' = {
  name: siteName
  location: location
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    provider: 'Custom'
    allowConfigFileUpdates: true
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
}

output hostname string = site.properties.defaultHostname
output resourceId string = site.id
