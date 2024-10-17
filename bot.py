import requests
import json
import time
import random
from setproctitle import setproctitle
from colorama import Fore, Style, init
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse  # For decoding the URL-encoded initData
from fake_useragent import UserAgent  # For fake user-agent
from faker import Faker  # For generating random user data

# Initialize Faker
fake = Faker()

# Load proxies from proxies.txt
def load_proxies_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Load proxy countries from proxy_countries.txt
def load_proxy_countries(filename):
    proxy_country_map = {}
    with open(filename, 'r') as file:
        for line in file:
            if line.strip():
                proxy, country = line.strip().split()
                proxy_country_map[proxy] = country
    return proxy_country_map

def welcome_message_ascii():
    message = """
█▀▄▀█ █▀▀ █▀▀ ▄▀█ █▀▄ █▀█ █▀█ █▀█
█░▀░█ ██▄ █▄█ █▀█ █▄▀ █▀▄ █▄█ █▀▀
Ingat kita miskin, semoga JP bareng
    """
    return message

# Example usage
print(welcome_message_ascii())

init(autoreset=True)
red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
green = Fore.LIGHTGREEN_EX
yellow = Fore.LIGHTYELLOW_EX
black = Fore.LIGHTBLACK_EX
white = Fore.LIGHTWHITE_EX
reset = Style.RESET_ALL

url = "https://notpx.app/api/v1"

# ACTIVITY
WAIT = 180 * 3
DELAY = 1

# Initialize colorama for colored output
init(autoreset=True)

setproctitle("notpixel")

# Initialize Fake UserAgent
ua = UserAgent()

class NotPixTod:
    def __init__(self, no, proxies, proxy_country_map):
        ci = lambda a, b: (b * 1000) + (a + 1)
        self.p = no
        self.proxies = proxies
        self.proxy_country_map = proxy_country_map
        self.colors = [
            "#3690ea",
            "#e46e6e",
            "#ffffff",
            "#be0039",
            "#6d001a",
            "#ffd635",
            "#ff9600",
            "#bf4300",
            "#7eed56",
            "#00cc78",
            "#00a368",
            "#000000",
        ]
        self.block = {
            "#000000": [
                [ci(650, 934), ci(651, 934)],
            ]
        }

    def log(self, msg):
        now = datetime.now().isoformat().split("T")[1].split(".")[0]
        print(
            f"{black}[{now}]{white}-{blue}[{white}acc {self.p + 1}{blue}]{white} {msg}{reset}"
        )

# Function to log messages with timestamp in light grey color
def log_message(message, color=Style.RESET_ALL):
    current_time = datetime.now().strftime("[%H:%M:%S]")
    print(f"{Fore.LIGHTBLACK_EX}{current_time}{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")

# Function to initialize a requests session with retry logic
def get_session_with_retries(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), proxy=None):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set the fake user agent
    session.headers.update({'User-Agent': ua.random})
    
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    
    return session

# Function to claim resources from the server
def claim(header, session):
    log_message("BISMILLAH JP", Fore.LIGHTYELLOW_EX)
    try:
        session.get(f"{url}/mining/claim", headers=header, timeout=10)
    except requests.exceptions.RequestException as e:
        log_message("Gagal Gus, Pokoke Sing Sabar", Fore.RED)  # Change the error message here

# Function to calculate pixel index based on x, y position
def get_pixel(x, y):
    return y * 1000 + x + 1

# Function to get x, y position from pixel index
def get_pos(pixel, size_x):
    return pixel % size_x, pixel // size_x

# Function to get pixel index based on canvas position
def get_canvas_pos(x, y):
    return get_pixel(start_x + x - 1, start_y + y - 1)

# Starting coordinates
start_x = 920
start_y = 386

