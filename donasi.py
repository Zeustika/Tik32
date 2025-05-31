import requests
import sys
import json
import time
from time import sleep
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.events import ConnectEvent, GiftEvent
import asyncio
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import logging

try:
    from TikTokLive.client.web.web_settings import WebDefaults
    TIKTOKLIVE_WEBDEFAULTS_AVAILABLE = True
except ImportError:
    TIKTOKLIVE_WEBDEFAULTS_AVAILABLE = False

load_dotenv()

console = Console()

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG = {
    'ESP32_PORT': 80,
    'MAX_RETRIES': 5,
    'RETRY_DELAY': 15,
    'CONNECTION_TIMEOUT': 10,
    'RATE_LIMIT_WAIT': 21600 
}

def display_banner():
    """Display application banner"""
    console.print("""
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║                TikTok Live ESP32 Gift Controller             ║
║                   Enhanced Version 2.0                       ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]
""")

def validate_arguments():
    """Validate command line arguments"""
    if len(sys.argv) < 3:
        console.print("[bold red]❌ Error:[/bold red] Missing required arguments")
        console.print("[bold yellow]Usage:[/bold yellow] python donasi.py <tiktok_username> <esp32_ip>")
        console.print("[bold yellow]Example:[/bold yellow] python donasi.py myusername 192.168.1.100")
        sys.exit(1)
    
    username = sys.argv[1].replace('@', '')
    esp32_ip = sys.argv[2]
    
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if not re.match(ip_pattern, esp32_ip):
        console.print(f"[bold red]❌ Error:[/bold red] Invalid IP address format: {esp32_ip}")
        console.print("[bold yellow]💡 Tip:[/bold yellow] Use format like 192.168.1.100")
        sys.exit(1)
    
    return username, esp32_ip

def load_gift_configuration():
    """Load gift configuration from JSON file"""
    try:
        with open('gift_tiktok.json', 'r', encoding='utf-8') as file:
            gift_config = json.load(file)
        console.print(f"[bold green]✅ Loaded {len(gift_config)} gift configurations[/bold green]")
        return gift_config
    except FileNotFoundError:
        console.print("[bold red]❌ Error: 'gift_tiktok.json' file not found![/bold red]")
        console.print("[bold yellow]💡 Solution:[/bold yellow] Create gift_tiktok.json with gift values")
        console.print("Example content:")
        console.print(json.dumps({"Rose": 1, "TikTok": 1, "Heart": 5}, indent=2))
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[bold red]❌ Error: Invalid JSON in gift_tiktok.json: {e}[/bold red]")
        sys.exit(1)

def test_esp32_connection(esp32_ip):
    """Test ESP32 connectivity with detailed feedback"""
    console.print(f"[bold blue]🔄 Testing ESP32 connection at {esp32_ip}:{CONFIG['ESP32_PORT']}...[/bold blue]")
    
    headers = {
        'User-Agent': 'TikTokLive-ESP32-Controller-Test/2.0',
        'Connection': 'close'
    }

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Connecting to ESP32...", total=None)
            response = requests.get(
                f"http://{esp32_ip}:{CONFIG['ESP32_PORT']}",
                headers=headers,
                timeout=CONFIG['CONNECTION_TIMEOUT']
            )
            progress.remove_task(task)
        
        console.print(f"[bold green]✅ ESP32 connected successfully (Status: {response.status_code})[/bold green]")
        
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                info = response.json()
                console.print(f"[dim]ESP32 Info: {info}[/dim]")
        except:
            pass
        
        return True
    except requests.exceptions.Timeout:
        console.print(f"[bold red]❌ ESP32 connection timeout[/bold red]")
        console.print("[bold yellow]⚠️  Warning: Commands may fail, but continuing anyway[/bold yellow]")
        return False
    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]❌ ESP32 connection refused or unreachable[/bold red]")
        console.print("[bold yellow]💡 Check:[/bold yellow] ESP32 IP, WiFi connection, and power")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ ESP32 connection error: {e}[/bold red]")
        return False

def get_tiktok_library_info():
    """Get information about the TikTokLive library version"""
    try:
        import TikTokLive
        version = getattr(TikTokLive, '__version__', 'Unknown')
        console.print(f"[bold cyan]📦 TikTokLive version 2[/bold cyan]")
        return version
    except Exception as e:
        console.print(f"[bold yellow]⚠️  Cannot determine TikTokLive version: {e}[/bold yellow]")
        return None

