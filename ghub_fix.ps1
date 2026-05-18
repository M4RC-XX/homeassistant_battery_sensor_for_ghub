# Prüfen, ob der Portproxy bereits existiert
$proxyExists = netsh interface portproxy show all | Select-String "9010"

if (-not $proxyExists) {
    # Falls gelöscht, Proxy neu einrichten
    netsh interface portproxy add v4tov4 listenport=9010 listenaddress=0.0.0.0 connectport=9010 connectaddress=127.0.0.1
}

# Prüfen, ob die Firewall-Regel existiert
$fwExists = Get-NetFirewallRule -DisplayName "Logitech G Hub WebSocket Proxy" -ErrorAction SilentlyContinue

if (-not $fwExists) {
    # Falls gelöscht, Firewall neu öffnen
    netsh advfirewall firewall add rule name="Logitech G Hub WebSocket Proxy" dir=in action=allow protocol=TCP localport=9010
}