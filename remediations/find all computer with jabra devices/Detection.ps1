# Detection Script for Intune Remediations

# Check for Jabra Audio Devices
$JabraDevice = Get-PnpDevice | Where-Object { $_.Class -eq "AudioEndpoint" -and $_.FriendlyName -like "*Jabra*" }

if ($JabraDevice) {
    # Jabra device found, indicating an issue
    Write-Output "Jabra Audio Device detected."
    exit 1
} else {
    # No Jabra device found, no issue
    Write-Output "No Jabra Audio Device detected."
    exit 0
}
