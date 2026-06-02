# Azure backend deployment

This backend repo deploys to Azure App Service through GitHub Actions using an
App Service publish profile. This is the smallest setup path: no service
principal, tenant ID, or OIDC federated credential is required.

## 1. Create the Azure App Service

In the Azure portal, create a Web App with:

- Publish: `Code`
- Runtime stack: `Python 3.14`
- Operating system: `Linux`

Use a small App Service plan while developing.

## 2. Configure the Azure Web App

In the Azure portal, open the backend Web App.

Set `Configuration -> General settings -> Startup Command` to:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Set `Configuration -> Application settings`:

`SCM_DO_BUILD_DURING_DEPLOYMENT`

```text
true
```

Optional, for Azure SQL:

`AZURE_SQL_CONNECTIONSTRING`

```text
Server=tcp:<server>.database.windows.net,1433;Database=<db>;Encrypt=yes;TrustServerCertificate=no;Authentication=ActiveDirectoryDefault;
```

If you do not set `AZURE_SQL_CONNECTIONSTRING`, the backend will fall back to
SQLite. That is fine for a quick smoke test, but not for real production data.

## 3. Add GitHub repository secrets

In the backend GitHub repo, go to:

`Settings -> Secrets and variables -> Actions -> New repository secret`

Create:

`AZURE_BACKEND_WEBAPP_NAME`

The exact Azure Web App name.

Example:

```text
selldonut-backend-prod
```

`AZURE_WEBAPP_PUBLISH_PROFILE`

Download this from the Azure Web App:

`Overview -> Download publish profile`

Open the downloaded `.PublishSettings` file and paste the entire XML file
contents as the GitHub secret value.

## 4. Deploy

Push to the backend repo's `main` branch, or run the workflow manually from:

`Actions -> Deploy backend -> Run workflow`

The workflow file is:

`.github/workflows/backend-deploy.yml`
