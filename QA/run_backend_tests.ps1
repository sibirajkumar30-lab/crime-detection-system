# Comprehensive Backend API Test Script
# Run from: crime_detection directory
# PowerShell script for testing all API endpoints

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Crime Detection System - API Tests" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000/api"
$testResults = @()
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$TestID,
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Headers = @{},
        [object]$Body = $null,
        [int]$ExpectedStatus = 200,
        [string]$Category = "General"
    )
    
    Write-Host "Testing: $Name" -NoNewline
    
    try {
        $params = @{
            Uri = "$baseUrl$Endpoint"
            Method = $Method
            UseBasicParsing = $true
            ErrorAction = 'Stop'
        }
        
        if ($Headers.Count -gt 0) {
            $params['Headers'] = $Headers
        }
        
        if ($Body) {
            $params['Body'] = ($Body | ConvertTo-Json -Depth 10)
            $params['ContentType'] = 'application/json'
        }
        
        $response = Invoke-WebRequest @params
        $actualStatus = $response.StatusCode
        
        if ($actualStatus -eq $ExpectedStatus) {
            Write-Host " [PASS]" -ForegroundColor Green
            $global:testsPassed++
            return @{
                TestID = $TestID
                Name = $Name
                Category = $Category
                Status = "PASS"
                Expected = $ExpectedStatus
                Actual = $actualStatus
                Notes = "Success"
            }
        } else {
            Write-Host " [FAIL]" -ForegroundColor Red
            Write-Host "  Expected: $ExpectedStatus, Got: $actualStatus" -ForegroundColor Yellow
            $global:testsFailed++
            return @{
                TestID = $TestID
                Name = $Name
                Category = $Category
                Status = "FAIL"
                Expected = $ExpectedStatus
                Actual = $actualStatus
                Notes = "Wrong status code"
            }
        }
    }
    catch {
        $actualStatus = if ($_.Exception.Response) { 
            [int]$_.Exception.Response.StatusCode 
        } else { 
            "Error" 
        }
        
        if ($actualStatus -eq $ExpectedStatus) {
            Write-Host " [PASS]" -ForegroundColor Green
            $global:testsPassed++
            return @{
                TestID = $TestID
                Name = $Name
                Category = $Category
                Status = "PASS"
                Expected = $ExpectedStatus
                Actual = $actualStatus
                Notes = "Expected error received"
            }
        } else {
            Write-Host " [FAIL]" -ForegroundColor Red
            Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
            $global:testsFailed++
            return @{
                TestID = $TestID
                Name = $Name
                Category = $Category
                Status = "FAIL"
                Expected = $ExpectedStatus
                Actual = $actualStatus
                Notes = $_.Exception.Message
            }
        }
    }
}

# Test 1: Backend Health Check
Write-Host "`n[1] Backend Health Check" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
$result = Test-Endpoint -TestID "T001" -Name "Backend Server Running" -Method GET -Endpoint "/" -ExpectedStatus 404 -Category "Health"
$testResults += $result

# Test 2: Authentication Endpoints
Write-Host "`n[2] Authentication Tests" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Test login without credentials
$result = Test-Endpoint -TestID "T002" -Name "Login without credentials" -Method POST -Endpoint "/auth/login" -ExpectedStatus 400 -Category "Authentication"
$testResults += $result

# Test login with invalid credentials
$result = Test-Endpoint -TestID "T003" -Name "Login with invalid credentials" -Method POST -Endpoint "/auth/login" `
    -Body @{email="invalid@test.com"; password="wrong"} -ExpectedStatus 401 -Category "Authentication"
$testResults += $result

# Test register without data
$result = Test-Endpoint -TestID "T004" -Name "Register without data" -Method POST -Endpoint "/auth/register" -ExpectedStatus 400 -Category "Authentication"
$testResults += $result

# Test protected endpoint without token
$result = Test-Endpoint -TestID "T005" -Name "Protected endpoint without auth" -Method GET -Endpoint "/auth/profile" -ExpectedStatus 401 -Category "Authentication"
$testResults += $result

# Test 3: Criminal Endpoints (Unauthorized)
Write-Host "`n[3] Criminal Management (Unauthorized)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$result = Test-Endpoint -TestID "T006" -Name "Get criminals without auth" -Method GET -Endpoint "/criminals" -ExpectedStatus 401 -Category "Criminal"
$testResults += $result

