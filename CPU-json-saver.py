import requests
from bs4 import BeautifulSoup
import json
import time
import re

def normalize_cpu_slug(cpu_name):


    if not cpu_name:
        return ""

    # Convert to lowercase
    cpu_name = cpu_name.lower()

    # Remove common noise words
    remove_words = [
        "processor",
        "cpu",
        "12th gen",
        "13th gen",
        "14th gen",
        "15th gen",
        "16th gen",
        "octa core",
        "hexa core",
        "quad core",
        "dual core"
    ]

    for word in remove_words:
        cpu_name = cpu_name.replace(word, " ")

    # Normalize separators
    cpu_name = cpu_name.replace("/", " ")
    cpu_name = cpu_name.replace("(", " ")
    cpu_name = cpu_name.replace(")", " ")
    cpu_name = cpu_name.replace(",", " ")

    # Collapse multiple spaces
    cpu_name = re.sub(r"\s+", " ", cpu_name).strip()

    # Handle Qualcomm Snapdragon X series
    # Examples:
    # Snapdragon X
    # Snapdragon X Plus
    # Snapdragon X Elite
    if cpu_name.startswith("snapdragon x"):
        # Remove existing "qualcomm" if present
        cpu_name = cpu_name.replace("qualcomm ", "")
        return "qualcomm-" + cpu_name.replace(" ", "-")

    # Handle AMD Ryzen AI series
    # Examples:
    # AMD Ryzen AI 7 350
    # AMD Ryzen AI 9 HX 370
    if cpu_name.startswith("amd ryzen ai"):
        return cpu_name.replace(" ", "-")

    # Handle standard AMD Ryzen series
    # Examples:
    # AMD Ryzen 5 5625U
    if cpu_name.startswith("amd ryzen"):
        return cpu_name.replace(" ", "-")

    # Handle Intel Core Ultra
    # Examples:
    # Intel Core Ultra 5 125H
    if cpu_name.startswith("intel core ultra"):
        return cpu_name.replace(" ", "-")

    # Handle Intel Core processors
    # Examples:
    # Intel Core i5-13450HX
    # Intel Core 3 100U
    # Intel Core 5 120U
    # Intel Core 7 240H
    if cpu_name.startswith("intel core"):
        return cpu_name.replace(" ", "-")

    # Fallback for any other processor
    return cpu_name.replace(" ", "-")


def scrape_cpu_scores(cpu_name):

    slug = normalize_cpu_slug(cpu_name)

    url = f"https://nanoreview.net/en/cpu/{slug}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
        "Referer": "https://google.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed: {cpu_name}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    score_blocks = soup.find_all("div", class_="score-bar")

    cpu_info = {
        "cpu_name": cpu_name,
        "single_core_score": None,
        "multi_core_score": None,
        "power_score": None,
        "integrated_gpu_score": None
    }

    for block in score_blocks:

        name = block.find("div", class_="score-bar-name")
        value = block.find("span", class_="score-bar-result-square")

        if name and value:

            score_name = name.text.strip().lower()
            score_value = value.text.strip()

            print(score_name, ":", score_value)

            if "single-core" in score_name:
                cpu_info["single_core_score"] = score_value

            elif "multi-core" in score_name:
                cpu_info["multi_core_score"] = score_value

            elif "power efficiency" in score_name:
                cpu_info["power_score"] = score_value

            elif "integrated graphics" in score_name:
                cpu_info["integrated_gpu_score"] = score_value

    return cpu_info


# LOAD LAPTOPS
with open("laptops.json", "r", encoding="utf-8") as file:
    laptops = json.load(file)


# EXTRACT UNIQUE CPUS
cpu_set = set()

for laptop in laptops:
    cpu_set.add(laptop["cpu"])


all_cpu_data = []


# SCRAPE ALL CPUS
for cpu in cpu_set:

    print(f"\nScraping: {cpu}")

    data = scrape_cpu_scores(cpu)

    if data:
        all_cpu_data.append(data)

    time.sleep(2)


# SAVE JSON FILE
with open("CPU_info.json", "w", encoding="utf-8") as file:
    json.dump(all_cpu_data, file, indent=4)


