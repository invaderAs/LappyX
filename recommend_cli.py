
import json


# ==========================================================
# MENU HELPERS
# ==========================================================

def ask_menu(question, options):
    print(f"\n{question}")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:
        choice = input("Enter your choice number: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        print("Invalid choice. Please try again.")


# ==========================================================
# LOAD DATA
# ==========================================================

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []


# ==========================================================
# BUILD LOOKUP TABLES
# ==========================================================

def build_cpu_lookup(cpu_data):
    lookup = {}
    for item in cpu_data:
        lookup[item["cpu_name"]] = item
    return lookup



def build_gpu_lookup(gpu_data):
    lookup = {}
    for item in gpu_data:
        lookup[item["gpu_name"]] = item
    return lookup


# ==========================================================
# QUESTIONNAIRE
# ==========================================================

def collect_user_preferences():
    budget_options = [
        40000,
        50000,
        60000,
        70000,
        80000,
        90000,
        100000,
        125000,
        150000,
        175000,
        200000,
    ]

    budget_labels = [f"₹{b:,}" for b in budget_options]

    budget_label = ask_menu("1. What is your maximum budget?", budget_labels)
    budget = budget_options[budget_labels.index(budget_label)]

    primary_use = ask_menu(
        "2. What will you primarily use the laptop for?",
        [
            "General Use",
            "Programming / Coding",
            "Heavy Multitasking",
            "Gaming",
            "Video Editing / 3D Rendering",
            "AI / Machine Learning",
        ],
    )

    battery_importance = ask_menu(
        "3. How important is battery life?",
        ["Very Important", "Moderately Important", "Not Important"],
    )

    travel_frequency = ask_menu(
        "4. How often do you travel with your laptop?",
        ["Frequently", "Occasionally", "Rarely"],
    )

    min_ram = ask_menu(
        "5. What is the minimum RAM you require?",
        ["8 GB", "16 GB", "32 GB"],
    )
    min_ram_gb = int(min_ram.split()[0])

    gpu_requirement = ask_menu(
        "6. Do you need a dedicated GPU?",
        ["Yes", "No", "Not Sure"],
    )

    longevity = ask_menu(
        "7. How many years do you plan to use this laptop?",
        ["1-2 Years", "3-4 Years", "5+ Years"],
    )

    return {
        "budget": budget,
        "primary_use": primary_use,
        "battery_importance": battery_importance,
        "travel_frequency": travel_frequency,
        "min_ram_gb": min_ram_gb,
        "needs_dgpu": gpu_requirement == "Yes",
        "longevity": longevity,
    }


# ==========================================================
# ENRICH LAPTOP WITH CPU/GPU DATA
# ==========================================================

def enrich_laptop(laptop, cpu_lookup, gpu_lookup):
    laptop = laptop.copy()

    laptop["cpu_info"] = cpu_lookup.get(laptop.get("cpu"))

    if laptop.get("has_dgpu"):
        laptop["gpu_info"] = gpu_lookup.get(laptop.get("gpu"))
    else:
        laptop["gpu_info"] = None

    return laptop


# ==========================================================
# FILTERING
# ==========================================================

def filter_laptops(laptops, prefs):
    filtered = []

    for laptop in laptops:
        if laptop.get("price_inr") is None:
            continue

        if laptop["price_inr"] > prefs["budget"]:
            continue

        if (laptop.get("ram_gb") or 0) < prefs["min_ram_gb"]:
            continue

        if prefs["needs_dgpu"] and not laptop.get("has_dgpu", False):
            continue

        filtered.append(laptop)

    return filtered


# ==========================================================
# VALIDATION
# ==========================================================

def validate_requirements(laptops, prefs):
    """
    Explain why no laptops matched the user's requirements.
    Prioritizes the most relevant constraint.
    """

    # If at least one laptop matches, continue normally
    if laptops:
        return True

    print("\nNo suitable laptops match your requirements.\n")

    # Highest priority: 32 GB RAM requirement
    if prefs["min_ram_gb"] >= 32:
        print("32 GB RAM laptops are uncommon in this budget range.")
        print("Suggestion:")
        print("- Increase your budget, or")
        print("- Choose a 16 GB laptop (many models support future RAM upgrades).")
        save_no_recommendations(
            prefs,
            "No laptops match the selected budget and requirements."
        )
        return False

    # AI / ML requires a strong GPU
    # AI / ML requires a strong GPU
    if prefs["primary_use"] == "AI / Machine Learning":
        print("AI/ML workloads benefit greatly from a dedicated GPU.")

        print("Suggestion:")

        if prefs["budget"] < 70000:
            print("- Increase your budget to at least ₹70,000+ for a capable GPU laptop.")

        if prefs["min_ram_gb"] >= 32:
            print("- Consider reducing RAM requirement to 16 GB (many laptops support future upgrades).")

        if not prefs["needs_dgpu"]:
            print("- Select 'Yes' for dedicated GPU for better AI/ML performance.")

        print("- Cloud platforms like Google Colab can be used until you upgrade your hardware.")

        save_no_recommendations(
            prefs,
            "No laptops match the selected budget and requirements."
        )

        return False

    # Dedicated GPU requirement
    if prefs["needs_dgpu"]:
        print("No dedicated GPU laptops are available within this budget.")
        print("Suggestion:")
        print("- Increase your budget by ₹10,000 or more, or")
        print("- Select 'Not Sure' for dedicated GPU if your workloads are lighter.")
        save_no_recommendations(
            prefs,
            "No laptops match the selected budget and requirements."
        )
        return False

    # Generic fallback
    print("Your requirements are too restrictive for the selected budget.")
    print("Suggestion:")
    print("- Increase your budget, or")
    print("- Relax one or more requirements.")
    save_no_recommendations(
        prefs,
        "No laptops match the selected budget and requirements."
    )

    return False


# ==========================================================
# HELPERS
# ==========================================================

def to_number(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default



def ram_score(ram_gb):
    if ram_gb is None:
        return 50
    if ram_gb >= 32:
        return 100
    if ram_gb >= 16:
        return 80
    if ram_gb >= 8:
        return 40
    return 10



def weight_score(weight_kg):
    if weight_kg is None:
        return 50

    score = 100 - (weight_kg - 1.0) * 50
    return max(0, min(100, score))



def get_cpu_metric(laptop, key):
    cpu_info = laptop.get("cpu_info")
    if not cpu_info:
        return None
    return to_number(cpu_info.get(key))



def get_gpu_metric(laptop, key):
    gpu_info = laptop.get("gpu_info")
    if not gpu_info:
        return None
    return to_number(gpu_info.get(key))


# ==========================================================
# SCORING FUNCTIONS
# ==========================================================

def calculate_battery_score(laptop):
    battery_wh = to_number(laptop.get("battery_wh"), 50)
    cpu_eff = get_cpu_metric(laptop, "power_score")

    if cpu_eff is None:
        cpu_eff = 50

    score = (battery_wh + cpu_eff) / 2

    if laptop.get("has_dgpu"):
        score -= 15

    return max(0, min(100, score))



def calculate_portability_score(laptop):
    battery = calculate_battery_score(laptop)
    weight = weight_score(to_number(laptop.get("weight_kg")))

    score = (battery * 0.7) + (weight * 0.3)
    return max(0, min(100, score))



def calculate_performance_score(laptop):
    single = get_cpu_metric(laptop, "single_core_score")
    multi = get_cpu_metric(laptop, "multi_core_score")

    if single is None:
        single = 50
    if multi is None:
        multi = 50

    return (single * 0.4) + (multi * 0.6)

def calculate_video_editing_score(laptop):
    """
    Video Editing / 3D Rendering priority:
    50% GPU benchmark
    35% CPU multi-core
    15% RAM
    """

    if laptop.get("has_dgpu"):
        gpu_score = get_gpu_metric(laptop, "gaming_score")
        if gpu_score is None:
            gpu_score = 35
    else:
        gpu_score = get_cpu_metric(laptop, "integrated_gpu_score")
        if gpu_score is None:
            gpu_score = 15

    cpu_multi = get_cpu_metric(laptop, "multi_core_score")
    if cpu_multi is None:
        cpu_multi = 50

    ram = ram_score(laptop.get("ram_gb"))

    score = (
        gpu_score * 0.50
        + cpu_multi * 0.35
        + ram * 0.15
    )

    return score

def calculate_multitasking_score(laptop):
    ram = ram_score(laptop.get("ram_gb"))
    multi = get_cpu_metric(laptop, "multi_core_score")

    if multi is None:
        multi = 50

    return (ram * 0.4) + (multi * 0.6)



def calculate_gaming_score(laptop):
    """
    Gaming priority:
    75% GPU benchmark
    20% CPU single-core
    5% RAM
    """

    if laptop.get("has_dgpu"):
        gpu_score = get_gpu_metric(laptop, "gaming_score")
        if gpu_score is None:
            gpu_score = 40
    else:
        gpu_score = get_cpu_metric(laptop, "integrated_gpu_score")
        if gpu_score is None:
            gpu_score = 15

    cpu_single = get_cpu_metric(laptop, "single_core_score")
    if cpu_single is None:
        cpu_single = 50

    ram = ram_score(laptop.get("ram_gb"))

    score = (
        gpu_score * 0.75
        + cpu_single * 0.20
        + ram * 0.05
    )

    return score



def calculate_ai_ml_score(laptop):
    """
    AI / Machine Learning priority:
    60% GPU benchmark
    25% CPU multi-core
    15% RAM

    Strong penalty for laptops without dedicated GPU.
    """

    if laptop.get("has_dgpu"):
        gpu_score = get_gpu_metric(laptop, "gaming_score")
        if gpu_score is None:
            gpu_score = 40
    else:
        gpu_score = get_cpu_metric(laptop, "integrated_gpu_score")
        if gpu_score is None:
            gpu_score = 10

    cpu_multi = get_cpu_metric(laptop, "multi_core_score")
    if cpu_multi is None:
        cpu_multi = 50

    ram = ram_score(laptop.get("ram_gb"))

    score = (
        gpu_score * 0.60
        + cpu_multi * 0.25
        + ram * 0.15
    )

    if not laptop.get("has_dgpu"):
        score -= 20

    return max(0, score)



def calculate_general_use_score(laptop):
    battery = calculate_battery_score(laptop)
    performance = calculate_performance_score(laptop)
    portability = calculate_portability_score(laptop)

    return (battery * 0.4) + (performance * 0.3) + (portability * 0.3)


# ==========================================================
# SCORE DISPATCHER
# ==========================================================

def calculate_score(laptop, prefs):
    primary_use = prefs["primary_use"]

    if primary_use == "Gaming":
        score = calculate_gaming_score(laptop)

    elif primary_use == "Heavy Multitasking":
        score = calculate_multitasking_score(laptop)

    elif primary_use == "AI / Machine Learning":
        score = calculate_ai_ml_score(laptop)

    elif primary_use == "Programming / Coding":
        score = (
            calculate_performance_score(laptop) * 0.5
            + calculate_battery_score(laptop) * 0.3
            + calculate_multitasking_score(laptop) * 0.2
        )


    elif primary_use == "Video Editing / 3D Rendering":

        score = calculate_video_editing_score(laptop)

    else:
        score = calculate_general_use_score(laptop)

    # Battery modifier
    if prefs["battery_importance"] == "Very Important":
        score += calculate_battery_score(laptop) * 0.15
    elif prefs["battery_importance"] == "Moderately Important":
        score += calculate_battery_score(laptop) * 0.05

    # Travel modifier
    if prefs["travel_frequency"] == "Frequently":
        score += calculate_portability_score(laptop) * 0.15
    elif prefs["travel_frequency"] == "Occasionally":
        score += calculate_portability_score(laptop) * 0.05

    # Longevity modifier
    if prefs["longevity"] == "5+ Years":
        score += calculate_performance_score(laptop) * 0.10
        score += ram_score(laptop.get("ram_gb")) * 0.05

    return round(score, 2)


# ==========================================================
# RECOMMENDATION REASON
# ==========================================================

def get_reason(laptop, prefs):
    use = prefs["primary_use"]

    battery = calculate_battery_score(laptop)
    portability = calculate_portability_score(laptop)
    performance = calculate_performance_score(laptop)
    multitasking = calculate_multitasking_score(laptop)
    gaming = calculate_gaming_score(laptop)

    price = laptop.get("price_inr")
    ram = laptop.get("ram_gb")
    has_dgpu = laptop.get("has_dgpu", False)

    if use == "Gaming":
        if has_dgpu:
            gpu_name = laptop.get("gpu", "Dedicated GPU")
            return f"{gpu_name} provides the best gaming performance available in your budget"

        return (
            "Offers the best integrated graphics performance in your budget, "
            "but if gaming is your top priority, you should strongly consider "
            "a laptop with a dedicated GPU (dGPU) for much better performance."
        )

    if use == "AI / Machine Learning":
        if has_dgpu:
            gpu_name = laptop.get("gpu", "Dedicated GPU")
            return f"{gpu_name} and strong multi-core CPU performance make it ideal for local AI and ML workloads"
        return "Suitable for learning AI/ML, but a dedicated GPU is strongly recommended for model training"

    if use == "Heavy Multitasking":
        if ram >= 32:
            return "32 GB RAM and strong multi-core performance make it excellent for heavy multitasking"
        if ram >= 16:
            return "16 GB RAM and strong multi-core performance are ideal for multitasking"
        return "Balanced CPU and RAM performance for moderate multitasking"

    if use == "Programming / Coding":
        if battery >= 75:
            return "Combines strong performance with excellent battery life for coding on the go"
        return "Strong CPU performance and sufficient RAM for programming workloads"

    if use == "Video Editing / 3D Rendering":
        if has_dgpu:
            gpu_name = laptop.get("gpu", "Dedicated GPU")
            return f"{gpu_name} and strong CPU performance make it excellent for video editing and rendering"
        return "Good for light editing, but a dedicated GPU is recommended for heavier creative workloads"

    # General Use / default
    if battery >= 80 and portability >= 80:
        return "Outstanding battery life and lightweight design make it ideal for everyday use"

    if battery >= 75:
        return "Offers some of the best battery life in your budget"

    if portability >= 80:
        return "Very lightweight and easy to carry for daily travel"

    if performance >= 80:
        return "Delivers stronger CPU performance than most laptops in this budget"

    if price is not None:
        return "Well-balanced specifications and strong value for the price"

    return "A balanced option for your requirements"


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

def display_results(laptops, prefs):
    if not laptops:
        print("No recommendations available.")
        return

    # Score laptops according to user's selected priority
    scored = []

    for laptop in laptops:
        score = calculate_score(laptop, prefs)
        scored.append((score, laptop))

    # Sort by priority score
    scored.sort(key=lambda x: x[0], reverse=True)

    # Top 2 according to user's priority
    top_recommendations = scored[:2]

    # ------------------------------------------------------
    # Find Overall Good Buy
    # Balanced scoring irrespective of user priority
    # ------------------------------------------------------
    balanced_scores = []

    for laptop in laptops:
        balanced_score = calculate_general_use_score(laptop)

        # Reward value for money
        price = laptop.get("price_inr", 100000)
        value_bonus = max(0, (100000 - price) / 5000)

        overall_score = balanced_score + value_bonus
        balanced_scores.append((overall_score, laptop))

    balanced_scores.sort(key=lambda x: x[0], reverse=True)

    # Select best laptop not already in top recommendations
    top_ids = {
        id(laptop)
        for _, laptop in top_recommendations
    }

    overall_good_buy = None

    for _, laptop in balanced_scores:
        if id(laptop) not in top_ids:
            overall_good_buy = laptop
            break

    # If all laptops overlap, use the top balanced laptop
    if overall_good_buy is None and balanced_scores:
        overall_good_buy = balanced_scores[0][1]

    # ------------------------------------------------------
    # Display Top 2 Recommendations
    # ------------------------------------------------------
    print("\n" + "=" * 70)
    print("TOP RECOMMENDATIONS")
    print("=" * 70)

    for rank, (score, laptop) in enumerate(top_recommendations, start=1):
        print(f"\n{rank}. {laptop.get('brand', '')} {laptop.get('model', '')}")
        print(f"   Score: {score:.2f}")
        print(f"   Price: ₹{laptop.get('price_inr', 'N/A'):,}")
        print(f"   CPU: {laptop.get('cpu', 'N/A')}")
        print(f"   GPU: {laptop.get('gpu', 'N/A')}")
        print(f"   RAM: {laptop.get('ram_gb', 'N/A')} GB")
        print(f"   Battery: {laptop.get('battery_wh', 'N/A')} Wh")
        print(f"   Weight: {laptop.get('weight_kg', 'N/A')} kg")
        print(f"   Why recommended: {get_reason(laptop, prefs)}")

    # ------------------------------------------------------
    # Display Overall Good Buy
    # ------------------------------------------------------
    if overall_good_buy:
        print("\n" + "=" * 70)
        print("OVERALL GOOD BUY")
        print("=" * 70)

        print(f"\n{overall_good_buy.get('brand', '')} {overall_good_buy.get('model', '')}")
        print(f"Price: ₹{overall_good_buy.get('price_inr', 'N/A'):,}")
        print(f"CPU: {overall_good_buy.get('cpu', 'N/A')}")
        print(f"GPU: {overall_good_buy.get('gpu', 'N/A')}")
        print(f"RAM: {overall_good_buy.get('ram_gb', 'N/A')} GB")
        print(f"Battery: {overall_good_buy.get('battery_wh', 'N/A')} Wh")
        print(f"Weight: {overall_good_buy.get('weight_kg', 'N/A')} kg")
        print("Why this is a good buy: Offers the best balance of performance, battery life, portability, and value for money.")


    save_recommendations(prefs, top_recommendations, overall_good_buy)


def save_no_recommendations(prefs, reason):
    output = {
        "user_preferences": prefs,
        "top_recommendations": [],
        "overall_good_buy": None,
        "no_recommendations": True,
        "reason": reason
    }

    with open("recommended_laptops.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print("\nSaved no-recommendation result to recommended_laptops.json")

def save_recommendations(prefs, top_recommendations, overall_good_buy):
    """
    Saves the latest recommendations to recommended_laptops.json.
    The file is overwritten each time, so old recommendations are removed.
    """

    output = {
        "user_preferences": prefs,
        "top_recommendations": [],
        "overall_good_buy": None
    }

    # Save top 2 recommendations
    for rank, (score, laptop) in enumerate(top_recommendations, start=1):
        item = {
            "rank": rank,
            "score": round(score, 2),
            "brand": laptop.get("brand"),
            "model": laptop.get("model"),
            "price_inr": laptop.get("price_inr"),
            "cpu": laptop.get("cpu"),
            "gpu": laptop.get("gpu"),
            "ram_gb": laptop.get("ram_gb"),
            "battery_wh": laptop.get("battery_wh"),
            "weight_kg": laptop.get("weight_kg"),
            "has_dgpu": laptop.get("has_dgpu"),
            "why_recommended": get_reason(laptop, prefs)
        }

        output["top_recommendations"].append(item)

    # Save overall good buy
    if overall_good_buy:
        output["overall_good_buy"] = {
            "brand": overall_good_buy.get("brand"),
            "model": overall_good_buy.get("model"),
            "price_inr": overall_good_buy.get("price_inr"),
            "cpu": overall_good_buy.get("cpu"),
            "gpu": overall_good_buy.get("gpu"),
            "ram_gb": overall_good_buy.get("ram_gb"),
            "battery_wh": overall_good_buy.get("battery_wh"),
            "weight_kg": overall_good_buy.get("weight_kg"),
            "has_dgpu": overall_good_buy.get("has_dgpu"),
            "why_recommended": (
                "Offers the best balance of performance, battery life, "
                "portability, and value for money."
            )
        }


    # Overwrite file every time
    with open("recommended_laptops.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print("\nSaved recommendations to recommended_laptops.json")
# ==========================================================
# MAIN
# ==========================================================

def main():
    print("=" * 70)
    print("LAPTOP RECOMMENDATION ENGINE")
    print("=" * 70)

    laptops = load_json("laptops.json")
    cpu_data = load_json("CPU_info.json")
    gpu_data = load_json("GPU_out.json")

    if not laptops:
        return

    cpu_lookup = build_cpu_lookup(cpu_data)
    gpu_lookup = build_gpu_lookup(gpu_data)

    enriched_laptops = [
        enrich_laptop(laptop, cpu_lookup, gpu_lookup)
        for laptop in laptops
    ]

    prefs = collect_user_preferences()

    filtered = filter_laptops(enriched_laptops, prefs)

    if not validate_requirements(filtered, prefs):
        return

    display_results(filtered, prefs)


if __name__ == "__main__":
    main()
