param(
    [int]$MaxRows = 100,
    [int]$PageSize = 10,
    [string]$LoadFile = ""
)

$python = Join-Path $PSScriptRoot "..\venv\Scripts\python.exe"
$python = (Resolve-Path $python).Path

$args = @("-m", "src.pbixray_server", "--max-rows", "$MaxRows", "--page-size", "$PageSize")

if ($LoadFile -ne "") {
    $args += @("--load-file", $LoadFile)
}

& $python @args
