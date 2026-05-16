# gpu_scraper.py
# Scrapes dedicated GPU benchmark data from Nanoreview
# Input:  laptops.json
# Output: GPU_out.json

import requests
from bs4 import BeautifulSoup
import json
import time
import re


# ==========================================================
# HTTP HEADERS
# ==========================================================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://google.com"
}


# ==========================================================
# NORMALIZE GPU NAME TO BASE SLUG
# ==========================================================
def normalize_gpu_slug(gpu_name):
    """
    Converts:
    NVIDIA GeForce RTX 4050 Laptop GPU
    ->
    nvidia-geforce-rtx-4050
    """

    if not gpu_name:
        return ""

    gpu_name = gpu_name.lower()

    # Remove common noise words
    remove_words = [
        "laptop gpu",
        "graphics",
        "gpu",
        "mobile graphics"
    ]

    for word in remove_words:
        gpu_name = gpu_name.replace(word, " ")

    # Remove brackets and commas
    gpu_name = gpu_name.replace("(", " ")
    gpu_name = gpu_name.replace(")", " ")
    gpu_name = gpu_name.replace(",", " ")

    # Normalize vendor names
    gpu_name = gpu_name.replace("nvidia geforce", "nvidia-geforce")
    gpu_name = gpu_name.replace("amd radeon", "amd-radeon")
    gpu_name = gpu_name.replace("intel iris xe", "intel-iris-xe")
    gpu_name = gpu_name.replace("intel uhd", "intel-uhd")

    # Collapse spaces
    gpu_name = re.sub(r"\s+", " ", gpu_name).strip()

    # Convert spaces to hyphens
    return gpu_name.replace(" ", "-")


# ==========================================================
# GENERATE POSSIBLE NANOREVIEW SLUGS
# ==========================================================
def get_possible_gpu_slugs(gpu_name):
    """
    Generate possible Nanoreview slugs for GPU names.

    Examples:
    NVIDIA GeForce RTX 4050
        -> ["geforce-rtx-4050-mobile", "geforce-rtx-4050"]

    NVIDIA GeForce GTX 1650
        -> ["geforce-gtx-1650-mobile", "geforce-gtx-1650"]

    AMD Radeon RX 7700S
        -> ["radeon-rx-7700s"]

    AMD Radeon RX 7600M XT
        -> ["radeon-rx-7600m-xt"]

    Intel Arc Graphics
        -> ["intel-arc-graphics"]

    Qualcomm Adreno Graphics
        -> ["qualcomm-adreno-gpu"]
    """

    base_slug = normalize_gpu_slug(gpu_name)

    if not base_slug:
        return []

    possible_slugs = []

    # ======================================================
    # NVIDIA GeForce RTX / GTX
    # ======================================================
    if "rtx" in base_slug or "gtx" in base_slug:
        # nvidia-geforce-rtx-4050 -> geforce-rtx-4050
        if base_slug.startswith("nvidia-geforce-"):
            base_slug = base_slug.replace("nvidia-", "", 1)

        possible_slugs.append(base_slug + "-mobile")
        possible_slugs.append(base_slug)

    # ======================================================
    # AMD Radeon RX dedicated GPUs
    # ======================================================
    elif "amd-radeon-rx-" in base_slug:
        # amd-radeon-rx-7700s -> radeon-rx-7700s
        slug = base_slug.replace("amd-", "", 1)
        possible_slugs.append(slug)

    # ======================================================
    # AMD Radeon integrated GPUs
    # ======================================================
    elif "amd-radeon-" in base_slug:
        possible_slugs.append(base_slug)

    # ======================================================
    # Intel Arc
    # ======================================================
    elif "intel-arc" in base_slug:
        possible_slugs.append("intel-arc-graphics")

    # ======================================================
    # Intel Iris Xe
    # ======================================================
    elif "intel-iris-xe" in base_slug:
        possible_slugs.append("intel-iris-xe-graphics")

    # ======================================================
    # Intel UHD
    # ======================================================
    elif "intel-uhd" in base_slug:
        possible_slugs.append("intel-uhd-graphics")

    # ======================================================
    # Qualcomm Adreno
    # ======================================================
    elif "adreno" in base_slug:
        possible_slugs.append("qualcomm-adreno-gpu")

    # ======================================================
    # Fallback
    # ======================================================
    else:
        possible_slugs.append(base_slug)

    # Remove duplicates while preserving order
    unique_slugs = []
    seen = set()

    for slug in possible_slugs:
        if slug not in seen:
            unique_slugs.append(slug)
            seen.add(slug)

    return unique_slugs

