# Notes

- Configure the app to use the identity for Key Vault reference operations by setting the keyVaultReferenceIdentity property to the resource ID of the user-assigned identity:
```bash
userAssignedIdentity=$(az identity show --resource-group poc-rg --name simple-func-app-identity --query id --output tsv)
az functionapp update --resource-group poc-rg --name simple-func-app --set keyVaultReferenceIdentity=${userAssingnedIdentity}

```

- Configure your app to pull from Azure Container Registry by using managed identities.
```bash
appConfig=$(az functionapp config show --resource-group poc-rg --name simple-func-app --query id --output tsv)
az resource update --ids $appConfig --set properties.acrUseManagedIdentityCreds=True
```

- Set the client ID your Function App app uses to pull from Azure Container Registry. 
```bash
clientId=$(az identity show --resource-group poc-rg --name simple-func-app-identity --query clientId --output tsv)
az resource update --ids $appConfig --set properties.AcrUserManagedIdentityID=$clientId
```

- Build and run in container 
```bash
docker build -t avamlechavez.azurecr.io/simple_func_app:local .
docker run -v $(pwd)/local.settings.json:/home/site/wwwroot/local.settings.json \
-v /usr/bin/az:/usr/local/bin/az \
-v ~/.azure:/root/.azure \
-v /usr/lib/python3.12:/opt/az/bin/python3 \
-v secrets:/azure-functions-host/Secrets \
-e AzureWebJobsSecretStorageType=files \
-p 8080:80 avamlechavez.azurecr.io/simple_func_app:local
```
