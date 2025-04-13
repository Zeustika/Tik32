import requests
import sys
import json
import time
from time import sleep
from rich.console import Console
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.events import ConnectEvent, GiftEvent

# Initialize console for better output
console = Console()

# TikTok username from command-line arguments
if len(sys.argv) < 2:
    console.print("[bold red]Error:[/bold red] TikTok username is required!")
    sys.exit(1)

tiktok_username = sys.argv[1]

# Define static ESP32 IP address (match with ESP32 code)
ESP32_IP = "192.168.187.116"  # Static IP configured in ESP32
ESP32_PORT = 80

# Load gift values from JSON file
try:
    with open('gift_tiktok.json', 'r') as file:
        gift_tiktok = json.load(file)
except FileNotFoundError:
    console.print("[bold red]Error: 'gift_tiktok.json' file not found![/bold red]")
    sys.exit(1)

# Create TikTokLive client
client = TikTokLiveClient(unique_id=tiktok_username)

# Function to send relay activation requests
def send_relay_command(relay_command, duration, user="Test User"):
    payload = {
        "relay": relay_command,
        "waktu": duration,
        "user": user
    }
    headers = {'Content-Type': 'application/json'}

    try:
        url = f"http://{ESP32_IP}:{ESP32_PORT}/gift"
        response = requests.post(url, headers=headers, json=payload, timeout=10)  # Increased timeout
        if response.status_code == 200:
            response_data = response.json()
            console.print(f"[bold green]Success: {response_data.get('status', 'No status received')}[/bold green]")
        else:
            console.print(f"[bold red]Error: {response.status_code} - {response.text}[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Request failed: {e}[/bold red]")

# Event handler when connected to TikTok Live
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    console.print(f"[bold green]Connected to TikTok user:[/bold green] {event.unique_id}!")

# Event handler for gift events
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift_name = event.gift.name
    repeat_count = event.repeat_count
    sender = event.user.unique_id

    if gift_name in gift_tiktok:
        points = gift_tiktok[gift_name] * repeat_count
        console.print(
            f"[bold yellow]{sender}[/bold yellow] sent [bold cyan]{repeat_count}x {gift_name}[/bold cyan] worth [bold magenta]{points} points[/bold magenta]!"
        )

        # Determine relay command and duration based on points
        if points <= 2:
            relay_command, duration = "relay1nyala", 1
        elif 3 <= points <= 19:
            relay_command, duration = "semuarelaynyala", 2
        elif 20 <= points <= 50:
            relay_command, duration = "semuarelaynyala", 3
        elif 51 <= points <= 100:
            relay_command, duration = "relay1nyala", 4
        else:
            relay_command, duration = "relay2nyala", 5

        # Send command to ESP32
        send_relay_command(relay_command, duration, sender)
    else:
        console.print(f"[bold red]Unknown gift received: {gift_name}[/bold red]")

def connect_with_retries(max_retries=5, retry_delay=5):
    retry_count = 0
    while retry_count < max_retries:
        try:
            console.print(f"[bold blue]Connecting to TikTok username:[/bold blue] {tiktok_username}... (Attempt {retry_count + 1})")
            client.run()
        except Exception as e:
            console.print(f"[bold red]Connection error:[/bold red] {e}")
            retry_count += 1
            if retry_count < max_retries:
                console.print(f"[bold yellow]Retrying in {retry_delay} seconds...[/bold yellow]")
                time.sleep(retry_delay)
            else:
                console.print("[bold red]Failed to connect after maximum retries. Exiting.[/bold red]")
                sys.exit(1)

if __name__ == '__main__':
    # Connect to TikTok Live
    connect_with_retries()
