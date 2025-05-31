import socket
import threading
import requests
import subprocess
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def get_local_ip():
    """Get the local IP address and network range"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        network_base = '.'.join(local_ip.split('.')[:-1])
        return local_ip, network_base
    except Exception as e:
        console.print(f"[bold red]Error getting local IP: {e}[/bold red]")
        return None, None

def check_device(ip, timeout=2):
    """Check if device at IP is an ESP32"""
    try:
        response = requests.get(f"http://{ip}", timeout=timeout)

        content = response.text.lower()
        headers = str(response.headers).lower()

        esp_indicators = [
            'esp32', 'esp-32', 'espressif', 
            'arduino', 'iot', 'relay',
            'tiktok', 'gift', 'donation'
        ]
        
        device_info = {
            'ip': ip,
            'status': response.status_code,
            'is_esp': False,
            'device_name': 'Unknown Device',
            'indicators': []
        }

        for indicator in esp_indicators:
            if indicator in content or indicator in headers:
                device_info['is_esp'] = True
                device_info['indicators'].append(indicator)

        name_patterns = [
            r'<title>(.*?)</title>',
            r'<h1>(.*?)</h1>',
            r'<h2>(.*?)</h2>',
            r'device[_\s]*name["\s]*[:=]["\s]*([^"<>\n]+)',
            r'name["\s]*[:=]["\s]*([^"<>\n]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                device_info['device_name'] = match.group(1).strip()
                break

        if device_info['device_name'] == 'Unknown Device':
            server = response.headers.get('Server', '')
            if server:
                device_info['device_name'] = f"HTTP Server ({server})"
            elif device_info['is_esp']:
                device_info['device_name'] = "esp32-D9AEEC"
            else:
                device_info['device_name'] = "esp32-D9AEEC"
        
        return device_info
        
    except requests.exceptions.ConnectTimeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None

def scan_network_range(network_base, max_workers=50):
    """Scan network range for HTTP devices"""
    devices = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning network...", total=254)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {
                executor.submit(check_device, f"{network_base}.{i}"): f"{network_base}.{i}"
                for i in range(1, 255)
            }

            for future in as_completed(future_to_ip):
                progress.update(task, advance=1)
                result = future.result()
                if result:
                    devices.append(result)
    
    return devices

def display_devices(devices):
    """Display found devices in a nice table"""
    if not devices:
        console.print("[bold red]Tidak ada perangkat HTTP yang ditemukan di jaringan![/bold red]")
        return []

    esp_devices = [d for d in devices if d['is_esp']]
    other_devices = [d for d in devices if not d['is_esp']]

    all_devices = esp_devices + other_devices
    
    table = Table(title="Perangkat yang Ditemukan di Jaringan")
    table.add_column("No", style="cyan", no_wrap=True)
    table.add_column("IP Address", style="magenta")
    table.add_column("Device Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Indicators", style="blue")
    
    for i, device in enumerate(all_devices, 1):
        device_type = "[bold green]ESP32/IoT[/bold green]" if device['is_esp'] else "HTTP Device"
        indicators = ", ".join(device['indicators']) if device['indicators'] else "-"
        
        table.add_row(
            str(i),
            device['ip'],
            device['device_name'],
            device_type,
            indicators
        )
    
    console.print(table)
    return all_devices

def main():
    console.print("[bold blue]🔍 ESP32 WiFi Scanner[/bold blue]")
    console.print("="*50)

    local_ip, network_base = get_local_ip()
    if not local_ip:
        console.print("[bold red]Gagal mendapatkan informasi jaringan lokal![/bold red]")
        sys.exit(1)
    
    console.print(f"[bold green]Local IP:[/bold green] {local_ip}")
    console.print(f"[bold green]Scanning network:[/bold green] {network_base}.1-254")
    console.print()
    
    # Scan network
    devices = scan_network_range(network_base)
    
    if not devices:
        console.print("[bold red]Tidak ada perangkat yang ditemukan![/bold red]")
        console.print("[bold yellow]Tip:[/bold yellow] Pastikan ESP32 sudah terhubung ke WiFi yang sama")
        return
    
    # Display devices
    all_devices = display_devices(devices)
    
    console.print()
    console.print("[bold cyan]Pilih perangkat ESP32 Anda:[/bold cyan]")
    console.print("[dim]Ketik nomor perangkat atau 0 untuk input manual[/dim]")
    
    while True:
        try:
            choice = input("\nPilih nomor (0 untuk manual): ").strip()
            
            if choice == "0":
                console.print("[bold yellow]Menggunakan input manual...[/bold yellow]")
                break
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(all_devices):
                selected_device = all_devices[choice_num - 1]
                console.print(f"[bold green]Dipilih:[/bold green] {selected_device['device_name']} ({selected_device['ip']})")

                with open('selected_esp32.tmp', 'w') as f:
                    f.write(selected_device['ip'])
                    
                break
            else:
                console.print(f"[bold red]Pilihan tidak valid! Masukkan angka 1-{len(all_devices)} atau 0[/bold red]")
                
        except ValueError:
            console.print("[bold red]Input tidak valid! Masukkan angka[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scanning dibatalkan[/bold yellow]")
            sys.exit(0)

if __name__ == "__main__":
    main()
