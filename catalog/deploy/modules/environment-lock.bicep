// Puts a CanNotDelete lock on the Container Apps environment. The environment owns the URL's domain, so deleting
// it (even by accident) would change the URL of every app in it. The lock still allows updates.
param environmentName string

resource environment 'Microsoft.App/managedEnvironments@2025-01-01' existing = {
  name: environmentName
}

resource lock 'Microsoft.Authorization/locks@2020-05-01' = {
  name: 'protect-${environmentName}'
  scope: environment
  properties: {
    level: 'CanNotDelete'
    notes: 'Keeps the environment, and so the default domain used in the app URLs. Remove this lock before deleting the environment.'
  }
}