# ==========================================================
# TRY POSSIBLE URLS UNTIL ONE WORKS
# ==========================================================
def get_working_gpu_url(gpu_name):
    possible_slugs = get_possible_gpu_slugs(gpu_name)

    for slug in possible_slugs:
        url = f"https://nanoreview.net/en/gpu/{slug}"

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=20
            )

            if response.status_code == 200:
                print(f"Success: {gpu_name} -> {slug}")
                return url, response.text

            print(f"Failed: {slug} ({response.status_code})")

        except Exception as e:
            print(f"Error for {slug}: {e}")

    print(f"No working URL found for {gpu_name}")
    return None, None


# ==========================================================
# SCRAPE SCORES FROM PAGE
# ==========================================================
def scrape_gpu_scores(gpu_name):
    url, html = get_working_gpu_url(gpu_name)

    if not url:
        return None

    soup = BeautifulSoup(html, "html.parser")

    score_blocks = soup.find_all("div", class_="score-bar")

    gpu_info = {
        "gpu_name": gpu_name,
        "url": url,
        "gaming_score": None,
        "power_efficiency_score": None,
        "scores": {}
    }

    for block in score_blocks:
        name_elem = block.find("div", class_="score-bar-name")
        value_elem = block.find("span", class_="score-bar-result-square")

        if not name_elem or not value_elem:
            continue

        score_name = name_elem.get_text(" ", strip=True)
        score_value_text = value_elem.get_text(strip=True)

        # Convert score to integer if possible
        try:
            score_value = int(score_value_text)
        except ValueError:
            score_value = score_value_text

        # Save all scores in a generic dictionary
        gpu_info["scores"][score_name] = score_value

        score_name_lower = score_name.lower()

        # Extract specific important scores
        if "gaming performance" in score_name_lower:
            gpu_info["gaming_score"] = score_value

        elif "power efficiency" in score_name_lower:
            gpu_info["power_efficiency_score"] = score_value

        print(f"{score_name}: {score_value}")

    return gpu_info


# ==========================================================
# LOAD UNIQUE DEDICATED GPUS FROM laptops.json
# ==========================================================
def load_unique_dedicated_gpus():
    with open("laptops.json", "r", encoding="utf-8") as file:
        laptops = json.load(file)

    gpu_set = set()

    for laptop in laptops:
        gpu = laptop.get("gpu")
        has_dgpu = laptop.get("has_dgpu", False)

        if gpu and has_dgpu:
            gpu_set.add(gpu)

    return sorted(gpu_set)


# ==========================================================
# MAIN
# ==========================================================
def main():
    gpu_list = load_unique_dedicated_gpus()

    print(f"Found {len(gpu_list)} unique dedicated GPUs.\n")

    all_gpu_data = []

    for gpu_name in gpu_list:
        print("=" * 60)
        print(f"Scraping: {gpu_name}")
        print("=" * 60)

        gpu_data = scrape_gpu_scores(gpu_name)

        if gpu_data:
            all_gpu_data.append(gpu_data)

        # Delay to avoid rate limiting
        time.sleep(2)

    # Save output
    with open("GPU_out.json", "w", encoding="utf-8") as file:
        json.dump(all_gpu_data, file, indent=4)

    print("\nSaved GPU_out.json")


# ==========================================================
# ENTRY POINT
# ==========================================================
if __name__ == "__main__":
    main()