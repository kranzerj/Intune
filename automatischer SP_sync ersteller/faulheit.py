#creats a SharePoint Mount PowerShell Script like https://github.com/tabs-not-spaces/CodeDump/blob/master/Sync-SharepointFolder/Sync-SharepointFolder.ps1  and assisted at the necessary steps
#GNU General Public License v3.0

import os
import urllib.parse

def get_input(prompt):
    return input(prompt)

def process_url(url):
    # Entferne Escape-Sequenzen aus der URL
    url = urllib.parse.unquote(url)

    # Extrahiere Parameter aus der URL
    site_id = url.split("&siteId={")[1].split("}")[0]
    web_id = url.split("&webId={")[1].split("}")[0]
    list_id = url.split("&listId=")[1].split("&webUrl=")[0]
    web_url = url.split("webUrl=")[1].split("&version=1")[0]
    kurzname = url.split("sharepoint.com/sites/")[1].split("&version=1")[0]

    return site_id, web_id, list_id, web_url, kurzname

def create_powershell_script(params):
    ps_script = f"""
#based on: https://github.com/tabs-not-spaces/CodeDump/blob/master/Sync-SharepointFolder/Sync-SharepointFolder.ps1 
#region Functions
function Sync-SharepointLocation {{
    param (
        [guid]$siteId,
        [guid]$webId,
        [guid]$listId,
        [mailaddress]$userEmail,
        [string]$webUrl,
        [string]$webTitle,
        [string]$listTitle,
        [string]$syncPath
    )
    try {{
        Add-Type -AssemblyName System.Web
        #Encode site, web, list, url & email
        [string]$siteId = [System.Web.HttpUtility]::UrlEncode($siteId)
        [string]$webId = [System.Web.HttpUtility]::UrlEncode($webId)
        [string]$listId = [System.Web.HttpUtility]::UrlEncode($listId)
        [string]$userEmail = [System.Web.HttpUtility]::UrlEncode($userEmail)
        [string]$webUrl = [System.Web.HttpUtility]::UrlEncode($webUrl)
        #build the URI
        $uri = New-Object System.UriBuilder
        $uri.Scheme = "odopen"
        $uri.Host = "sync"
        $uri.Query = "siteId={params['siteId']}&webId={params['webId']}&listId={params['listId']}&userEmail=$userEmail&webUrl={params['webUrl']}&listTitle={params['listTitle']}&webTitle={params['webTitle']}"
        #launch the process from URI
        Write-Host $uri.ToString()
        start-process -filepath $($uri.ToString())
    }}
    catch {{
        $errorMsg = $_.Exception.Message
    }}
    if ($errorMsg) {{
        Write-Warning "Sync failed."
        Write-Warning $errorMsg
    }}
    else {{
        Write-Host "Sync completed."
        while (!(Get-ChildItem -Path $syncPath -ErrorAction SilentlyContinue)) {{
            Start-Sleep -Seconds 2
            write-host $syncPath
        }}
        return $true
    }}    
}}
#endregion
#region Main Process
try {{
    #region Sharepoint Sync
    [mailaddress]$userUpn = cmd /c "whoami/upn"
    $params = @{{
        #replace with data captured from your sharepoint site.
        siteId    = "{params['siteId']}"
        webId     = "{params['webId']}"
        listId    = "{params['listId']}"
        userEmail = $userUpn
        webUrl    = "{params['webUrl']}"
        webTitle  = "{params['webTitle']}"
        listTitle = "{params['listTitle']}"
        entraidname = "{params['entraidname']}"
    }}
    $params.syncPath  = "$(split-path $env:onedrive)\\$($params.entraidname)\\$($params.webTitle) - $($Params.listTitle)"
    Write-Host "SharePoint params:"
    $params | Format-Table
    if (!(Test-Path $($params.syncPath))) {{
        Write-Host "Sharepoint folder not found locally, will now sync.." -ForegroundColor Yellow
        $sp = Sync-SharepointLocation @params
        if (!($sp)) {{
            Throw "Sharepoint sync failed."
        }}
    }}
    else {{
        Write-Host "Location already syncronized: $($params.syncPath)" -ForegroundColor Yellow
    }}
    #endregion
}}
catch {{
    $errorMsg = $_.Exception.Message
}}
finally {{
    if ($errorMsg) {{
        Write-Warning $errorMsg
        Throw $errorMsg
    }}
    else {{
        Write-Host "Completed successfully.."
    }}
}}
#endregion
"""
    return ps_script

def main():
    web_title = get_input("Name der SharePoint Bibliothek (z.B.: Kunde 123 Datenaustausch) eingeben: ")
    list_title = get_input("Name der SharePoint Seite (z.B.: Documents) eingeben: ")
    entraid_name = get_input("Name des Entra ID Tenant (z.B: COUNT IT) ")
    url = get_input("Bibliotheks ID URL eingeben: ")

    # Verarbeite die URL
    site_id, web_id, list_id, web_url, kurzname = process_url(url)

    params = {
        "siteId": site_id,
        "webId": web_id,
        "listId": list_id,
        "webUrl": web_url,
        "kurzname": kurzname,
        "webTitle": web_title,
        "listTitle": list_title,
        "entraidname": entraid_name
    }

    # Prüfe, ob der Ordner existiert, andernfalls erstellen
    folder = "fertige Scripts"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Dateiname
    file_name = os.path.join(folder, f"{kurzname}.ps1")

    # Überprüfen, ob die Datei bereits existiert
    if os.path.exists(file_name):
        overwrite = get_input(f"Die Datei {file_name} existiert bereits. Soll sie ersetzt werden? (y/n): ")
        if overwrite.lower() != 'y':
            print("Das Skript wird nicht überschrieben. Ende.")
            return

    # PowerShell-Skript erstellen
    ps_script = create_powershell_script(params)

    # Schreibe das Skript in die Datei
    with open(file_name, 'w') as file:
        file.write(ps_script)

    print(f"Das PowerShell-Skript wurde unter {file_name} gespeichert.")

    # Gebe verwendete Parameter aus
    print("\nVerwendete Parameter:")
    for key, value in params.items():
        print(f"{key}: {value}")

    # Öffne den Explorer im Zielordner
    os.system(f'explorer "{os.path.abspath(folder)}"')

    # Öffne den Standardbrowser mit der URL
    os.system("start https://intune.microsoft.com/#view/Microsoft_Intune_DeviceSettings/PowershellScriptsWizard")

    # Zeige den Hinweistext an
    print(f"""
es wird sich nun das Intune öffnen. Erstelle dort eine eines Skript mit dem z.B: den Namen SP_Sync_{kurzname}.
Wähle im nächsten Schritt das erstellte Skript aus.
belasse Run this script using the logged on credentials auf Yes
setze Enforce script signature check auf No 
und belasse Run script in 64 bit PowerShell Host auf nein

Weise das Skript ausschließlich der entsprechenden Gruppe zu

bitte eine Taste drücken um das Skript zu schließen 
""")

    input()  # Warte auf Tastendruck

if __name__ == "__main__":
    main()
