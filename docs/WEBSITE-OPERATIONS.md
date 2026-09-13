# Stakeholder website operations

## Purpose and boundary

The stakeholder website is a **public, static, informational** view of the portfolio. It has no API, authentication credentials, model access, data upload or control connection to the accelerator lab. It does not spend PTUs when someone visits it.

- Website: https://blue-beach-0fb8cd70f.5.azurestaticapps.net/
- Private source: https://github.com/ParthVyas2912/ptu-accelerator-bundle
- Azure resource: `ptu-bundle-portal`, group `rg-ptu-bundle-web`
- Hosting: Azure Static Web Apps **Free**, East US 2
- Provisioning template: `infra/website.bicep`
- Production deploy workflow: `.github/workflows/deploy-site.yml`

Azure Static Web Apps did not offer a Canadian resource region in the provider inventory used for this deployment. East US 2 hosts only curated public-safe material. This is not a Canadian data-residency or DND accreditation claim.

## Cost

The new Azure resource is a Free-tier static website. No additional storage account, database, model deployment, registry, Container App, application backend or paid plan was provisioned for it. Free-tier limits and GitHub Actions plan allowances apply. The separate retained accelerator lab may still incur its previously documented costs.

Do not change the SKU or add APIs/custom infrastructure without reviewing the new cost and publication boundary.

## Updating the website

1. Create a branch.
2. Edit the curated source under `site/`; never import root reports/evidence into the public build.
3. Follow `site/README.md` to install dependencies, run tests and build.
4. Run the staged publication check: `python scripts/check_publication.py --staged --allowlist scripts/publication_allowlist.json`.
5. Open and review the pull request. Public-content review is required even though the repository is private.
6. Merge into `main`. Changes to `site/` or the deployment workflow trigger the production deployment.
7. Verify the workflow completed, the expected text is live, browser interactions work, and private artifact paths are not exposed.

Historical lab scripts are not a generic validation command. Site work does not authorize inference or lab restarts.

## Deployment credential

`AZURE_STATIC_WEB_APPS_API_TOKEN` is stored as a GitHub Actions secret, never in a file or Git history. It is limited to this static site and is used only by the production deploy job. Workflow permissions default to read-only, Actions are pinned to reviewed commits, pull requests do not receive deployment credentials, and checkout does not persist Git credentials.

Do not log the Azure CLI's deployment-token output. To rotate, use the owning Azure resource's token-management operation and immediately update the GitHub secret from process memory or secure stdin. Coordinate rotation with a deployment window. No tenant application registration or client secret is required by this hosting path.

## Rollback

Revert the offending **site source** commit through a reviewed change, run checks, and deploy the resulting `main` revision. A revert of documentation alone does not alter the deployed website.

Do not run destructive lab cleanup, change existing application's ingress, or delete unrelated resources as a website rollback.

## Provisioning again

Infrastructure is intentionally not auto-provisioned by GitHub Actions. Review the target subscription, resource group, region and Free SKU first. Use the guarded Azure invocation pattern for this MCAPS workspace:

```powershell
.\Invoke-LabAz.ps1 deployment group create `
  --name stakeholder-website `
  --resource-group rg-ptu-bundle-web `
  --template-file infra\website.bicep `
  --subscription <approved-mcaps-subscription-id>
```

The guard enforces the subscription in the local deployment contract. This example is not approval to create resources in a different tenant, modify protected applications, or restart model-consuming services.

## Verify resource versus content

An Azure resource returning HTTP 200 may still display the platform's default welcome page. Completion requires both:

1. Resource exists with SKU **Free** and only the intended static-site resource in its group.
2. The built portfolio content is published, interactions pass, and private files are inaccessible.

Final publication evidence is recorded in `docs/website-deployment.json`. Keep operational metadata private; it is not input to the website build.
