# Quick Performance Test Runner
# Run load tests with Locust

Write-Host "Crime Detection System - Performance Test Runner" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
$backendUrl = "http://localhost:5000"
Write-Host "Checking if backend is running at $backendUrl..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "$backendUrl/api/health" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Host "✓ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend is not running!" -ForegroundColor Red
    Write-Host "Please start the backend server first:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python run.py" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

Write-Host ""
Write-Host "Select test mode:" -ForegroundColor Green
Write-Host "1. Web UI (interactive)"
Write-Host "2. Headless (automated)"
Write-Host "3. Quick smoke test (10 users, 1 min)"
Write-Host "4. Standard load test (50 users, 5 min)"
Write-Host "5. Stress test (100 users, 10 min)"
Write-Host "Q. Quit"
Write-Host ""

$choice = Read-Host "Enter choice"

$locustFile = "QA\tests\performance\test_load.py"
$host = "http://localhost:5000"

switch ($choice) {
    "1" {
        Write-Host "Starting Locust web UI..." -ForegroundColor Yellow
        Write-Host "Open http://localhost:8089 in your browser" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        locust -f $locustFile --host=$host
    }
    "2" {
        $users = Read-Host "Number of users"
        $spawnRate = Read-Host "Spawn rate (users/sec)"
        $duration = Read-Host "Duration (e.g., 5m, 60s)"
        
        Write-Host "Running headless load test..." -ForegroundColor Yellow
        locust -f $locustFile --host=$host --users $users --spawn-rate $spawnRate --run-time $duration --headless
    }
    "3" {
        Write-Host "Running quick smoke test (10 users, 1 minute)..." -ForegroundColor Yellow
        locust -f $locustFile --host=$host --users 10 --spawn-rate 2 --run-time 1m --headless
    }
    "4" {
        Write-Host "Running standard load test (50 users, 5 minutes)..." -ForegroundColor Yellow
        locust -f $locustFile --host=$host --users 50 --spawn-rate 5 --run-time 5m --headless
    }
    "5" {
        Write-Host "Running stress test (100 users, 10 minutes)..." -ForegroundColor Yellow
        Write-Host "WARNING: This may impact system performance!" -ForegroundColor Red
        $confirm = Read-Host "Continue? (y/n)"
        if ($confirm -eq "y") {
            locust -f $locustFile --host=$host --users 100 --spawn-rate 10 --run-time 10m --headless
        }
    }
    "Q" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Performance test complete!" -ForegroundColor Green
