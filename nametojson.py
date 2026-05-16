import re
import json

INPUT_FILE = "name.txt"
OUTPUT_FILE = "laptops.json"


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def slugify(text):
    """
    Convert text to a clean ID.
    Example:
    "HP Victus 15" -> "hp_victus_15"
    """
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def extract_price(line):
    """
    Extract price from beginning of line.
    Example:
    "59,990 MSI Thin A15 ..."
    -> 59990
    """
    match = re.match(r"([\d,]+)", line)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def extract_laptop_name(title):
    """
    Extract clean laptop name.

    Examples:
    "Lenovo LOQ 2025 AMD Ryzen 5 Quad Core 7235HS ..."
    -> "Lenovo LOQ 2025"

    "HP Victus Intel Core i5 13th Gen 13420H ..."
    -> "HP Victus"

    "ASUS Vivobook 16 (2026) AI PC AMD Ryzen AI 7 Hexa Core ..."
    -> "ASUS Vivobook 16 (2026)"
    """

    # CPU keywords where laptop name usually ends
    stop_keywords = [
        "AMD Ryzen AI",
        "AMD Ryzen",
        "Intel Core Ultra",
        "Intel Core",
        "Snapdragon X Plus",
        "Snapdragon X",
        "Qualcomm Snapdragon",
    ]

    name = title

    # Cut title before CPU section
    for keyword in stop_keywords:
        pos = title.lower().find(keyword.lower())
        if pos != -1:
            name = title[:pos]
            break

    # Remove common marketing words
    remove_patterns = [
        r"\bLaptop\b",
        r"\bNotebook\b",
        r"\bThin and Light\b",
        r"\bGaming\b",
        r"\bBusiness\b",
        r"\bAI PC\b",
        r"\bCopilot\+?\s*PC\b",
        r"\bFull Metal\b",
        r"\bMetal Body\b",
        r"\bBacklit Keyboard\b",
        r"\bWith Office\b",
        r"\bOffice 2024\b",
        r"\bM365 Basic\b",
        r"\bTouch Screen\b",
        r"\bOLED\b",
        r"\bWUXGA\b",
        r"\bFHD\b",
        r"\bQuad Core\b",
        r"\bHexa Core\b",
        r"\bOcta Core\b",
        r"\bDeca Core\b",
        r"\bSeries 2\b",
        r"\bProcessor\b",
    ]

    for pattern in remove_patterns:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)

    # Remove empty parentheses like "()"
    name = re.sub(r"\(\s*\)", "", name)

    # Normalize spaces
    name = re.sub(r"\s+", " ", name)

    # Strip punctuation
    name = name.strip(" ,-/")

    return name


def extract_ram(title):
    """
    Extract RAM in GB.
    Handles:
    - 16 GB RAM
    - (16 GB/512 GB SSD)
    """
    match = re.search(r"\(\s*(\d+)\s*GB", title, re.IGNORECASE)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*GB\s*RAM", title, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return None


def extract_storage(title):
    """
    Extract SSD size in GB.
    Converts TB to GB.
    """
    match = re.search(r"(\d+)\s*(GB|TB)\s*SSD", title, re.IGNORECASE)

    if not match:
        return None

    size = int(match.group(1))
    unit = match.group(2).upper()

    if unit == "TB":
        size *= 1024

    return size


