
$resultsDir = Join-Path $PSScriptRoot "results"
New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null

$inputPath = Join-Path $PSScriptRoot "input.txt"
$solverPath = Join-Path $PSScriptRoot "BMSSP_deterministic_optimal_solver.py"

if (-not (Test-Path $inputPath)) {
	Write-Error "Input file not found: $inputPath"
	exit 1
}

if (-not (Test-Path $solverPath)) {
	Write-Error "Solver file not found: $solverPath"
	exit 1
}

$lineNumber = 0
foreach ($rawLine in Get-Content $inputPath) {
	$lineNumber++
	$line = $rawLine.Trim()

	if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
		continue
	}

	$parts = $line -split ',' | ForEach-Object { $_.Trim() }

	if ($parts.Count -ne 4) {
		Write-Warning "Skipping malformed line $lineNumber in ${inputPath} (expected 4 comma-separated values): $line"
		continue
	}

	$mdpType = $parts[0]
	$n = 0
	$sensorBudget = 0
	$memoryBudget = 0

	if (-not [int]::TryParse($parts[1], [ref]$n) -or -not [int]::TryParse($parts[2], [ref]$sensorBudget) -or -not [int]::TryParse($parts[3], [ref]$memoryBudget)) {
		Write-Warning "Skipping malformed line $lineNumber in ${inputPath} (n, sensor budget, and memory budget must be integers): $line"
		continue
	}

	$typeSlug = ($mdpType -replace '[^A-Za-z0-9_-]', '-')
	$outputFileName = "{0}_n{1}_sb{2}_mb{3}.txt" -f $typeSlug, $n, $sensorBudget, $memoryBudget
	$outputPath = Join-Path $resultsDir $outputFileName

	& python $solverPath $mdpType $n $sensorBudget $memoryBudget *> $outputPath

	if ($LASTEXITCODE -ne 0) {
		Write-Warning "Solver failed for line $lineNumber. See output: $outputPath"
	}
	else {
		Write-Host "Saved output to: $outputPath"
	}
}

