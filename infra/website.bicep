@description('Name of the informational stakeholder site.')
param siteName string = 'ptu-bundle-portal'

@description('Static Web Apps supports a limited set of regions. Public-safe content only.')
param location string = 'eastus2'

@description('Optional branded addresses added alongside the auto-generated default hostname, which Azure assigns randomly and which cannot be renamed or removed. Free tier allows up to two. Each item is { name: \'ai-solutions-hub.example.ca\', validation: \'cname-delegation\' }; use dns-txt-token for an apex domain. Create the DNS records first, because deployment fails if validation cannot complete.')
@maxLength(2)
param customDomains array = []

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

// Custom domains are additive: the default hostname keeps serving the site
// alongside them. Free tier covers up to two, with managed TLS certificates,
// so this does not change the SKU or the cost boundary.
resource brandedDomains 'Microsoft.Web/staticSites/customDomains@2023-12-01' = [for domain in customDomains: {
  parent: site
  name: domain.name
  properties: {
    validationMethod: contains(domain, 'validation') ? domain.validation : 'cname-delegation'
  }
}]

output hostname string = site.properties.defaultHostname
output brandedHostnames array = [for domain in customDomains: domain.name]
output resourceId string = site.id

// A second, readable address for the same published files. Static Web Apps
// assigns its default hostname randomly and cannot rename it, and no custom
// domain is available because the lab owns no DNS zone. An App Service
// hostname is chosen rather than generated, so it carries the brand. The Free
// (F1) plan has no cost and no reserved compute, which keeps the existing
// allowances closed. The Static Web App keeps serving its original address.
@description('Readable hostname for the additional link, published as <name>.azurewebsites.net.')
param brandedSiteName string = 'ai-solutions-hub-ca'

@description('Free App Service plan hosting the additional link.')
param brandedPlanName string = 'asp-ai-solutions-hub'

@description('Free (F1) App Service quota was unavailable in the Static Web App region, so the additional link runs in Canada Central. It serves identical files, so this is not a data-residency change.')
param brandedLocation string = 'canadacentral'

@description('Set false to publish the Static Web App address only.')
param deployBrandedHost bool = true

resource brandedPlan 'Microsoft.Web/serverfarms@2023-12-01' = if (deployBrandedHost) {
  name: brandedPlanName
  location: brandedLocation
  tags: tags
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  properties: {
    reserved: false
  }
}

resource brandedHost 'Microsoft.Web/sites@2023-12-01' = if (deployBrandedHost) {
  name: brandedSiteName
  location: brandedLocation
  tags: tags
  properties: {
    serverFarmId: brandedPlan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      defaultDocuments: [
        'index.html'
      ]
    }
  }
}

// site/dist/web.config reproduces the Static Web Apps response headers on this
// host, so both addresses serve one security policy from one source of truth.
output brandedSiteHostname string = deployBrandedHost ? brandedHost.properties.defaultHostName : ''
