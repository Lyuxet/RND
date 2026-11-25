import os

def clear():
    os.system("clear")


import requests

def get_ip_country(ip):
    response = requests.get(f"https://ipwho.is/{ip}", timeout=10)
    data = response.json()

    if not data.get("success"):
        raise ValueError("Не удалось определить страну")

    return data["country"]

import random

def generate_7_digits():
    return random.randint(1000000, 9999999)