def create_tiktok_client(username):
    """Create TikTok client with proper configuration and multiple fallback strategies"""
    get_tiktok_library_info()
    api_key = os.getenv('EULERSTREAM_API_KEY')
    if api_key:
        console.print("[bold green]🔑 EulerStream API key detected[/bold green]")
        if TIKTOKLIVE_WEBDEFAULTS_AVAILABLE:
            try:
                WebDefaults.tiktok_sign_api_key = api_key
                console.print("[bold green]✅ EulerStream API key applied to TikTokLive WebDefaults[/bold green]")
            except Exception as e:
                console.print(f"[bold yellow]⚠️ Error setting EulerStream API key in WebDefaults: {e}[/bold yellow]")
        else:
            console.print("[bold yellow]⚠️ WebDefaults not available. Cannot set EulerStream API key via WebDefaults.[/bold yellow]")
            console.print("[bold yellow]💡 Note: API key config may vary by library version.[/bold yellow]")
    else:
        console.print("[bold yellow]⚠️  No API Key found - using default configuration[/bold yellow]")
        console.print("[bold yellow]💡 Consider EulerStream for potentially better stability.[/bold yellow]")
    
    try:
        console.print("[bold blue]🔄 Strategy 1: Standard initialization (unique_id)[/bold blue]")
        client = TikTokLiveClient(unique_id=username)
        console.print("[bold green]✅ Success with standard method[/bold green]")
        return client
    except Exception as e:
        console.print(f"[bold yellow]⚠️  Strategy 1 failed: {str(e)[:100]}...[/bold yellow]")
    
    try:
        console.print("[bold blue]🔄 Strategy 2: Positional argument[/bold blue]")
        client = TikTokLiveClient(username)
        console.print("[bold green]✅ Success with positional argument[/bold green]")
        return client
    except Exception as e:
        console.print(f"[bold yellow]⚠️  Strategy 2 failed: {str(e)[:100]}...[/bold yellow]")
    
    try:
        console.print("[bold blue]🔄 Strategy 3: Username parameter[/bold blue]")
        client = TikTokLiveClient(username=username)
        console.print("[bold green]✅ Success with username parameter[/bold green]")
        return client
    except Exception as e:
        console.print(f"[bold yellow]⚠️  Strategy 3 failed: {str(e)[:100]}...[/bold yellow]")
    
    session_id = os.getenv('TIKTOK_SESSION_ID')
    if session_id:
        try:
            console.print("[bold blue]🔄 Strategy 4: With session ID[/bold blue]")
            client = TikTokLiveClient(unique_id=username, sessionid=session_id)
            console.print("[bold green]✅ Success with session ID[/bold green]")
            return client
        except Exception as e:
            console.print(f"[bold yellow]⚠️  Strategy 4 (session ID) failed: {str(e)[:100]}...[/bold yellow]")
    
    raise Exception("All TikTok client creation strategies failed.")

