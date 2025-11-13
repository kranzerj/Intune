#Requires -Version 5.1
#pwsh -ExecutionPolicy Bypass -File ".\DriveMapping-Generator.ps1"
<#
.SYNOPSIS
    Generiert ein PowerShell-Script für Netzlaufwerk-Mapping via Intune (User Context)

.DESCRIPTION
    Fragt interaktiv UNC-Pfad und Laufwerksbuchstabe ab und erstellt ein fertiges
    Deployment-Script für die Verteilung via Intune im User-Kontext.
#>

[CmdletBinding()]
param()

Clear-Host

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Intune Drive Mapping Generator" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Freigabe abfragen
do {
    $sharePath = Read-Host "UNC-Pfad der Freigabe (z.B. \\fileserver.countit.at\geheim$)"
    
    if ([string]::IsNullOrWhiteSpace($sharePath)) {
        Write-Host "Bitte gib einen gültigen UNC-Pfad ein!" -ForegroundColor Red
        $validShare = $false
    }
    elseif ($sharePath -notmatch '^\\\\[^\\]+\\[^\\]+') {
        Write-Host "Ungültiges Format! Verwende z.B.: \\server\share" -ForegroundColor Red
        $validShare = $false
    }
    else {
        $validShare = $true
    }
} while (-not $validShare)

Write-Host ""

# Laufwerksbuchstabe abfragen
do {
    $driveLetter = Read-Host "Laufwerksbuchstabe (z.B. M oder M:)"
    
    # Bereinigen des Inputs
    $driveLetter = $driveLetter.Trim().ToUpper() -replace ':', ''
    
    if ([string]::IsNullOrWhiteSpace($driveLetter)) {
        Write-Host "Bitte gib einen Laufwerksbuchstaben ein!" -ForegroundColor Red
        $validDrive = $false
    }
    elseif ($driveLetter -notmatch '^[A-Z]$') {
        Write-Host "Ungültiger Buchstabe! Verwende A-Z" -ForegroundColor Red
        $validDrive = $false
    }
    elseif ($driveLetter -in @('C', 'D')) {
        Write-Host "Systemlaufwerke C und D können nicht verwendet werden!" -ForegroundColor Red
        $validDrive = $false
    }
    else {
        $validDrive = $true
    }
} while (-not $validDrive)

Write-Host ""

# Freigabename abfragen
do {
    $shareName = Read-Host "Anzeigename der Freigabe (z.B. Geheime Freigabe)"
    
    if ([string]::IsNullOrWhiteSpace($shareName)) {
        Write-Host "Bitte gib einen Namen ein!" -ForegroundColor Red
        $validName = $false
    }
    else {
        $validName = $true
    }
} while (-not $validName)

# Servername und Share aus UNC-Pfad extrahieren für MountPoints2
if ($sharePath -match '^\\\\([^\\]+)\\(.+)$') {
    $serverName = $Matches[1]
    $shareNamePath = $Matches[2]
}
else {
    $serverName = "unknown"
    $shareNamePath = "unknown"
}

Write-Host ""
Write-Host "Konfiguration:" -ForegroundColor Green
Write-Host "  Freigabe: $sharePath" -ForegroundColor White
Write-Host "  Laufwerk: ${driveLetter}:" -ForegroundColor White
Write-Host "  Anzeigename: $shareName" -ForegroundColor White
Write-Host ""

# Script-Inhalt generieren
$scriptContent = @"
<#
.SYNOPSIS
    Verbindet Netzlaufwerk $($driveLetter): mit $sharePath

.DESCRIPTION
    Verbindet das Netzlaufwerk persistent im User-Kontext.
    Deployment via Intune als User Context Script.
    
.NOTES
    Generiert am: $(Get-Date -Format 'dd.MM.yyyy HH:mm')
#>

[CmdletBinding()]
param()

# Logging starten
Start-Transcript -Path "`$(Join-Path `$env:temp 'DriveMapping-$($driveLetter).log')" -Force

