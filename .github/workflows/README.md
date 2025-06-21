# GitHub Actions Setup for Azure Container Registry

This document explains how to configure the GitHub repository secrets required for the Docker build and push workflow into an Azure Container Registry.

## Required GitHub Secrets

You need to set up the following secrets in your GitHub repository:

### Azure Container Registry Secrets

1. **AZURE_REGISTRY_URL**
   - Description: The URL of your Azure Container Registry
   - Example: `myregistry.azurecr.io`
   - How to find: In Azure Portal → Container registries → Your registry → Overview → Registry name

2. **AZURE_REGISTRY_USERNAME**
   - Description: The username for authentication to your ACR
   - Example: `myregistry` (usually the registry name)
   - How to find: In Azure Portal → Container registries → Your registry → Access keys → Username

3. **AZURE_REGISTRY_PASSWORD**
   - Description: The password for authentication to your ACR
   - How to find: In Azure Portal → Container registries → Your registry → Access keys → password (or password2)

## Setting up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each of the three secrets listed above

## Alternative: Using Azure Service Principal (Recommended for Production)

For production environments, it's recommended to use a Service Principal instead of registry admin credentials:

1. Create a Service Principal in Azure:
   ```bash
   az ad sp create-for-rbac --name "github-actions-acr" --role acrpush --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.ContainerRegistry/registries/{registry-name}
   ```

2. Use these secrets instead:
   - **AZURE_REGISTRY_URL**: Your ACR URL (same as above)
   - **AZURE_REGISTRY_USERNAME**: The `appId` from the service principal output
   - **AZURE_REGISTRY_PASSWORD**: The `password` from the service principal output

## Workflow Triggers

The workflow is configured to run on:
- Push to `main` and `develop` branches
- Push of version tags (e.g., `v1.0.0`)
- Pull requests to `main` branch

## Image Tags

The workflow automatically creates the following tags:
- Branch name for branch pushes
- PR number for pull requests
- Semantic version tags for version tags
- `latest` for the default branch
- SHA-prefixed tags for commit identification

## Multi-platform Builds

The workflow builds images for both:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64)

This ensures compatibility with various deployment targets including Apple Silicon and ARM-based cloud instances.