class Statistics:
    def __init__(self):
        self.data = {
            'session_start': datetime.now(), 'total_gifts': 0, 'total_points': 0,
            'total_commands': 0, 'successful_commands': 0, 'failed_commands': 0,
            'unique_users': set(), 'top_gifters': {}, 'gift_types': {}
        }
    
    def add_gift(self, gift_name, points, user, repeat_count):
        self.data['total_gifts'] += repeat_count
        self.data['total_points'] += points
        self.data['unique_users'].add(user)
        self.data['top_gifters'][user] = self.data['top_gifters'].get(user, 0) + points
        self.data['gift_types'][gift_name] = self.data['gift_types'].get(gift_name, 0) + repeat_count
    
    def add_command_result(self, success):
        self.data['total_commands'] += 1
        if success: self.data['successful_commands'] += 1
        else: self.data['failed_commands'] += 1
    
    def display_summary(self):
        table = Table(title="Session Statistics", title_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        duration = datetime.now() - self.data['session_start']
        table.add_row("Session Duration", str(duration).split('.')[0])
        table.add_row("Total Gifts", str(self.data['total_gifts']))
        table.add_row("Total Points", str(self.data['total_points']))
        table.add_row("Unique Users", str(len(self.data['unique_users'])))
        table.add_row("Commands Sent", f"{self.data['successful_commands']}/{self.data['total_commands']}")
        if self.data['top_gifters']:
            top_gifter = sorted(self.data['top_gifters'].items(), key=lambda item: item[1], reverse=True)[0]
            table.add_row("Top Gifter", f"{top_gifter[0]} ({top_gifter[1]} pts)")
        console.print(table)

stats = Statistics()

def send_relay_command(relay_command, duration, user="Unknown", esp32_ip=""):
    if not esp32_ip:
        console.print("[bold red]❌ ESP32 IP not provided to send_relay_command.[/bold red]")
        stats.add_command_result(False)
        return

    payload = {
        "relay": relay_command, "waktu": duration, "user": user,
        "timestamp": datetime.now().isoformat()
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'TikTokLive-ESP32-Controller/2.0',
        'Connection': 'close'
    }
    
    try:
        url = f"http://{esp32_ip}:{CONFIG['ESP32_PORT']}/gift"
        console.print(f"[dim]📤 Command: {relay_command} ({duration}s) → {user} to {esp32_ip}[/dim]")
        
        response = requests.post(
            url, headers=headers, json=payload, timeout=CONFIG['CONNECTION_TIMEOUT']
        )
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                status_msg = response_data.get('status', 'Command executed')
                console.print(f"[bold green]✅ ESP32: {status_msg}[/bold green]")
                stats.add_command_result(True)
            except json.JSONDecodeError:
                console.print(f"[bold green]✅ ESP32: Command sent (Status: {response.status_code})[/bold green]")
                stats.add_command_result(True)
        else:
            console.print(f"[bold red]❌ ESP32 Error: HTTP {response.status_code}[/bold red]")
            if response.text: console.print(f"[dim]Response: {response.text[:100]}[/dim]")
            stats.add_command_result(False)
            
    except requests.exceptions.Timeout:
        console.print(f"[bold red]⏱️  ESP32 Timeout: Command may not have been received[/bold red]")
        stats.add_command_result(False)
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ ESP32 Request failed: {str(e)[:100]}[/bold red]")
        stats.add_command_result(False)

def determine_relay_action(points):
    if points <= 2: return "relay1nyala", 1
    elif 3 <= points <= 19: return "semuarelaynyala", 2
    elif 20 <= points <= 50: return "semuarelaynyala", 3
    elif 51 <= points <= 100: return "relay1nyala", 4
    elif 101 <= points <= 200: return "relay2nyala", 5
    elif 201 <= points <= 500: return "semuarelaynyala", 7
    else: return "semuarelaynyala", 10

def main():
    display_banner()
    username, esp32_ip = validate_arguments()
    console.print(f"[bold cyan]🎯 Target:[/bold cyan] @{username}")
    console.print(f"[bold cyan]🌐 ESP32:[/bold cyan] {esp32_ip}:{CONFIG['ESP32_PORT']}")
    console.print("="*60)
    
    gift_config = load_gift_configuration()
    esp32_connected = test_esp32_connection(esp32_ip)
    
    try:
        client = create_tiktok_client(username)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to initialize TikTok client: {e}[/bold red]")
        sys.exit(1)
    
    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        console.print(f"[bold green]🔴 LIVE: Connected to @{event.unique_id}[/bold green]")
        try:
            if client.room_id: console.print(f"[bold cyan]🆔 Room ID: {client.room_id}[/bold cyan]")
            else: console.print("[bold cyan]🆔 Room ID: Not available immediately.[/bold cyan]")
        except AttributeError: console.print("[bold cyan]🆔 Room ID: Not available on connect.[/bold cyan]")
        except Exception as e: console.print(f"[bold yellow]⚠️ Could not retrieve Room ID: {e}[/bold yellow]")
        console.print("[bold cyan]👀 Monitoring gifts...[/bold cyan]")
        console.print("="*60)
    
    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent): 
        try:
            gift_name = event.gift.name
            user_display_name = event.user.nickname if event.user.nickname else event.user.unique_id
            repeat_count = getattr(event.gift, 'repeat_count', 1)
            if repeat_count == 0: repeat_count = 1
            
            if gift_name in gift_config:
                points = gift_config[gift_name] * repeat_count
                stats.add_gift(gift_name, points, user_display_name, repeat_count)
                console.print(
                    f"[bold yellow]🎁 {user_display_name}[/bold yellow] → "
                    f"[bold cyan]{repeat_count}x {gift_name}[/bold cyan] → "
                    f"[bold magenta]{points} points[/bold magenta]"
                )
                if esp32_connected:
                    relay_command, duration = determine_relay_action(points)
                    send_relay_command(relay_command, duration, user_display_name, esp32_ip)
                
                console.print(
                    f"[dim]📊 Session: {stats.data['total_gifts']} gifts | "
                    f"{stats.data['total_points']} points | "
                    f"{len(stats.data['unique_users'])} users | "
                    f"{stats.data['successful_commands']}/{stats.data['total_commands']} commands[/dim]"
                )
            else:
                console.print(f"[bold red]❓ Unknown gift: '{gift_name}' (x{repeat_count}) from {user_display_name}[/bold red]")
                console.print(f"[dim]💡 Add to gift_tiktok.json: \"{gift_name}\": 1[/dim]")
        except Exception as e:
            logger.error(f"Error processing gift: {e}", exc_info=True)
            console.print(f"[bold red]❌ Error processing gift: {e}[/bold red]")
            if isinstance(e, AttributeError) and 'event.gift' in str(e).lower():
                 try:
                     console.print(f"[bold yellow]🔧 Debug: event.gift (type: {type(event.gift).__name__}):[/bold yellow]")
                     attrs = ['id', 'name', 'diamond_count', 'type', 'combo', 'can_be_repeated', 'count', 'actual_repeat_count', 'repeat_count']
                     for attr in attrs: console.print(f"  - {attr}: {getattr(event.gift, attr, 'Not found')}")
                 except Exception as ex_debug: console.print(f"[bold red]🚨 Debug info error: {ex_debug}[/bold red]")
            console.print(f"[dim]Gift Event Data (short): {str(event)[:200]}[/dim]")
    
    def connect_with_retries():
        retry_count = 0
        last_error = None
        while retry_count < CONFIG['MAX_RETRIES']:
            try:
                console.print(f"[bold blue]🔄 Connecting @{username} (Attempt {retry_count + 1}/{CONFIG['MAX_RETRIES']})[/bold blue]")
                if retry_count > 0: time.sleep(CONFIG['RETRY_DELAY'])
                client.run()
                console.print("[bold yellow]📡 Connection ended or client stopped.[/bold yellow]")
                last_error = None; break
            except KeyboardInterrupt:
                console.print("\n[bold yellow]⏹️  Stopped by user.[/bold yellow]"); last_error = None; break
            except Exception as e:
                last_error = e; error_str = str(e).lower(); logger.error(f"Connection attempt {retry_count + 1} failed: {e}", exc_info=True)
                if any(term in error_str for term in ["rate limit", "too many", "429"]):
                    console.print(f"[bold red]🚫 Rate Limited: {e}[/bold red]")
                    wait_match = re.search(r"try again in (\d+)", error_str)
                    wait_time = int(wait_match.group(1)) if wait_match else CONFIG['RATE_LIMIT_WAIT']
                    actual_wait = max(wait_time, CONFIG['RATE_LIMIT_WAIT'])
                    console.print(f"[bold yellow]⏳ Waiting {actual_wait // 3600}h ({actual_wait}s)...[/bold yellow]")
                    time.sleep(actual_wait); console.print("[bold yellow]🛑 Stopping. Restart manually.[/bold yellow]"); break
                elif any(term in error_str for term in ["connection", "network", "timeout", "unreachable"]):
                    console.print(f"[bold red]🌐 Network error: {e}[/bold red]")
                elif any(term in error_str for term in ["not found", "invalid user", "user not live", "live has ended"]):
                    console.print(f"[bold red]👤 User/Stream error: {e}[/bold red]"); break
                else: console.print(f"[bold red]❌ Unexpected error: {e}[/bold red]")
                retry_count += 1
                if retry_count >= CONFIG['MAX_RETRIES']: console.print(f"[bold red]❌ Max retries reached.[/bold red]"); break
                console.print(f"[bold yellow]🔄 Will retry in {CONFIG['RETRY_DELAY']}s...[/bold yellow]")
        
        if retry_count >= CONFIG['MAX_RETRIES'] and last_error and not isinstance(last_error, KeyboardInterrupt):
            console.print(f"[bold red]❌ Max retries ({CONFIG['MAX_RETRIES']}) reached. Stopping.[/bold red]")
        console.print("\n" + "="*60 + "\n[bold cyan]📊 SESSION SUMMARY[/bold cyan]\n" + "="*60)
        stats.display_summary()
    
    try:
        connect_with_retries()
    except KeyboardInterrupt: console.print("\n[bold yellow]👋 Program terminated by user.[/bold yellow]"); stats.display_summary()
    except Exception as e:
        logger.critical(f"Unexpected program error: {e}", exc_info=True)
        console.print(f"\n[bold red]❌ Unexpected program error: {e}[/bold red]"); stats.display_summary()
    finally:
        console.print("[bold cyan]Thank you for using TikTok Live ESP32 Controller![/bold cyan]")

if __name__ == '__main__':
    main()
