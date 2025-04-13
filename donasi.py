from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, GiftEvent
import requests
import sys
from rich.console import Console

# Initialize rich console for better output
console = Console()

# Read TikTok username from command-line arguments
if len(sys.argv) < 2:
    console.print("[bold red]Error:[/bold red] TikTok username is required!")
    sys.exit(1)

tiktok_username = sys.argv[1]

# Define static ESP32 IP address (match with ESP32 code)
ESP32_IP = "192.168.10.116"  # Static IP configured in ESP32
ESP32_PORT = 80

# Gift values (in points)
gift_values = {
    "Brat": 1,
    "Heart Me": 1,
    "Finger Heart": 5,
    "Red Packet": 5,  
    "Bouquet Flower": 5,
    "Cow": 10,
    "Paper Crane": 10,
    "Fest burst": 1,
    "Candy Cane": 1,
    "Flame Heart": 1,
    "Music play": 1,
    "GG": 1,
    "Lightning bolt": 1,
    "Ice cream cone": 1,
    "Rose": 1,
    "TikTok": 1,
    "Fluffy penguin": 5,
    "Tofu the cat": 5,
    "Ladybug": 5,
    "Espresso": 5,
    "Finger heart": 5,
    "Gold boxing glove": 10,
    "Festive potato": 10,
    "Hi bear": 5,
    "Sweet Sheep": 5,
    "Little ghost": 10,
    "Christmas wreath": 10,
    "Friendship necklace": 10,
    "Rosa": 10,
    "Perfume": 20,
    "Scented candle": 20,
    "Doughnut": 30,
    "Sign language love": 49,
    "Butterfly": 88,
    "Fist bump": 90,
    "Sending strength": 90,
    "Family": 90,
    "Hat and mustache": 99,
    "Cap": 99,
    "Paper crane": 99,
    "Fest crown": 99,
    "Love painting": 99,
    "Little crown": 99,
    "Hand heart": 100,
    "Hand hearts": 100,
    "Super GG": 100,
    "Confetti": 100,
    "Headphones": 199,
    "Reindeer": 199,
    "Festive bear": 199,
    "Hearts": 199,
    "Sunglasses": 199,
    "Night star": 199,
    "Eye see you": 199,
    "Santa’s mailbox": 199,
    "Dancing hands": 199,
    "Mistletoe": 199,
    "Message for you": 199,
    "Stinging bee": 199,
    "Coffee magic": 199,
    "Sending positivity": 199,
    "Love you": 199,
    "Garland headpiece": 199,
    "Elephant trunk": 299,
    "TikTok crown": 299,
    "Elf’s hat": 299,
    "Fruit friends": 299,
    "Play for you": 299,
    "Rock star": 299,
    "Superpower": 299,
    "Boxing Gloves": 299,
    "Corgi": 299,
    "Dancing flower": 299,
    "Rosie the Rose Bean": 399,
    "Jolly the Joy Bean": 399,
    "Good Afternoon": 399,
    "Tom’s hug": 399,
    "Relaxed goose": 399,
    "Rocky the Rock Bean": 399,
    "Sage the Smart Bean": 399,
    "Pumpkin head": 399,
    "Forever Rosa": 399,
    "Gaming headset": 399,
    "Beating heart": 449,
    "Coral": 499,
    "You’re amazing": 500,
    "Money gun": 500,
    "Manifesting": 500,
    "Lion’s mane": 500,
    "DJ glasses": 500,
    "Star map polaris": 500,
    "VR Goggles": 500,
    "Swan": 699,
    "Train": 899,
    "Travel with you": 999,
    "Lucky the Airdrop Box": 999,
    "Drums": 1000,
    "Galaxy": 1000,
    "Blooming ribbons": 1000,
    "Glowing jellyfish": 1000,
    "Watermelon love": 1000,
    "Dinosaur": 1000,
    "Gerry the giraffe": 1000,
    "Fireworks": 1088,
    "Diamond tree": 1088,
    "Fountain": 1200,
    "Spooky cat": 1200,
    "Moonlight flower": 1400,
    "Future encounter": 1500,
    "Love explosion": 1500,
    "Under control": 1500,
    "Greeting card": 1500,
    "Chasing the dream": 1500
}

# Create TikTokLive client
client: TikTokLiveClient = TikTokLiveClient(unique_id=tiktok_username)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    console.print(f"[bold green]Connected to TikTok user:[/bold green] {event.unique_id}!")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift_name = event.gift.name
    repeat_count = event.repeat_count
    sender = event.user.unique_id

    if gift_name in gift_values:
        points = gift_values[gift_name] * repeat_count
        console.print(
            f"[bold yellow]{sender}[/bold yellow] sent [bold cyan]{repeat_count}x {gift_name}[/bold cyan] worth [bold magenta]{points} points[/bold magenta]!"
        )

        # Send data to ESP32
        try:
            url = f"http://{ESP32_IP}:{ESP32_PORT}/gift"
            payload = {"gift": gift_name, "points": points, "user": sender}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                console.print("[bold green]Data sent to ESP32![/bold green]")
            else:
                console.print(f"[bold red]Failed to send data to ESP32: {response.status_code}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error sending data to ESP32:[/bold red] {e}")
    else:
        console.print(f"[bold red]Unknown gift received: {gift_name}[/bold red]")

if __name__ == '__main__':
    console.print(f"[bold blue]Connecting to TikTok username:[/bold blue] {tiktok_username}...")
    client.logger.setLevel(LogLevel.INFO.value)
    client.run()