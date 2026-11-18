using 'main.bicep'

// Web App names are globally unique, and the URL is derived only from the app name, so the URL stays
// https://scm-advisor.azurewebsites.net as long as the app keeps this name.
param appName = 'scm-advisor'
param planName = 'plan-scm-advisor'
param planSku = 'B1' // Basic tier

// This subscription has 0 Basic/Standard App Service quota in East US 2 (the resource group's region) but
// not in East US, so the plan is deployed there instead. Change this if that quota is granted for East US 2,
// or the subscription changes. Check with:
//   az rest --method get --url "https://management.azure.com/subscriptions/<sub-id>/providers/Microsoft.Web/locations/<region>/usages?api-version=2023-12-01"
param location = 'eastus'

// Deployed by digest. Replace with the digest printed by publish-image.ps1 (or the one running today).
param image = 'eshopacr.azurecr.io/csm-learn-catalog@sha256:4e5a2c3ab8e65453a0b58ba49607663f70205e7107d803adc417bea6513894c4'
param registryName = 'eshopacr'
param registryResourceGroup = 'AZ-400-eShop-Prod'

// Optional API key: set the CATALOG_API_KEY environment variable before deploying; empty means no key.
param apiKey = readEnvironmentVariable('CATALOG_API_KEY', '')
