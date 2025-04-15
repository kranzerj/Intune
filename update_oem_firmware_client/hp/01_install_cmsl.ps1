#use this as a Intune Win32App

# URL der Zielseite
$targetUrl = "https://www.hp.com/us-en/solutions/client-management-solutions/download.html"

# Setze den WebClient, um den Download zu starten
$webClient = New-Object System.Net.WebClient

# Lade den HTML-Inhalt der Zielseite herunter
$htmlContent = Invoke-WebRequest -Uri $targetUrl

# Verwende Regex, um den Link zu extrahieren, der mit hp-cmsl endet und .exe enthält
$downloadUrl = [regex]::Match($htmlContent.Content, "https://.*?/hp-cmsl.*?\.exe").Value

# Prüfen, ob ein passender Link gefunden wurde
if ($downloadUrl) {
    Write-Host "Gefundener Download-Link: $downloadUrl"

    # Setze den Zielpfad, um die Datei zu speichern
    $downloadPath = "$env:Temp\hp-cmsl.exe"

    # Datei herunterladen
    try {
        Write-Host "Lade Datei herunter..."
        $webClient.DownloadFile($downloadUrl, $downloadPath)
        Write-Host "Download abgeschlossen."

        # Installiere die Datei mit den erforderlichen Parametern
        Write-Host "Installiere die heruntergeladene Datei..."
        Start-Process -FilePath $downloadPath -ArgumentList "/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES" -Wait

        Write-Host "Installation abgeschlossen."
    }
    catch {
        Write-Error "Fehler beim Herunterladen oder Installieren der Datei: $_"
    }
} else {
    Write-Error "Kein gültiger Link für hp-cmsl-Download gefunden."
}