# Main function to perform the painting process
def main(auth, account, notpixtod):
    headers = {'authorization': auth}
    try:
        # Create a new session with a random proxy and a fake user-agent
        proxy = random.choice(notpixtod.proxies)
        session = get_session_with_retries(proxy=proxy)
        
        # Extract username from initData (or generate fake data with Faker)
        username = extract_username_from_initdata(account)
        if username == "Unknown":
            username = fake.user_name()  # Generate a random username if not found
        
        # Get country for the proxy
        proxy_parts = proxy.split('@')[-1]  # Extract proxy address with port
        proxy_address = proxy_parts.split(':')[0]  # Remove port from the address
        country = notpixtod.proxy_country_map.get(proxy_address, "Unknown")  # Get country from the map
        
        # Log the connected account in blue
        log_message(f"Account: {username}", Fore.LIGHTBLUE_EX)
        
        # Log the proxy and country information below the account
        log_message(f"Proxy: {proxy_address}, Country: {country}", Fore.GREEN)

        # Claim resources and get initial balance
        claim(headers, session)
        response = session.get(f"{url}/mining/status", headers=headers, timeout=10)
        balance = response.json().get("userBalance", 0)  # Initial balance
        log_message(f"Balance: {balance:.2f}", Fore.CYAN)

        # Initialize total points
        total_points = 0

        # Paint each pixel in the defined block
        charges = response.json().get("boosts", {}).get("energyLimit", 0)
        for i in range(charges):
            try:
                pixel_id = random.randint(1, 1000000)
                new_color = random.choice(list(notpixtod.block.keys())).upper()
                temp_color = [color.upper() for color in notpixtod.colors]
                temp_color.remove(new_color)
                first_color = random.choice(temp_color).upper()
                pixel_id = random.choice(random.choice(notpixtod.block[new_color]))

                for i in range(2):
                    if i == 0:
                        data_post = {"pixelId": pixel_id, "newColor": first_color}
                        response = session.post(f"{url}/repaint/start", json=data_post, headers=headers, timeout=10)
                    else:
                        data_post = {"pixelId": pixel_id, "newColor": new_color}
                        response = session.post(f"{url}/repaint/start", json=data_post, headers=headers, timeout=10)

                    new_balance = response.json().get("balance", 0)
                    inc = new_balance - balance  # Points earned from painting
                    balance = new_balance  # Update balance
                    log_message(f"Paint: {pixel_id}, color: {new_color}, reward: +{inc:.2f} points", Fore.GREEN)

                    # Check response status
                    if response.status_code == 400:
                        log_message("Wayahe Leren Mas", Fore.RED)
                        break
                    if response.status_code == 401:
                        log_message("Turu Sik", Fore.RED)
                        break

                total_points += inc

            except requests.exceptions.RequestException as e:
                log_message(f"Failed to paint: {e}", Fore.RED)
                break

    except requests.exceptions.RequestException as e:
        log_message(f"Network error in account {account}: {e}", Fore.RED)

    # Add an extra line for spacing between accounts
    print()

# Process accounts and manage sleep logic
def process_accounts(accounts, proxies, proxy_country_map):
    for account in accounts:
        notpixtod = NotPixTod(0, proxies, proxy_country_map)  # Create an instance of NotPixTod with proxies and country map
        main(account, account, notpixtod)  # Pass notpixtod to the main function

# Function to extract the username from the URL-encoded init data
def extract_username_from_initdata(init_data):
    decoded_data = urllib.parse.unquote(init_data)
    
    username_start = decoded_data.find('"username":"') + len('"username":"')
    username_end = decoded_data.find('"', username_start)
    
    if username_start != -1 and username_end != -1:
        return decoded_data[username_start:username_end]
    
    return "Unknown"

# Function to load accounts from data.txt
def load_accounts_from_file(filename):
    with open(filename, 'r') as file:
        accounts = [f"initData {line.strip()}" for line in file if line.strip()]
    return accounts

if __name__ == "__main__":
    accounts = load_accounts_from_file('data.txt')
    proxies = load_proxies_from_file('proxies.txt')  # Load proxies from the file
    proxy_country_map = load_proxy_countries('proxy_countries.txt')  # Load proxy-country mapping
    process_accounts(accounts, proxies, proxy_country_map)
