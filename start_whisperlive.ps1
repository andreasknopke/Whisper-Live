# Konfiguration
$CONDA_PATH = "C:\Users\Andre.AUDIO-WS1\miniconda3\Scripts\conda.exe"
$ENV_NAME = "med_transcription"
$WORKING_DIR = "D:\GitHub\whisper\live"
$PORT = 5001
$WAIT_TIME = 10 

Write-Host "--- WhisperLive WSS Monitor & Logs gestartet ---" -ForegroundColor Green
Write-Host "Logs werden direkt in diesem Fenster ausgegeben." -ForegroundColor Gray
Write-Host "--------------------------------------------------"

function Start-WhisperServer {
    Write-Host "$(Get-Date): Starte Fast-Whisper Prozess (med_live_server.py)..." -ForegroundColor Cyan
    
    # Der '&' Operator startet den Prozess im aktuellen Fenster-Stream.
    # Wir wechseln kurz ins Verzeichnis, damit Python alle Pfade findet.
    Push-Location $WORKING_DIR
    try {
        & $CONDA_PATH run -n $ENV_NAME python "med_live_server.py"
    }
    finally {
        Pop-Location
    }
}

while($true) {
    # Prüfen, ob der Port belegt ist und ob der Status auf 'Listen' steht
    $connection = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($null -eq $connection) {
        Write-Host "$(Get-Date): WSS-Port $PORT ist nicht belegt. Starte Server neu..." -ForegroundColor Red
        Start-WhisperServer
    } 
    elseif ($connection.State -ne "Listen") {
        Write-Host "$(Get-Date): Port $PORT blockiert (Status: $($connection.State)). Bereinige PID $($connection.OwningProcess)..." -ForegroundColor Yellow
        Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Start-WhisperServer
    }
    else {
        # Server läuft und Port ist im Status 'Listen'
        # Wir geben eine kurze Info aus, damit man sieht, dass das Monitoring noch lebt
        # (Optional: Diese Zeile entfernen, wenn sie zu viel 'Spam' im Log erzeugt)
        # Write-Host "." -NoNewline 
    }

    Start-Sleep -Seconds $WAIT_TIME
}