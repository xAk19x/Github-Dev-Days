$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    throw "Python 3 is required to run this remediation script."
}

& $pythonCmd.Source "$scriptDir/fix_rce_vulnerabilities.py" @args
exit $LASTEXITCODE
