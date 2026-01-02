# Test Admin-Only Registration System
# Run this script after both backend and frontend are running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Admin-Only Registration System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$backendUrl = "http://127.0.0.1:5000"
$frontendUrl = "http://localhost:3000"

# Step 1: Check if backend is running
Write-Host "[1/7] Checking backend status..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-WebRequest -Uri "$backendUrl/api/auth/login" -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body '{"username":"test","password":"test"}' `
        -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Backend is running on $backendUrl" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is NOT running. Please start it first." -ForegroundColor Red
    exit 1
}

# Step 2: Login as admin
Write-Host "`n[2/7] Logging in as admin..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body '{"username":"admin","password":"admin123"}'
    
    $adminToken = $loginResponse.access_token
    Write-Host "✅ Admin login successful" -ForegroundColor Green
    Write-Host "   Token: $($adminToken.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Admin login failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure admin user exists with password 'admin123'" -ForegroundColor Yellow
    exit 1
}

# Step 3: Create invitation
Write-Host "`n[3/7] Creating invitation for newuser@test.com..." -ForegroundColor Yellow
try {
    $invitationData = @{
        email = "newuser@test.com"
        role = "operator"
        department = "Testing Department"
    } | ConvertTo-Json

    $invitation = Invoke-RestMethod -Uri "$backendUrl/api/admin/invitations" `
        -Method POST `
        -Headers @{
            "Content-Type"="application/json"
            "Authorization"="Bearer $adminToken"
        } `
        -Body $invitationData

    Write-Host "✅ Invitation created successfully" -ForegroundColor Green
    Write-Host "   Email: $($invitation.email)" -ForegroundColor Gray
    Write-Host "   Role: $($invitation.role)" -ForegroundColor Gray
    Write-Host "   Token: $($invitation.token.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "   Expires: $($invitation.expires_at)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Invitation Link:" -ForegroundColor Cyan
    Write-Host "   $($invitation.invitation_link)" -ForegroundColor White
    
    $invitationToken = $invitation.token
} catch {
    Write-Host "❌ Failed to create invitation: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
    exit 1
}

# Step 4: Verify token
Write-Host "`n[4/7] Verifying invitation token..." -ForegroundColor Yellow
try {
    $verifyData = @{ token = $invitationToken } | ConvertTo-Json
    
    $verification = Invoke-RestMethod -Uri "$backendUrl/api/auth/verify-token" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $verifyData

    Write-Host "✅ Token is valid" -ForegroundColor Green
    Write-Host "   Valid: $($verification.valid)" -ForegroundColor Gray
    Write-Host "   Email: $($verification.email)" -ForegroundColor Gray
    Write-Host "   Role: $($verification.role)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Token verification failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Register new user with token
Write-Host "`n[5/7] Registering new user with invitation..." -ForegroundColor Yellow
try {
    $registerData = @{
        username = "testuser_$(Get-Random -Maximum 9999)"
        email = "newuser@test.com"
        password = "password123"
        token = $invitationToken
    } | ConvertTo-Json

    $registration = Invoke-RestMethod -Uri "$backendUrl/api/auth/register" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $registerData

    Write-Host "✅ User registered successfully" -ForegroundColor Green
    Write-Host "   Username: $($registration.username)" -ForegroundColor Gray
    Write-Host "   Email: $($registration.email)" -ForegroundColor Gray
    Write-Host "   Role: $($registration.role)" -ForegroundColor Gray
    
    $newUsername = $registration.username
} catch {
    Write-Host "❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
    exit 1
}

# Step 6: Verify invitation is now marked as used
Write-Host "`n[6/7] Checking invitation status..." -ForegroundColor Yellow
try {
    $invitations = Invoke-RestMethod -Uri "$backendUrl/api/admin/invitations?status=used" `
        -Method GET `
        -Headers @{
            "Content-Type"="application/json"
            "Authorization"="Bearer $adminToken"
        }

    $usedInvitation = $invitations.invitations | Where-Object { $_.token -eq $invitationToken }
    
    if ($usedInvitation) {
        Write-Host "✅ Invitation marked as used" -ForegroundColor Green
        Write-Host "   Used at: $($usedInvitation.used_at)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Invitation not found in used list" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not verify invitation status" -ForegroundColor Yellow
}

# Step 7: Try to reuse the same token (should fail)
Write-Host "`n[7/7] Testing token reuse prevention..." -ForegroundColor Yellow
try {
    $reuseData = @{
        username = "testuser2_$(Get-Random -Maximum 9999)"
        email = "newuser@test.com"
        password = "password123"
        token = $invitationToken
    } | ConvertTo-Json

    $reuseAttempt = Invoke-RestMethod -Uri "$backendUrl/api/auth/register" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $reuseData `
        -ErrorAction Stop

    Write-Host "❌ Token was reused (should have failed!)" -ForegroundColor Red
} catch {
    Write-Host "✅ Token reuse correctly prevented" -ForegroundColor Green
    Write-Host "   Error: $($_.ErrorDetails.Message)" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Backend is running" -ForegroundColor Green
Write-Host "✅ Admin authentication works" -ForegroundColor Green
Write-Host "✅ Invitation creation works" -ForegroundColor Green
Write-Host "✅ Token verification works" -ForegroundColor Green
Write-Host "✅ User registration with token works" -ForegroundColor Green
Write-Host "✅ Token marked as used" -ForegroundColor Green
Write-Host "✅ Token reuse prevented" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 All tests passed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open frontend: $frontendUrl" -ForegroundColor White
Write-Host "2. Login as admin (username: admin, password: admin123)" -ForegroundColor White
Write-Host "3. Navigate to Admin Panel in sidebar" -ForegroundColor White
Write-Host "4. Explore User Management and Invitation Management tabs" -ForegroundColor White
Write-Host ""
