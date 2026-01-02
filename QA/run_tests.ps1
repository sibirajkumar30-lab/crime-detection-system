# Quick Test Execution Scripts
# PowerShell scripts for running tests easily

# Run all tests
Write-Host "Crime Detection System - Test Runner" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Function to run tests with options
function Run-Tests {
    param(
        [string]$TestType = "all",
        [switch]$Coverage,
        [switch]$Verbose,
        [switch]$Html
    )
    
    $baseCmd = "pytest"
    $args = @()
    
    # Add test type filter
    switch ($TestType) {
        "unit" { $args += "-m", "unit" }
        "integration" { $args += "-m", "integration" }
        "e2e" { $args += "-m", "e2e" }
        "security" { $args += "-m", "security" }
        "slow" { $args += "-m", "slow" }
        "auth" { $args += "QA\tests\unit\test_auth.py" }
        "criminal" { $args += "QA\tests\unit\test_criminal.py" }
        "face" { $args += "QA\tests\unit\test_face_detection.py" }
        "all" { }
        default { $args += $TestType }
    }
    
    # Add verbosity
    if ($Verbose) {
        $args += "-v"
    }
    
    # Add coverage
    if ($Coverage) {
        $args += "--cov=backend/app"
        $args += "--cov-report=term-missing"
        
        if ($Html) {
            $args += "--cov-report=html:QA/reports/coverage/html"
        }
    }
    
    # Add HTML report
    if ($Html) {
        $args += "--html=QA/reports/test-report.html"
        $args += "--self-contained-html"
    }
    
    Write-Host "Running: $baseCmd $($args -join ' ')" -ForegroundColor Yellow
    Write-Host ""
    
    & $baseCmd @args
}

# Menu
Write-Host "Select test suite to run:" -ForegroundColor Green
Write-Host "1. All tests"
Write-Host "2. Unit tests only"
Write-Host "3. Integration tests only"
Write-Host "4. E2E tests only"
Write-Host "5. Security tests only"
Write-Host "6. Authentication tests"
Write-Host "7. Criminal management tests"
Write-Host "8. Face detection tests"
Write-Host "9. All tests with coverage"
Write-Host "10. All tests with HTML reports"
Write-Host "Q. Quit"
Write-Host ""

$choice = Read-Host "Enter choice"

switch ($choice) {
    "1" { Run-Tests -TestType "all" -Verbose }
    "2" { Run-Tests -TestType "unit" -Verbose }
    "3" { Run-Tests -TestType "integration" -Verbose }
    "4" { Run-Tests -TestType "e2e" -Verbose }
    "5" { Run-Tests -TestType "security" -Verbose }
    "6" { Run-Tests -TestType "auth" -Verbose }
    "7" { Run-Tests -TestType "criminal" -Verbose }
    "8" { Run-Tests -TestType "face" -Verbose }
    "9" { Run-Tests -TestType "all" -Coverage -Verbose -Html }
    "10" { Run-Tests -TestType "all" -Html -Verbose }
    "Q" { Write-Host "Exiting..." -ForegroundColor Yellow; exit }
    default { Write-Host "Invalid choice!" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Test execution complete!" -ForegroundColor Green

# Open reports if generated
if ($choice -eq "9" -or $choice -eq "10") {
    $openReports = Read-Host "Open HTML reports? (y/n)"
    if ($openReports -eq "y") {
        if (Test-Path "QA\reports\test-report.html") {
            Start-Process "QA\reports\test-report.html"
        }
        if (Test-Path "QA\reports\coverage\html\index.html") {
            Start-Process "QA\reports\coverage\html\index.html"
        }
    }
}
