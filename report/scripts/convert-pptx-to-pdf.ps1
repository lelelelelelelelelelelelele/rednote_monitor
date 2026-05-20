# Convert PPTX to PDF using PowerPoint COM (Windows)
# Usage: .\convert-pptx-to-pdf.ps1 <path-to-pptx>
# Output: same name with .pdf extension in the same folder

param(
    [Parameter(Mandatory=$true)]
    [string]$PptxPath
)

$pptxPath = Resolve-Path $PptxPath
$pdfPath = [System.IO.Path]::ChangeExtension($pptxPath, ".pdf")

Write-Host "Converting: $pptxPath"
Write-Host "Output:     $pdfPath"

try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoFalse

    $pres = $ppt.Presentations.Open($pptxPath)
    $pres.SaveAs($pdfPath, 32)  # 32 = ppSaveAsPDF
    $pres.Close()

    Write-Host "Done."
} catch {
    Write-Error "Failed: $($_.Exception.Message)"
    Write-Host "Make sure Microsoft PowerPoint is installed."
} finally {
    if ($ppt) {
        $ppt.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
    }
}
