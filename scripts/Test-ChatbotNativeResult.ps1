[CmdletBinding()]
param(
    [Parameter(Mandatory)][object]$Result,
    [string]$UnknownSku = 'ZZ-999999'
)
$ErrorActionPreference = 'Stop'
if($Result.status -ne 200) { throw "Native journey returned HTTP $($Result.status)." }
$answer = [string]$Result.response.content
$cards = @($Result.response.recommendedProducts)
if($answer -notmatch 'Snow Veil' -or $answer -notmatch '(?<!\d)59\.5(?:0)?(?!\d)' -or
   @($cards | Where-Object {$_.id -eq 'CP-0001' -and $_.price -eq 59.5}).Count -ne 1) {
    throw 'Functional failure: no grounded Snow Veil/CP-0001/59.50 recommendation. HTTP200 alone is not success.'
}
if($answer -notmatch [regex]::Escape($UnknownSku) -or
   $answer -notmatch "(?i)(not.{0,60}(catalog|found|sell|stock|available)|no (data|record)|cannot (find|confirm)|can't (find|confirm))" -or
   @($cards | Where-Object {$_.id -eq $UnknownSku}).Count -gt 0) {
    throw 'Functional failure: the unknown SKU was not explicitly rejected without a fabricated card.'
}
'Native catalog and negative-SKU assertions passed.'
