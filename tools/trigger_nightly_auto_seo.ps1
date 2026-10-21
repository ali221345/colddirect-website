# Fallback hook for Nightly auto-seo (live).
# Safe to run from Task Scheduler: if a successful nightly already finished in
# the last 6 hours it exits 0 without dispatching. Does not print secrets.
$ErrorActionPreference = "Stop"
$repo = "ali221345/colddirect-website"
$workflow = "auto-seo-nightly.yml"
$cutoff = (Get-Date).ToUniversalTime().AddHours(-6).ToString("yyyy-MM-ddTHH:mm:ssZ")

$runs = gh run list --repo $repo --workflow $workflow --limit 8 --json databaseId,conclusion,createdAt,status | ConvertFrom-Json
$recentOk = $runs | Where-Object { $_.conclusion -eq "success" -and $_.createdAt -ge $cutoff }
if ($recentOk) {
    Write-Output ("skip: successful nightly already ran at {0}" -f $recentOk[0].createdAt)
    exit 0
}

gh workflow run $workflow --repo $repo --ref main
Write-Output "dispatched $workflow on $repo main"
