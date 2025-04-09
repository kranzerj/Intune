#creates a SharePoint Mount PowerShell Script like https://github.com/tabs-not-spaces/CodeDump/blob/master/Sync-SharepointFolder/Sync-SharepointFolder.ps1  and assisted at the necessary steps
#GNU General Public License v3.0
#https://github.com/kranzerj/Intune/tree/main/automatischer%20SP_sync%20ersteller
#ChatGPT 4o mini



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
    
    # Trenne listId und optional folderId
    list_id_part = url.split("&listId=")[1].split("&")[0]
    list_id = list_id_part.split("&folderId=")[0]  # ListId bis zur folderId
    folder_id = None
    if "&folderId=" in url:
        folder_id = url.split("&folderId=")[1].split("&")[0]
    
    web_url = url.split("webUrl=")[1].split("&version=1")[0]
    kurzname = url.split("sharepoint.com/sites/")[1].split("&version=1")[0]

    return site_id, web_id, list_id, web_url, kurzname, folder_id

def create_powershell_script(params):
    # Baue das PowerShell-Skript mit Platzhaltern für Parameter
    # Nur wenn folderId vorhanden ist, wird es in das PowerShell Skript aufgenommen
    if params['folderId']:
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
        [string]$syncPath,
        [string]$folderId
    )
    try {{
        Add-Type -AssemblyName System.Web
        #Encode site, web, list, url & email
        [string]$siteId = [System.Web.HttpUtility]::UrlEncode($siteId)
        [string]$webId = [System.Web.HttpUtility]::UrlEncode($webId)
        [string]$listId = [System.Web.HttpUtility]::UrlEncode($listId)
        [string]$userEmail = [System.Web.HttpUtility]::UrlEncode($userEmail)
        [string]$webUrl = [System.Web.HttpUtility]::UrlEncode($webUrl)
        [string]$folderId = [System.Web.HttpUtility]::UrlEncode($folderId)
        #build the URI
        $uri = New-Object System.UriBuilder
        $uri.Scheme = "odopen"
        $uri.Host = "sync"
        $uri.Query = "siteId=$siteId&webId=$webId&listId=$listId&userEmail=$userEmail&folderId=$folderId&webUrl=$webUrl&listTitle=$listTitle&webTitle=$webTitle"
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
        folderId  = "{params['folderId']}"
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
    else:
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
        $uri.Query = "siteId=$siteId&webId=$webId&listId=$listId&userEmail=$userEmail&webUrl=$webUrl&listTitle=$listTitle&webTitle=$webTitle"
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
    web_title = get_input("enter Name of the SharePoint Library (e.g.: Contoso File Sharing): ")
    list_title = get_input("enter Name of the SharePoint Library (e.g.: Documents): ")
    entraid_name = get_input("Name of the Entra ID Tenant on which the library is located: ")
    url = get_input("enter Library Sync URL: ")
    
    # Verarbeite die URL
    site_id, web_id, list_id, web_url, kurzname, folder_id = process_url(url)

    params = {
        "siteId": site_id,
        "webId": web_id,
        "listId": list_id,
        "webUrl": web_url,
        "kurzname": kurzname,
        "webTitle": web_title,
        "listTitle": list_title,
        "entraidname": entraid_name,
        "folderId": folder_id
    }

    # Prüfe, ob der Ordner existiert, andernfalls erstellen
    folder = "ready-made scripts"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Dateiname
    file_name = os.path.join(folder, f"{kurzname}.ps1")

    # Überprüfen, ob die Datei bereits existiert
    if os.path.exists(file_name):
        overwrite = get_input(f"The File {file_name} already exists. Should it be replaced? (y/n): ")
        if overwrite.lower() != 'y':
            print("The script is not overwritten. The End")
            return

    # PowerShell-Skript erstellen
    ps_script = create_powershell_script(params)

    # Schreibe das Skript in die Datei
    with open(file_name, 'w') as file:
        file.write(ps_script)

    print(f"The PowerShell script was saved under {file_name}")

    # Gebe verwendete Parameter aus
    print("\nparameters used:")
    for key, value in params.items():
        print(f"{key}: {value}")

    # Öffne den Explorer im Zielordner
    os.system(f'explorer "{os.path.abspath(folder)}"')

    # Öffne den Standardbrowser mit der URL
    os.system("start https://intune.microsoft.com/#view/Microsoft_Intune_DeviceSettings/PowershellScriptsWizard")

    # Zeige den Hinweistext an
    print(f"""
Intune will now open. Create a script there with the following name. For example SP_Sync_{kurzname}
In the next step, select the script that has been created.
leave Run this script using the logged on credentials on Yes
set Enforce script signature check auf No 
and leave Run script in 64 bit PowerShell Host on no

Assign the script exclusively to the relevant group

please press a button to close the script 
""")

    input()  # Wait for keystroke

if __name__ == "__main__":
    main()
