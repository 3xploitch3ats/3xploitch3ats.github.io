Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Vérifier si le script est exécuté avec des privilèges d'administrateur
function Test-Admin {
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    [System.Windows.Forms.MessageBox]::Show("Ce script doit être exécuté avec des privilèges d'administrateur.", "Erreur", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    exit
}

# Créer la fenêtre de l'interface graphique
$form = New-Object Windows.Forms.Form
$form.Text = "Injection DLL"
$form.Size = New-Object Drawing.Size(400, 250)
$form.StartPosition = "CenterScreen"

# Label pour la sélection du fichier DLL
$labelDll = New-Object Windows.Forms.Label
$labelDll.Text = "Sélectionnez le fichier DLL à injecter :"
$labelDll.AutoSize = $true
$labelDll.Location = New-Object Drawing.Point(10, 20)
$form.Controls.Add($labelDll)

# Bouton pour ouvrir la boîte de dialogue de sélection de fichier
$buttonFile = New-Object Windows.Forms.Button
$buttonFile.Text = "Choisir DLL"
$buttonFile.Location = New-Object Drawing.Point(10, 50)
$form.Controls.Add($buttonFile)

# Zone de texte pour afficher le chemin du fichier DLL sélectionné
$textboxFile = New-Object Windows.Forms.TextBox
$textboxFile.Location = New-Object Drawing.Point(110, 50)
$textboxFile.Size = New-Object Drawing.Size(250, 20)
$form.Controls.Add($textboxFile)

# Label pour la sélection du processus cible
$labelProcess = New-Object Windows.Forms.Label
$labelProcess.Text = "Sélectionnez le processus cible :"
$labelProcess.AutoSize = $true
$labelProcess.Location = New-Object Drawing.Point(10, 90)
$form.Controls.Add($labelProcess)

# ComboBox pour lister les processus en cours d'exécution
$comboBoxProcess = New-Object Windows.Forms.ComboBox
$comboBoxProcess.Location = New-Object Drawing.Point(10, 120)
$comboBoxProcess.Size = New-Object Drawing.Size(250, 20)
$comboBoxProcess.DropDownStyle = "DropDownList"
$form.Controls.Add($comboBoxProcess)

# Bouton OK pour lancer l'injection
$buttonOk = New-Object Windows.Forms.Button
$buttonOk.Text = "Injecter"
$buttonOk.Location = New-Object Drawing.Point(280, 120)
$form.Controls.Add($buttonOk)

# Fonction pour remplir la ComboBox avec les processus en cours d'exécution
function Load-Processes {
    $comboBoxProcess.Items.Clear()
    $processes = Get-Process | Sort-Object -Property ProcessName
    foreach ($process in $processes) {
        $comboBoxProcess.Items.Add("$($process.ProcessName) (ID: $($process.Id))")
    }
}

# Fonction pour ouvrir le sélecteur de fichier
$buttonFile.Add_Click({
    $openFileDialog = New-Object Windows.Forms.OpenFileDialog
    $openFileDialog.Filter = "DLL Files (*.dll)|*.dll|All Files (*.*)|*.*"
    if ($openFileDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $textboxFile.Text = $openFileDialog.FileName
    }
})

# Charger les processus dans la ComboBox au démarrage
Load-Processes

# Ajouter les types nécessaires pour l'injection DLL
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Injector
{
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr OpenProcess(uint processAccess, bool bInheritHandle, int processId);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint dwSize, out int lpNumberOfBytesWritten);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out IntPtr lpThreadId);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern bool CloseHandle(IntPtr hObject);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr GetModuleHandle(string lpModuleName);

    public const uint PROCESS_ALL_ACCESS = 0x001F0FFF;
    public const uint MEM_COMMIT = 0x00001000;
    public const uint PAGE_READWRITE = 0x04;
    public const uint THREAD_EXECUTE_READWRITE = 0x00000040;
}
"@

# Fonction pour injecter la DLL
function Inject-DLL {
    param (
        [string]$dllPath,
        [int]$processId
    )

    try {
        $hProcess = [Injector]::OpenProcess([Injector]::PROCESS_ALL_ACCESS, $false, $processId)
        if ($hProcess -eq [IntPtr]::Zero) {
            throw "Impossible d'ouvrir le processus cible. Code d'erreur : " + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        }

        $dllPathBytes = [System.Text.Encoding]::ASCII.GetBytes($dllPath + [char]0)
        $dllPathLength = $dllPathBytes.Length
        $lpAddress = [Injector]::VirtualAllocEx($hProcess, [IntPtr]::Zero, $dllPathLength, [Injector]::MEM_COMMIT, [Injector]::PAGE_READWRITE)
        if ($lpAddress -eq [IntPtr]::Zero) {
            throw "Impossible d'allouer la mémoire dans le processus cible. Code d'erreur : " + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        }

        $bytesWritten = 0
        if (-not [Injector]::WriteProcessMemory($hProcess, $lpAddress, $dllPathBytes, $dllPathLength, [ref]$bytesWritten)) {
            throw "Impossible d'écrire dans la mémoire du processus cible. Code d'erreur : " + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        }

        $kernel32Handle = [Injector]::GetModuleHandle("kernel32.dll")
        if ($kernel32Handle -eq [IntPtr]::Zero) {
            throw "Impossible de récupérer le handle de kernel32.dll. Code d'erreur : " + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        }

        $loadLibraryAddr = [Injector]::GetProcAddress($kernel32Handle, "LoadLibraryA")
        if ($loadLibraryAddr -eq [IntPtr]::Zero) {
            throw "Impossible de trouver l'adresse de LoadLibraryA. Code d'erreur : " + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        }

        $hThread = [IntPtr]::Zero
        if (-not [Injector]::CreateRemoteThread($hProcess, [IntPtr]::Zero, 0, $loadLibraryAddr, $lpAddress, 0, [ref]$hThread)) {
            throw "Impossible de créer le thread distant. Code d'erreur : " + [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        }

        [Injector]::CloseHandle($hThread)
        [Injector]::CloseHandle($hProcess)
        [System.Windows.Forms.MessageBox]::Show("DLL injectée avec succès.", "Succès", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, "Erreur", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
}

# Action lors du clic sur le bouton OK
$buttonOk.Add_Click({
    $selectedProcess = $comboBoxProcess.SelectedItem
    if ($selectedProcess -eq $null) {
        [System.Windows.Forms.MessageBox]::Show("Veuillez sélectionner un processus cible.", "Erreur", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return
    }

    $dllPath = $textboxFile.Text
    if (-not (Test-Path $dllPath)) {
        [System.Windows.Forms.MessageBox]::Show("Le fichier DLL sélectionné n'existe pas.", "Erreur", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return
    }

    $processId = [int]($selectedProcess -replace ".*ID: (\d+).*", '$1')
    Inject-DLL -dllPath $dllPath -processId $processId
})

$form.ShowDialog()
