targetScope = 'resourceGroup'
@allowed(['chat-api','scenario-api','chat-ui','scenario-ui'])
param service string
param image string
param minimumReplicas int = 0
param clientCidr string
resource environment 'Microsoft.App/managedEnvironments@2025-01-01' existing = {
  name: 'cae-ptu-bundle'
  scope: resourceGroup('rg-ptu-bundle-platform')
}
var domain = environment.properties.defaultDomain
var isFrontend = endsWith(service, '-ui')
var chatApi = 'https://chatbot-chat-api.internal.${domain}'
var scenarioApi = 'https://chatbot-scenario-api.internal.${domain}'
var env = isFrontend ? [
  { name: 'NGINX_USE_SYSTEM_RESOLVER', value: '1' }
  { name: 'BACKEND_API_URL', value: service == 'chat-ui' ? chatApi : scenarioApi }
  { name: 'CHAT_BACKEND_API_URL', value: chatApi }
  { name: 'VITE_CHAT_WIDGET_THEME', value: 'light' }
  { name: 'VITE_SCENARIO', value: 'ecommerce' }
] : [
  { name: 'AZURE_SEARCH_ENDPOINT', value: 'https://srch-ccptu1feb0911.search.windows.net' }
  { name: 'AZURE_SEARCH_PRODUCT_INDEX', value: 'ptu-chatbot-products' }
  { name: 'CHAT_API_URL', value: chatApi }
  { name: 'ALLOWED_ORIGINS_STR', value: 'https://chatbot-chat-ui.${domain},https://chatbot-scenario-ui.${domain}' }
]
module app './chatbot-container-app.bicep' = {
  name: 'ptu-${service}-container'
  params: {
    appName: 'chatbot-${service}'
    image: image
    targetPort: isFrontend ? 80 : (service == 'chat-api' ? 8001 : 8000)
    cpu: isFrontend ? '0.25' : '0.5'
    memory: isFrontend ? '0.5Gi' : '1Gi'
    external: isFrontend
    minimumReplicas: minimumReplicas
    clientCidr: clientCidr
    environmentVariables: env
  }
}
output endpoint string = 'https://${app.outputs.fqdn}'
output resourceId string = app.outputs.resourceId
output latestRevision string = app.outputs.latestRevision
