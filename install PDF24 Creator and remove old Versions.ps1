# Define the registry paths to search for uninstall entries
$uninstallPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)

foreach ($path in $uninstallPaths) {
    # Get all subkeys in the current uninstall path
    $subKeys = Get-ChildItem -Path $path

    foreach ($subKey in $subKeys) {
        # Get the DisplayName value of the current subkey
        $displayName = Get-ItemProperty -Path $subKey.PSPath -Name DisplayName -ErrorAction SilentlyContinue

        if ($null -ne $displayName -and $displayName.DisplayName -like "PDF24*") {
            # Get the QuietUninstallString value
            $quietUninstallString = Get-ItemProperty -Path $subKey.PSPath -Name QuietUninstallString -ErrorAction SilentlyContinue

            if ($null -ne $quietUninstallString) {
                # Execute the QuietUninstallString command
                Write-Host "Uninstalling: $($displayName.DisplayName)"
                $command = $quietUninstallString.QuietUninstallString
                Start-Process -FilePath "cmd.exe" -ArgumentList "/c $command" -Wait
            }
        }
    }
}



.\pdf24-creator-11.18.0-x64.msi AUTOUPDATE=No DESKTOPICONS=Yes FAXPRINTER=No REGISTERREADER=No /QN
