// Deploys the catalog search container to Azure Container Apps with a stable public URL.
//
// The URL is https://<appName>.<environment default domain>. The default domain is generated once, when the
// Container Apps environment is created, and then never changes. So the URL stays the same through image
// updates, new revisions, and even deleting and recreating the app, as long as two things hold:
//   1. the environment is kept (this template deploys INTO an existing environment unless createEnvironment is
//      true, and puts a delete lock on it), and
//   2. the app keeps its name.
// No custom domain is needed.
//
// The app pulls its image from Azure Container Registry with a user-assigned managed identity that is granted
// the AcrPull role, so there is no registry password. The registry must be in the same Microsoft Entra tenant.
//
//   az deployment group what-if -g <rg> -f main.bicep -p main.bicepparam
//   az deployment group create  -g <rg> -f main.bicep -p main.bicepparam
targetScope = 'resourceGroup'

// ---------------------------------------------------------------- App and URL
@description('Name of the Container App. It is the first part of the public URL, so changing it changes the URL.')
@minLength(2)
@maxLength(32)
param appName string = 'learn-catalog'

@description('Name of the Container Apps environment. Its default domain, the rest of the URL, is fixed when the environment is created.')
param environmentName string

@description('Create the environment. Use true only for a first-time deployment into a resource group that has none. Re-deploying with true to the same group and name keeps the existing environment and its domain. Leave false to deploy into an existing environment.')
param createEnvironment bool = false

@description('Protect the environment with a CanNotDelete lock. Deleting an environment gives the next one a new domain, so this protects the URL. Remove the lock first if you really want to delete it.')
param lockEnvironment bool = true

@description('Workload profile of the environment. Leave empty for a Consumption-only environment (the older kind). Ignored when createEnvironment is true, which creates a workload-profiles environment with the Consumption profile.')
param workloadProfileName string = ''

@description('Azure region. It must match the environment, so by default it is the region of the resource group.')
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
@description('Optional. When set, every call except /health must send this value in the x-api-key header. Leave empty for an open API. Stored as a Container Apps secret.')
@secure()
param apiKey string = ''

@description('CPU cores, for example 0.5.')
param cpu string = '0.5'

@description('Memory, for example 1Gi. The service needs about 200 MB.')
param memory string = '1Gi'

@minValue(0)
param minReplicas int = 1

@minValue(1)
param maxReplicas int = 2

var port = 8000
var environmentId = resourceId('Microsoft.App/managedEnvironments', environmentName)
var profileName = createEnvironment ? 'Consumption' : workloadProfileName
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d' // built-in "AcrPull"
var hasApiKey = !empty(apiKey)

// ---------------------------------------------------------------- Environment (first-time only) and lock
module environment 'modules/environment.bicep' = if (createEnvironment) {
  name: 'environment-${environmentName}'
  params: {
    name: environmentName
    location: location
    tags: tags
  }
}

module environmentLock 'modules/environment-lock.bicep' = if (lockEnvironment) {
  name: 'lock-${environmentName}'
  params: {
    environmentName: environmentName
  }
  dependsOn: [
    environment
  ]
}

// ---------------------------------------------------------------- Pull access: managed identity + AcrPull
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${appName}'
  location: location
  tags: tags
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registryName
  scope: resourceGroup(registrySubscriptionId, registryResourceGroup)
}

module acrPull 'modules/acr-pull.bicep' = {
  name: 'acr-pull-${appName}'
  scope: resourceGroup(registrySubscriptionId, registryResourceGroup)
  params: {
    registryName: registryName
    principalId: identity.properties.principalId
    roleAssignmentName: guid(subscription().id, registryResourceGroup, registryName, identity.name, acrPullRoleId)
    roleDefinitionId: acrPullRoleId
  }
}

// ---------------------------------------------------------------- The app
resource app 'Microsoft.App/containerApps@2025-01-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    environmentId: environmentId
    workloadProfileName: empty(profileName) ? null : profileName
    configuration: {
      activeRevisionsMode: 'Single' // the previous revision keeps serving until the new one is healthy
      ingress: {
        external: true
        targetPort: port
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: identity.id
        }
      ]
      secrets: hasApiKey ? [
        {
          name: 'api-key'
          value: apiKey
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'catalog'
          image: image
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: hasApiKey ? [
            {
              name: 'API_KEY'
              secretRef: 'api-key'
            }
          ] : []
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: port
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: port
              }
              initialDelaySeconds: 3
              periodSeconds: 10
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
  dependsOn: [
    environment
    acrPull
  ]
}

@description('The stable public URL of the API.')
output url string = 'https://${app.properties.configuration.ingress.fqdn}'

@description('The newest revision of the app.')
output latestRevision string = app.properties.latestRevisionName

@description('Principal id of the managed identity that pulls the image.')
output identityPrincipalId string = identity.properties.principalId