try {
    `$driveLetter = "$driveLetter"
    `$sharePath = "$sharePath"
    `$shareName = "$shareName"
    `$serverName = "$serverName"
    `$shareNamePath = "$shareNamePath"
    
    Write-Output "Starte Laufwerkszuordnung..."
    Write-Output "Laufwerk: `${driveLetter}:"
    Write-Output "Pfad: `$sharePath"
    Write-Output "Name: `$shareName"
    
    # Prüfen ob Laufwerk bereits existiert
    `$existingDrive = Get-PSDrive -Name `$driveLetter -PSProvider FileSystem -ErrorAction SilentlyContinue
    
    if (`$existingDrive) {
        if (`$existingDrive.DisplayRoot -eq `$sharePath) {
            Write-Output "Laufwerk `${driveLetter}: ist bereits korrekt zugeordnet zu `$sharePath"
        }
        else {
            Write-Output "Laufwerk `${driveLetter}: existiert mit anderem Pfad. Entferne altes Mapping..."
            Remove-PSDrive -Name `$driveLetter -PSProvider FileSystem -Force -ErrorAction SilentlyContinue
            
            # Warte kurz
            Start-Sleep -Seconds 2
            
            Write-Output "Erstelle neue Zuordnung..."
            `$null = New-PSDrive -PSProvider FileSystem -Name `$driveLetter -Root `$sharePath -Persist -Scope Global -ErrorAction Stop
        }
    }
    else {
        Write-Output "Erstelle Laufwerkszuordnung..."
        `$null = New-PSDrive -PSProvider FileSystem -Name `$driveLetter -Root `$sharePath -Persist -Scope Global -ErrorAction Stop
    }
    
    # ProviderFlags auf 1 setzen (macht Laufwerk persistent)
    Write-Output "Setze ProviderFlags..."
    `$regPath = "HKCU:\Network\`$driveLetter"
    
    if (Test-Path `$regPath) {
        Set-ItemProperty -Path `$regPath -Name "ProviderFlags" -Value 1 -Type DWord -Force -ErrorAction Stop
        Write-Output "ProviderFlags erfolgreich gesetzt"
    }
    else {
        Write-Warning "Registry-Pfad `$regPath nicht gefunden"
    }
    
    # MountPoints2 Registry-Eintrag setzen
    Write-Output "Setze Anzeigename in MountPoints2..."
    try {
        `$mountPointPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2\##`$serverName#`$shareNamePath"
        
        if (-not (Test-Path `$mountPointPath)) {
            `$null = New-Item -Path `$mountPointPath -Force -ErrorAction Stop
        }
        
        Set-ItemProperty -Path `$mountPointPath -Name "_LabelFromReg" -Value `$shareName -Type String -Force -ErrorAction Stop
        Write-Output "Anzeigename '`$shareName' erfolgreich gesetzt"
    }
    catch {
        Write-Warning "MountPoints2 konnte nicht gesetzt werden: `$(`$_.Exception.Message)"
    }
    
    # RestoreConnection deaktivieren (verhindert Auto-Reconnect bei Boot)
    Write-Output "Deaktiviere RestoreConnection..."
    try {
        `$null = New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\NetworkProvider" ``
            -Name "RestoreConnection" ``
            -PropertyType DWord ``
            -Value 0 ``
            -Force ``
            -ErrorAction Stop
        Write-Output "RestoreConnection erfolgreich deaktiviert"
    }
    catch {
        Write-Warning "RestoreConnection konnte nicht gesetzt werden (ggf. fehlende Rechte): `$(`$_.Exception.Message)"
        # Kein Fehler - wird ignoriert
    }
    
    # Verbindung testen
    Write-Output "Teste Verbindung..."
    if (Test-Path "`${driveLetter}:") {
        Write-Output "Laufwerk `${driveLetter}: erfolgreich verbunden und erreichbar!"
        `$exitCode = 0
    }
    else {
        Write-Warning "Laufwerk wurde verbunden, ist aber nicht erreichbar. Prüfe Berechtigungen!"
        `$exitCode = 1
    }
}
catch {
    Write-Error "Fehler beim Verbinden des Laufwerks: `$(`$_.Exception.Message)"
    `$exitCode = 1
}
finally {
    Stop-Transcript
}

exit `$exitCode
"@

# Dateinamen generieren - verwende Freigabename aus UNC-Pfad
$shareNameClean = $shareNamePath -replace '[^\w\$-]', '_'
$outputFileName = "LS_$($shareNameClean)_$($driveLetter).ps1"
$outputPath = Join-Path $PSScriptRoot $outputFileName

# Script speichern
try {
    $scriptContent | Out-File -FilePath $outputPath -Encoding UTF8 -Force
    Write-Host "Script erfolgreich erstellt!" -ForegroundColor Green
    Write-Host "Pfad: $outputPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Deployment-Hinweise:" -ForegroundColor Yellow
    Write-Host "1. Script in Intune hochladen (Devices > Scripts and remediations)" -ForegroundColor Gray
    Write-Host "2. 'Run this script using the logged on credentials' = YES" -ForegroundColor Gray
    Write-Host "3. 'Enforce script signature check' = NO" -ForegroundColor Gray
    Write-Host "4. Zuweisen an Benutzergruppe" -ForegroundColor Gray
}
catch {
    Write-Error "Fehler beim Erstellen des Scripts: $($_.Exception.Message)"
}