def extract_battery(title):
    """
    Extract battery capacity in Wh.
    """
    match = re.search(
        r"([\d.]+)\s*(?:WHrs|Watt Hours|Wh)",
        title,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def extract_weight(title):
    """
    Extract weight in kg.
    """
    match = re.search(r"([\d.]+)\s*Kg", title, re.IGNORECASE)

    if match:
        return float(match.group(1))

    return None


def extract_display_size(title):
    """
    Extract display size in inches.
    Handles:
    - 15.6 inch
    - 14 Inch
    - 14"
    """
    match = re.search(
        r'(\d{1,2}(?:\.\d+)?)\s*(?:inch|")',
        title,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def extract_refresh_rate(title):
    """
    Extract refresh rate.
    Default = 60 Hz.
    """
    match = re.search(r"(\d+)\s*Hz", title, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return 60


def extract_cpu(title):
    """
    Universal CPU extractor.

    Handles:
    - AMD Ryzen 7 7730U
    - AMD Ryzen 7-7745HS
    - AMD Ryzen 7 Octa Core 7730U
    - AMD Ryzen 7 Octa Core
    - AMD Ryzen AI 7 350
    - AMD Ryzen AI 7
    - Intel Core i7-13620H
    - Intel Core i7 13th Gen 13620H
    - Intel Core i7 13th Gen
    - Intel Core Ultra 7 255H
    - Intel Core Ultra 7
    - Intel Core 5 210H
    - Snapdragon X
    - Snapdragon X Plus

    Prevents invalid outputs such as:
    - Intel Core Ultra 7 -
    - Intel Core Ultra 7 Gaming
    - Intel Core i7 13th
    - AMD Ryzen 7 Octa
    """

    # ======================================================
    # 1. Exact model patterns (best case)
    # ======================================================
    patterns = [
        # AMD Ryzen AI 7 350 / 9 365
        r"AMD Ryzen AI\s+\d+\s+\d+[A-Za-z]*",

        # AMD Ryzen AI 7
        r"AMD Ryzen AI\s+\d+",

        # AMD Ryzen 7-7745HS
        r"AMD Ryzen\s+\d+\s*-\s*[0-9]{4,5}[A-Za-z]{1,3}",

        # AMD Ryzen 7 7730U
        r"AMD Ryzen\s+\d+\s+[0-9]{4,5}[A-Za-z]{1,3}",

        # AMD Ryzen 7 Octa Core 7730U
        r"AMD Ryzen\s+\d+.*?([0-9]{4,5}[A-Za-z]{1,3})",

        # Intel Core Ultra 7 255H / 256V
        r"Intel Core Ultra\s+\d+\s+[0-9]{3}[A-Za-z]",

        # Intel Core i7-13620H
        r"Intel Core i[3579]-[0-9]{4,5}[A-Za-z]{1,3}",

        # Intel Core i7 13620H
        r"Intel Core i[3579]\s+[0-9]{4,5}[A-Za-z]{1,3}",

        # Intel Core i7 13th Gen 13620H
        r"Intel Core i[3579]\s+\d+(?:st|nd|rd|th)\s+Gen\s+[0-9]{4,5}[A-Za-z]{1,3}",

        # Intel Core 3 100U / Core 5 210H / Core 7 240H
        r"Intel Core\s+\d+\s+[0-9]{3}[A-Za-z]",

        # Qualcomm
        r"Snapdragon X Plus",
        r"Snapdragon X",
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if not match:
            continue

        cpu = match.group(0).strip()
        cpu = re.sub(r"\s+", " ", cpu)

        # Normalize AMD hyphen:
        # AMD Ryzen 7-7745HS -> AMD Ryzen 7 7745HS
        cpu = re.sub(
            r"(\d+)\s*-\s*([0-9]{4,5}[A-Za-z]{1,3})",
            r"\1 \2",
            cpu
        )

        # Normalize Intel "13th Gen"
        gen_match = re.search(
            r"Intel Core (i[3579])\s+\d+(?:st|nd|rd|th)\s+Gen\s+([0-9]{4,5}[A-Za-z]{1,3})",
            cpu,
            re.IGNORECASE
        )
        if gen_match:
            return f"Intel Core {gen_match.group(1)}-{gen_match.group(2)}"

        # Normalize AMD noisy strings
        amd_match = re.search(
            r"AMD Ryzen\s+(\d+).*?([0-9]{4,5}[A-Za-z]{1,3})",
            cpu,
            re.IGNORECASE
        )
        if amd_match:
            return f"AMD Ryzen {amd_match.group(1)} {amd_match.group(2)}"

        # Reject obvious bad endings
        if cpu.endswith("-"):
            continue

        if re.search(
            r"\b(gaming|quad|hexa|octa|deca|13th|14th|15th)\b$",
            cpu,
            re.IGNORECASE
        ):
            continue

        return cpu

    # ======================================================
    # 2. Generic fallback when NO model number exists
    # ======================================================

    # AMD Ryzen AI 7
    match = re.search(r"AMD Ryzen AI\s+\d+", title, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # AMD Ryzen 7 Octa Core / AMD Ryzen 5 Hexa Core
    match = re.search(r"AMD Ryzen\s+\d+", title, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # Intel Core Ultra 7
    match = re.search(r"Intel Core Ultra\s+\d+", title, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # Intel Core i7 / i5 / i3 / i9
    match = re.search(r"Intel Core i[3579]", title, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # Intel Core 5 / Core 7 / Core 3
    match = re.search(r"Intel Core\s+\d+", title, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    # Qualcomm
    match = re.search(r"Snapdragon X Plus|Snapdragon X", title, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    return None


def extract_gpu(title):
    """
    Extract GPU name.
    """
    patterns = [
        r"NVIDIA GeForce RTX \d+",
        r"NVIDIA GeForce GTX \d+",
        r"AMD Radeon RX\d+[A-Za-z]*",
        r"Intel Arc Graphics",
        r"Intel Iris Xe Graphics",
        r"Intel UHD Graphics",
        r"Qualcomm Adreno Graphics",
        r"AMD Radeon Graphics",
        r"AMD Radeon Integrated Graphics",
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return "Integrated Graphics"


def detect_has_dgpu(gpu):
    """
    Determine if GPU is dedicated.
    """
    if not gpu:
        return False

    return bool(
        re.search(
            r"NVIDIA GeForce RTX|NVIDIA GeForce GTX|AMD Radeon RX",
            gpu,
            re.IGNORECASE
        )
    )


def detect_resolution(title):
    """
    Detect display resolution.
    """
    if re.search(r"\bWUXGA\b", title, re.IGNORECASE):
        return "WUXGA"

    if re.search(r"\bQHD\b", title, re.IGNORECASE):
        return "QHD"

    if re.search(r"\bOLED\b", title, re.IGNORECASE):
        return "OLED"

    if re.search(r"\bFHD\b|Full HD", title, re.IGNORECASE):
        return "FHD"

    return None


def detect_display_type(title):
    """
    Detect panel type.
    """
    if re.search(r"\bOLED\b", title, re.IGNORECASE):
        return "OLED"

    if re.search(r"\bIPS\b", title, re.IGNORECASE):
        return "IPS"

    if re.search(r"Touch|2 in 1|Flip", title, re.IGNORECASE):
        return "Touch"

    return None


def detect_os(title):
    """
    Detect operating system.
    """
    if re.search(r"Windows 11 Pro", title, re.IGNORECASE):
        return "Windows 11 Pro"

    if re.search(r"Windows 11 Home", title, re.IGNORECASE):
        return "Windows 11 Home"

    if re.search(r"Windows 11", title, re.IGNORECASE):
        return "Windows 11"

    return None


def detect_category(has_dgpu, title):
    """
    Detect category.
    """
    title_lower = title.lower()

    if has_dgpu:
        return "gaming"

    if "copilot" in title_lower or "snapdragon x" in title_lower:
        return "copilot_plus"

    if "2 in 1" in title_lower or "flip" in title_lower:
        return "convertible"

    if (
        "zenbook" in title_lower
        or "swift" in title_lower
        or "galaxy book" in title_lower
        or "motobook" in title_lower
    ):
        return "premium"

    if "professional" in title_lower or "business" in title_lower:
        return "budget"

    return "thin_and_light"


def detect_office(title):
    """
    Detect whether Office is included.
    """
    return bool(
        re.search(
            r"Office|MS Office|MSO",
            title,
            re.IGNORECASE
        )
    )


# ==========================================================
# MAIN CONVERTER
# ==========================================================

def convert():
    laptops = []
    existing_ids = set()

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        # Skip empty lines and headings
        if not line or line.startswith("#"):
            continue

        # Extract price
        price = extract_price(line)
        if price is None:
            continue

        # Remove price from title
        title = re.sub(
            r"^[\d,]+\s*[-–]?\s*",
            "",
            line
        ).strip()

        # Extract laptop name
        laptop_name = extract_laptop_name(title)
        if not laptop_name:
            continue

        # Generate unique ID based on laptop name
        base_id = slugify(laptop_name)
        laptop_id = base_id

        counter = 2
        while laptop_id in existing_ids:
            laptop_id = f"{base_id}_{counter}"
            counter += 1

        existing_ids.add(laptop_id)

        # Extract specifications
        cpu = extract_cpu(title)
        gpu = extract_gpu(title)
        has_dgpu = detect_has_dgpu(gpu)

        ram_gb = extract_ram(title)
        storage_gb = extract_storage(title)
        battery_wh = extract_battery(title)
        weight_kg = extract_weight(title)
        display_size_inch = extract_display_size(title)
        refresh_rate_hz = extract_refresh_rate(title)

        display_resolution = detect_resolution(title)
        display_type = detect_display_type(title)
        os_name = detect_os(title)
        office_included = detect_office(title)
        category = detect_category(has_dgpu, title)

        # Brand = first word of laptop name
        brand = laptop_name.split()[0]

        # Model = laptop name without brand
        model = laptop_name[len(brand):].strip()

        laptop = {
            "id": laptop_id,
            "brand": brand,
            "model": model,
            "price_inr": price,
            "cpu": cpu,
            "gpu": gpu,
            "has_dgpu": has_dgpu,
            "ram_gb": ram_gb,
            "storage_gb": storage_gb,
            "battery_wh": battery_wh,
            "weight_kg": weight_kg,
            "display_size_inch": display_size_inch,
            "display_resolution": display_resolution,
            "display_type": display_type,
            "refresh_rate_hz": refresh_rate_hz,
            "os": os_name,
            "office_included": office_included,
            "category": category,
            "raw_title": title
        }

        laptops.append(laptop)

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(laptops, file, indent=2, ensure_ascii=False)

    print(f"Saved {len(laptops)} laptops to {OUTPUT_FILE}")


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    convert()