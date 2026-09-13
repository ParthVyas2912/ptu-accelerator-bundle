[CmdletBinding()]
param([Parameter(Mandatory)][ValidatePattern('^[a-z0-9-]+$')][string]$Label)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$id = '/subscriptions/1feb53b2-854a-4ea7-b5a6-709b7d804f70/resourceGroups/accel-dkm-20260911/providers/Microsoft.CognitiveServices/accounts/oai-dkmeval0911a'
$end = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$base = @('monitor','metrics','list','--resource',$id,'--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',
    '--start-time','2026-09-12T01:24:00Z','--end-time',$end,'--interval','PT1M','-o','json')
$specs = @(
    @{name='totals'; args=@('--metrics','ModelRequests','InputTokens','OutputTokens','TotalTokens','--aggregation','Total','--filter',"ModelDeploymentName eq '*'")},
    @{name='statuses'; args=@('--metrics','AzureOpenAIRequests','--aggregation','Total','--filter',"StatusCode eq '*' and ModelDeploymentName eq '*'")},
    @{name='latency'; args=@('--metrics','Latency','--aggregation','Average','--filter',"OperationName eq '*'")}
)
foreach ($spec in $specs) {
    $raw = & (Join-Path $root 'Invoke-LabAz.ps1') -AzArguments ($base + $spec.args)
    $data = ($raw -join "`n") | ConvertFrom-Json
    [IO.File]::WriteAllText((Join-Path $root "evidence\documents\$Label-metrics-$($spec.name).json"),($data | ConvertTo-Json -Depth 50))
    foreach ($metric in $data.value) {
        foreach ($series in $metric.timeseries) {
            $points = @($series.data | Where-Object { $null -ne $_.total -or $null -ne $_.average })
            $sum = if ($spec.name -eq 'latency') { $null } else { ($points | Measure-Object -Property total -Sum).Sum }
            [pscustomobject]@{metric=$metric.name.value; dimensions=($series.metadatavalues | ConvertTo-Json -Compress); total=$sum; returned_points=$points.Count}
        }
    }
}