$result = Test-Endpoint -TestID "T007" -Name "Create criminal without auth" -Method POST -Endpoint "/criminals" -ExpectedStatus 401 -Category "Criminal"
$testResults += $result

# Test 4: Face Detection Endpoints (Unauthorized)
Write-Host "`n[4] Face Detection (Unauthorized)" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$result = Test-Endpoint -TestID "T008" -Name "Upload image without auth" -Method POST -Endpoint "/face-detection/upload" -ExpectedStatus 401 -Category "Detection"
$testResults += $result

$result = Test-Endpoint -TestID "T009" -Name "Get detection logs without auth" -Method GET -Endpoint "/face-detection/logs" -ExpectedStatus 401 -Category "Detection"
$testResults += $result

# Test 5: Video Detection Endpoints (Unauthorized)
Write-Host "`n[5] Video Detection (Unauthorized)" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$result = Test-Endpoint -TestID "T010" -Name "Upload video without auth" -Method POST -Endpoint "/video/upload" -ExpectedStatus 401 -Category "Video"
$testResults += $result

$result = Test-Endpoint -TestID "T011" -Name "Get video list without auth" -Method GET -Endpoint "/video/list" -ExpectedStatus 401 -Category "Video"
$testResults += $result

# Test 6: Dashboard Endpoints (Unauthorized)
Write-Host "`n[6] Dashboard/Analytics (Unauthorized)" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$result = Test-Endpoint -TestID "T012" -Name "Get dashboard stats without auth" -Method GET -Endpoint "/dashboard/stats" -ExpectedStatus 401 -Category "Dashboard"
$testResults += $result

$result = Test-Endpoint -TestID "T013" -Name "Get top criminals without auth" -Method GET -Endpoint "/dashboard/top-criminals" -ExpectedStatus 401 -Category "Dashboard"
$testResults += $result

$result = Test-Endpoint -TestID "T014" -Name "Get analytics report without auth" -Method GET -Endpoint "/dashboard/analytics/report" -ExpectedStatus 401 -Category "Dashboard"
$testResults += $result

# Test 7: Invalid Endpoints
Write-Host "`n[7] Invalid Endpoints" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

$result = Test-Endpoint -TestID "T015" -Name "Non-existent endpoint" -Method GET -Endpoint "/nonexistent" -ExpectedStatus 404 -Category "ErrorHandling"
$testResults += $result

$result = Test-Endpoint -TestID "T016" -Name "Invalid criminal ID" -Method GET -Endpoint "/criminals/99999" -ExpectedStatus 401 -Category "ErrorHandling"
$testResults += $result

# Summary
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Total Tests: $($testsPassed + $testsFailed)" -ForegroundColor White
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red

$passRate = if (($testsPassed + $testsFailed) -gt 0) { 
    [math]::Round(($testsPassed / ($testsPassed + $testsFailed)) * 100, 2) 
} else { 
    0 
}
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })

# Group by category
Write-Host "`nResults by Category:" -ForegroundColor Cyan
$testResults | Group-Object -Property Category | ForEach-Object {
    $passed = ($_.Group | Where-Object { $_.Status -eq "PASS" }).Count
    $failed = ($_.Group | Where-Object { $_.Status -eq "FAIL" }).Count
    Write-Host "  $($_.Name): $passed passed, $failed failed" -ForegroundColor White
}

# Save results to file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultsFile = "QA\test_results_$timestamp.json"
$testResults | ConvertTo-Json -Depth 10 | Out-File $resultsFile
Write-Host "`nResults saved to: $resultsFile" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
