# Azure CLI reference

This connector wraps the local `az` CLI; no remote MCP. Auth is the user's existing `az` session.

## Auth model

- `az login` for user accounts (browser flow).
- `az login --service-principal -u <appId> -p <secret> --tenant <tenantId>` for headless contexts; rotate the secret and prefer federated credentials where possible.
- `az login --identity` on Azure-hosted runners with a managed identity assigned.

## Read-side commands used

- `az resource show`
- `az storage account show`
- `az sql server show / sql db show`
- `az aks show`
- `az functionapp show / webapp show`
- `az keyvault show / secret list / secret show-deleted`
- `az role assignment list`
- `az role definition show`
- `az monitor activity-log list`
- `az consumption usage list`

## What this connector does NOT do

- It does not call mutating verbs (`create`, `update`, `delete`, `set`). Mutation is delegated to `polymath-infra-azure` (write-side IaC) or a human operator.
- It does not modify role assignments. Reading them is fine; granting is not.
- It does not span subscriptions in one call. Cross-sub analysis is multiple invocations.

## Common pitfalls

- Azure CLI's "default subscription" is sticky; chained calls without `--subscription` may run against the wrong tenant entirely. Polymath sets it explicitly per call.
- `az role assignment list` shows assignments at one scope by default. Use `--all` to include inheritance from RG/subscription/MG scopes.
- `az monitor activity-log` has a 90-day retention window; queries beyond require Log Analytics / Sentinel.
- `az consumption` queries can be slow on subscriptions with millions of line items; narrow with `--start-date` / `--end-date` / `--instance-id`.
