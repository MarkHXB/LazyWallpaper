Function GetPythonVersion {
    $pythonKey = Get-ItemProperty -Path "HKLM:\Software\Python\PythonCore\*" -ErrorAction SilentlyContinue
     if ($pythonKey) {
        $pythonVersion = $pythonKey.PSChildName
        Write-Host "Python is installed. Version: $pythonVersion"
        return $true;

     } else {
        Write-Host "Python is not installed."
        return $false;
     }
}

# Check if Python is installed
if (-not (GetPythonVersion)) {
    Write-Host "Python is not installed. Installing Python..."
    
    # Download Python installer
    $pythonInstallerUrl = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
    $pythonInstallerPath = Join-Path $env:TEMP 'python-3.10.0-amd64.exe'
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $pythonInstallerPath

    # Install Python
    Start-Process -Wait -FilePath $pythonInstallerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1"
    
     # Check if installation was successful
     if (GetPythonVersion) {
         Write-Host "Python is installed."
     } else {
        Write-Host "Python is not installed."
     }
}

# Check if requirements.txt exists
$requirementsFile = Join-Path $PSScriptRoot 'requirements.txt'
if (Test-Path $requirementsFile) {
    Write-Host "Found requirements.txt file. Installing Python packages..."
    
    # Install Python packages using pip
    & "python.exe" -m pip install -r $requirementsFile
    
    Write-Host "Python packages installation completed."
} else {
    Write-Host "requirements.txt file not found. Skipping package installation."
}
