$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) { python -m venv .venv }
& ./.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed' }
Push-Location frontend
try {
  npm.cmd install
  if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed' }
} finally { Pop-Location }
$backendProcess = Start-Process -FilePath "$projectRoot/.venv/Scripts/python.exe" -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory "$projectRoot/backend" -WindowStyle Hidden -PassThru
try {
  Set-Location -LiteralPath "$projectRoot/frontend"
  Write-Host 'PULSE AI: http://localhost:5173 | API docs: http://localhost:8000/docs'
  npm.cmd run dev -- --host 127.0.0.1
} finally {
  Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
}
