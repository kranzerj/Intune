#based on: https://gist.githubusercontent.com/nicolonsky/fdfdf78a4db6f4ce5cf321ad208f339d/raw/359759f016a1673a352d921d536d1fd7e26491d0/AutoMountTeamSites.ps1
# ad Name of Site and ID at Line 12

#run in usercotext


$tenantAutoMountRegKey="HKLM:\SOFTWARE\Policies\Microsoft\OneDrive\TenantAutoMount"

$autoMountTeamSitesList= @{
    
    #Enter yyour SharePoint libraries to configure here as key/value pairs
    DemoTeamSite="Enter your encoded SharePoint library ID here"
}


if (-not (Test-Path $tenantAutoMountRegKey)){
    
    New-Item -Path $tenantAutoMountRegKey -Force

}


#add registry entries from the hashtable above
$autoMountTeamSitesList.GetEnumerator() | ForEach-Object {
        
    Set-ItemProperty -Path $tenantAutoMountRegKey -Name $PSItem.Key -Value $PSItem.Value -ErrorAction Stop
}

# speed up connection
$regPath = "HKCU:\Software\Microsoft\OneDrive\Accounts\Business1"
$regName = "TimerAutoMount"
$regValue = @(0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
if (-not (Test-Path $regPath)) {
    # Erstellen des Registrierungspfades, falls er nicht existiert
    New-Item -Path $regPath -Force
}
if (-not (Get-ItemProperty -Path $regPath -Name $regName -ErrorAction SilentlyContinue)) {
    # Erstellen des Registrierungseintrags, falls er nicht existiert
    New-ItemProperty -Path $regPath -Name $regName -Value $regValue -PropertyType Binary -Force
    Write-Output "Registrierungseintrag 'TimerAutoMount' wurde erstellt."
} else {
    Write-Output "Registrierungseintrag 'TimerAutoMount' existiert bereits."
}

