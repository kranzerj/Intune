https://learn.microsoft.com/en-us/autopilot/requirements?tabs=configuration



Group Tags are existing

![](images/gt.png)

deployment profiles (in my case the full tag "default-LP24" ) and the script (in my case via the first letters of the group tag "default") are linked with the device
Script: https://github.com/kranzerj/Intune/blob/main/prerequisite-and-remove_bloatware/01.MS_crap/script.ps1



(device.devicePhysicalIds -any (_ -contains "[OrderID]:default-LP24"))
![](images/g1.png)





(device.devicePhysicalIds -any (_ -contains "[OrderID]:default"))
![](images/g2.png)



