# Function to show an OpenFileDialog to select an MP4 file
function Select-File {
    Add-Type -AssemblyName System.Windows.Forms
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $openFileDialog.Filter = "MP4 Files (*.mp4)|*.mp4"
    $openFileDialog.Title = "Select MP4 File"
    
    if ($openFileDialog.ShowDialog() -eq 'OK') {
        return $openFileDialog.FileName
    } else {
        Write-Host "No file selected."
        exit
    }
}

# Function to convert MP4 to WMA using ffmpeg.exe
function Convert-MP4ToWMA {
    param (
        [string]$inputFile
    )

    # Get the directory of the script or current directory
    $scriptDir = Get-Location

    # Path to ffmpeg.exe in the same directory as the script
    $ffmpegPath = Join-Path $scriptDir "ffmpeg.exe"

    # Check if ffmpeg.exe exists in the same directory as the script
    if (-not (Test-Path $ffmpegPath)) {
        Write-Host "ffmpeg.exe not found in the script directory. Please place ffmpeg.exe in the same directory as the script."
        exit
    }

    # Define the output file path
    $outputFile = [System.IO.Path]::ChangeExtension($inputFile, ".wma")

    # Run ffmpeg command to extract audio and convert it to WMA
    & $ffmpegPath -i $inputFile -vn -acodec wmav2 -b:a 192k $outputFile

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Conversion successful. Output saved to $outputFile"
    } else {
        Write-Host "Conversion failed."
    }
}

# Main script execution
$mp4File = Select-File
Convert-MP4ToWMA -inputFile $mp4File

# Pause to keep the PowerShell window open
pause
