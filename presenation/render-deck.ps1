param(
    [string]$Deck = (Join-Path $PSScriptRoot 'PTU-Accelerator-Internal-2026-09-14.pptx')
)
$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path -LiteralPath $Deck).Path
$preview = Join-Path $PSScriptRoot 'preview'
$qa = Join-Path $PSScriptRoot 'qa'
New-Item -ItemType Directory -Force -Path $preview, $qa | Out-Null
$app = $null
$presentation = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $presentation = $app.Presentations.Open($resolved, $true, $false, $false)
    $presentation.SaveAs(
        (Join-Path $PSScriptRoot 'PTU-Accelerator-Internal-2026-09-14.pdf'), 32)
    $issues = @()
    foreach ($slide in $presentation.Slides) {
        $slide.Export((Join-Path $preview ('slide-{0:d2}.png' -f $slide.SlideIndex)), 'PNG', 1600, 900)
        foreach ($shape in $slide.Shapes) {
            if ($shape.Left -lt 0 -or $shape.Top -lt 0 -or
                ($shape.Left + $shape.Width) -gt ($presentation.PageSetup.SlideWidth + 1) -or
                ($shape.Top + $shape.Height) -gt ($presentation.PageSetup.SlideHeight + 1)) {
                $issues += [pscustomobject]@{ slide = $slide.SlideIndex; shape = $shape.Name; issue = 'Out of slide bounds' }
            }
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $frame = $shape.TextFrame2
                $available = $shape.Height - $frame.MarginTop - $frame.MarginBottom
                if ($frame.TextRange.BoundHeight -gt ($available + 2)) {
                    $issues += [pscustomobject]@{
                        slide = $slide.SlideIndex
                        shape = $shape.Name
                        issue = 'Text exceeds box height'
                        text = $frame.TextRange.Text
                        required = [math]::Round($frame.TextRange.BoundHeight, 1)
                        available = [math]::Round($available, 1)
                    }
                }
            }
        }
    }
    ConvertTo-Json -InputObject @($issues) -Depth 4 |
        Set-Content -LiteralPath (Join-Path $qa 'powerpoint-layout.json') -Encoding utf8
    Write-Output ('Exported {0} slides and PDF; {1} layout warnings.' -f $presentation.Slides.Count, $issues.Count)
    if ($issues.Count -gt 0) { $issues | Format-Table -AutoSize }
}
finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($null -ne $app) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
