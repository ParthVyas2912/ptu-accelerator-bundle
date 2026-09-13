$ErrorActionPreference = 'Stop'
$allocationPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'evidence\modernize\budget-allocation.json'
if (-not (Test-Path -LiteralPath $allocationPath)) {
    throw 'Explicit Modernize budget authorization is required before start or evaluation.'
}
$allocation = Get-Content -LiteralPath $allocationPath -Raw | ConvertFrom-Json
if ($allocation.status -ne 'open' -or $allocation.total_limit -le $allocation.used -or
    $allocation.remaining -le 0 -or [string]::IsNullOrWhiteSpace($allocation.approval_reference)) {
    throw 'Modernize evaluation is closed at 10/10. Explicit new parent budget and guard reconciliation are required; the old two attempts belong to MACAE.'
}
