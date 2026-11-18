// Deploys the catalog search container to an Azure Web App (Linux, Web App for Containers) with a stable
// public URL.
//
// The URL is https://<appName>.azurewebsites.net. Web App names are globally unique and the hostname is
// derived only from the app name, so the URL stays the same through image updates and container restarts
// as long as the app keeps its name. No custom domain or separate "environment" resource is needed.
//
// The app pulls its image from Azure Container Registry with a user-assigned managed identity that is granted
// the AcrPull role, so there is no registry password. The registry must be in the same Microsoft Entra tenant.
//
// Basic tier runs a single instance with no deployment slots: unlike Container Apps, there is no previous
// version left serving traffic while a new image starts, so a bad image takes the app down until fixed.
//
//   az deployment group what-if -g <rg> -f main.bicep -p main.bicepparam
//   az deployment group create  -g <rg> -f main.bicep -p main.bicepparam
targetScope = 'resourceGroup'

// ---------------------------------------------------------------- App and URL
@description('Name of the Web App. It is also the first part of the public URL, so changing it changes the URL: https://<appName>.azurewebsites.net. Web App names are globally unique across Azure.')
@minLength(2)
@maxLength(60)
param appName string = 'scm-advisor'

@description('Name of the Linux App Service Plan that hosts the app. Created if it does not already exist.')
param planName string = 'plan-${appName}'

@description('App Service Plan SKU (Basic tier), for example B1, B2 or B3.')
param planSku string = 'B1'

@description('Azure region.')
param location string = resourceGroup().location

param tags object = {}

// ---------------------------------------------------------------- Image and registry
@description('Image to run. Use a digest so that a later push of the same tag cannot change what runs, for example myregistry.azurecr.io/csm-learn-catalog@sha256:...')
param image string

@description('Name of the Azure Container Registry the image is in.')
param registryName string

@description('Resource group of the registry.')
param registryResourceGroup string = resourceGroup().name

@description('Subscription of the registry.')
param registrySubscriptionId string = subscription().subscriptionId

// ---------------------------------------------------------------- Runtime
@description('Optional. When set, every call except /health must send this value in the x-api-key header. Leave empty for an open API. Stored as an app setting.')
@secure()
param apiKey string = ''

var port = 8000
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d' // built-in "AcrPull"
var hasApiKey = !empty(apiKey)

// ---------------------------------------------------------------- Plan (Linux, Basic tier)
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  tags: tags
  sku: {
    name: planSku
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true // required for Linux plans
  }
}

// ---------------------------------------------------------------- Pull access: managed identity + AcrPull
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${appName}'
  location: location
  tags: tags
}

module acrPull 'modules/acr-pull.bicep' = {
  name: 'acr-pull-${uniqueString(appName)}'
  scope: resourceGroup(registrySubscriptionId, registryResourceGroup)
  params: {
    registryName: registryName
    principalId: identity.properties.principalId
    roleAssignmentName: guid(subscription().id, registryResourceGroup, registryName, identity.name, acrPullRoleId)
    roleDefinitionId: acrPullRoleId
  }
}

// ---------------------------------------------------------------- The app
resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  tags: tags
  kind: 'app,linux,container'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${image}'
      acrUseManagedIdentityCreds: true
      acrUserManagedIdentityID: identity.properties.clientId
      alwaysOn: true // Basic tier supports Always On; keeps the single instance from idling out
      healthCheckPath: '/health'
      appSettings: concat([
        {
          name: 'WEBSITES_PORT'
          value: string(port)
        }
      ], hasApiKey ? [
        {
          name: 'API_KEY'
          value: apiKey
        }
      ] : [])
    }
  }
  dependsOn: [
    acrPull
  ]
}

@description('The stable public URL of the API.')
output url string = 'https://${app.properties.defaultHostName}'

@description('Principal id of the managed identity that pulls the image.')
output identityPrincipalId string = identity.properties.principalId

