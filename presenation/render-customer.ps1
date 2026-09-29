param(
  [string]$OutDir = (Join-Path $PSScriptRoot 'customer'),
  [string]$PreviewDir = (Join-Path $PSScriptRoot 'customer-preview')
)
# Exports the customer deliverables to PDF with installed desktop Office (COM,
# no online conversion) and enforces their length: one-pager = 1 page,
# two-pager = 2 pages, deck = 10-20 slides. Writes PNG previews for visual review.
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $PreviewDir | Out-Null
Get-ChildItem $PreviewDir -Filter *.png | Remove-Item
$failures = @()

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  foreach ($doc in @(@{ Name = 'PTU-Accelerator-One-Pager'; Pages = 1 }, @{ Name = 'PTU-Accelerator-Two-Pager'; Pages = 2 })) {
    $path = Join-Path $OutDir "$($doc.Name).docx"
    $d = $word.Documents.Open($path, $false, $true)
    $pages = $d.ComputeStatistics(2)
    $d.ExportAsFixedFormat((Join-Path $OutDir "$($doc.Name).pdf"), 17)
    $d.Close($false)
    Write-Output "$($doc.Name): $pages page(s)"
    if ($pages -ne $doc.Pages) { $failures += "$($doc.Name) has $pages pages; expected $($doc.Pages)" }
  }
} finally { $word.Quit() }

$ppt = New-Object -ComObject PowerPoint.Application
try {
  $name = 'PTU-Accelerator-Customer-Deck'
  $p = $ppt.Presentations.Open((Join-Path $OutDir "$name.pptx"), $true, $false, $false)
  $count = $p.Slides.Count
  $p.SaveAs((Join-Path $OutDir "$name.pdf"), 32)
  foreach ($slide in $p.Slides) {
    $slide.Export((Join-Path $PreviewDir ('deck-{0:d2}.png' -f $slide.SlideIndex)), 'PNG', 1600, 900)
    foreach ($shape in $slide.Shapes) {
      if ($shape.HasTextFrame -and $shape.TextFrame2.HasText) {
        $bottom = $shape.Top + [Math]::Max($shape.Height, $shape.TextFrame2.TextRange.BoundHeight)
        if ($bottom -gt $p.PageSetup.SlideHeight + 1 -or $shape.Left + $shape.Width -gt $p.PageSetup.SlideWidth + 1) {
          $failures += "Slide $($slide.SlideIndex): '$($shape.TextFrame2.TextRange.Text.Substring(0, [Math]::Min(40, $shape.TextFrame2.TextRange.Text.Length)))' runs off the slide"
        }
        if ($shape.TextFrame2.TextRange.BoundHeight -gt $shape.Height + 6) {
          $failures += "Slide $($slide.SlideIndex): text overflows its box: '$($shape.TextFrame2.TextRange.Text.Substring(0, [Math]::Min(40, $shape.TextFrame2.TextRange.Text.Length)))'"
        }
      }
    }
  }
  $p.Close()
  Write-Output "${name}: $count slides"
  if ($count -lt 10 -or $count -gt 20) { $failures += "Deck has $count slides; expected 10-20" }
} finally { $ppt.Quit() }

python -c "import pymupdf, pathlib, sys; out = pathlib.Path(sys.argv[2]); [p.get_pixmap(dpi=80).save(out / f'{pathlib.Path(f).stem}-{i+1}.png') for f in sys.argv[3:] for i, p in enumerate(pymupdf.open(pathlib.Path(sys.argv[1]) / f))]" $OutDir $PreviewDir 'PTU-Accelerator-One-Pager.pdf' 'PTU-Accelerator-Two-Pager.pdf'

if ($failures) { $failures | ForEach-Object { Write-Error $_ -ErrorAction Continue }; exit 1 }
Write-Output "All customer deliverables within length and bounds. PDFs in $OutDir; previews in $PreviewDir."
