using 'main.bicep'

// The app keeps this name, and the environment keeps its domain, so the URL stays
// https://learn-catalog.yellowgrass-5e694844.eastus2.azurecontainerapps.io
param appName = 'learn-catalog'
param environmentName = 'loader-app-env-dev'

// Deployed by digest. Replace with the digest printed by publish-image.ps1 (or the one running today).
param image = 'eshopacr.azurecr.io/csm-learn-catalog@sha256:4e5a2c3ab8e65453a0b58ba49607663f70205e7107d803adc417bea6513894c4'
param registryName = 'eshopacr'
param registryResourceGroup = 'AZ-400-eShop-Prod'

// Optional API key: set the CATALOG_API_KEY environment variable before deploying; empty means no key.
param apiKey = readEnvironmentVariable('CATALOG_API_KEY', '')
