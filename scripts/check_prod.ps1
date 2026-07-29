$src = "C:\Users\tomba\OneDrive\Escritorio\AppPlanillaPlantaPot"
$dst = "C:\Users\tomba\OneDrive\Escritorio\LaboratorioAgua_NEW"

$modulos = @("presentation","cliente","libro_entrada","libro_fisico","libro_bacteriologia","shared","data","planilla_diaria")
$issues = [System.Collections.Generic.List[string]]::new()

foreach ($mod in $modulos) {
    $srcFiles = Get-ChildItem "$src\$mod" -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
    foreach ($sf in $srcFiles) {
        $rel = $sf.FullName.Substring(("$src\$mod\").Length)
        $dstPath = Join-Path "$dst\$mod" $rel
        if (-not (Test-Path $dstPath)) {
            $issues.Add("  [FALTA]   $mod\$rel")
        } else {
            $df = Get-Item $dstPath
            if ($sf.LastWriteTime -gt $df.LastWriteTime) {
                $issues.Add("  [DESACT]  $mod\$rel    src=$($sf.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))  prod=$($df.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))")
            }
        }
    }
}

# main.py
$s = Get-Item "$src\main.py"
$dp = "$dst\main.py"
if (-not (Test-Path $dp)) { $issues.Add("  [FALTA]   main.py") }
else {
    $d = Get-Item $dp
    if ($s.LastWriteTime -gt $d.LastWriteTime) {
        $issues.Add("  [DESACT]  main.py    src=$($s.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))  prod=$($d.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))")
    }
}

Write-Host ""
Write-Host "=== FRONTEND PYTHON ===" -ForegroundColor Cyan
if ($issues.Count -eq 0) {
    Write-Host "  OK - Produccion actualizada" -ForegroundColor Green
} else {
    Write-Host "  $($issues.Count) archivo(s) con diferencias:" -ForegroundColor Yellow
    $issues | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
}

# --- API .NET ---
Write-Host ""
Write-Host "=== API .NET ===" -ForegroundColor Cyan
$apiSrc = "C:\Users\tomba\source\repos\ApiLaboratorioAgua\publish_out"
$apiDst = "C:\Users\tomba\OneDrive\Escritorio\LaboratorioAgua_NEW\Api"
$apiIssues = [System.Collections.Generic.List[string]]::new()

$srcDll = Get-Item "$apiSrc\ApiLaboratorioAgua.dll" -ErrorAction SilentlyContinue
$dstDll = Get-Item "$apiDst\ApiLaboratorioAgua.dll" -ErrorAction SilentlyContinue

if ($null -eq $srcDll) {
    Write-Host "  Sin publish_out disponible para comparar" -ForegroundColor Gray
} elseif ($null -eq $dstDll) {
    Write-Host "  [FALTA] ApiLaboratorioAgua.dll en produccion" -ForegroundColor Red
} elseif ($srcDll.LastWriteTime -gt $dstDll.LastWriteTime) {
    Write-Host "  [DESACT] ApiLaboratorioAgua.dll    src=$($srcDll.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))  prod=$($dstDll.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Yellow
} else {
    Write-Host "  OK - DLL actualizada" -ForegroundColor Green
    Write-Host "       prod: $($dstDll.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))  src: $($srcDll.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
}
Write-Host ""
