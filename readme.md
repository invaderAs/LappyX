# LappyX

LappyX is a Python-based laptop recommendation engine that helps users choose the best laptop based on their budget, workload, and personal priorities.

The project uses real CPU and GPU benchmark data to rank laptops for tasks such as programming, gaming, AI and machine learning, video editing, and general use.

Development is currently in the initial stage. The core recommendation engine is functional, but data collection, benchmark scraping, and dataset generation are still being improved.

## Features

* Budget-based laptop filtering
* Personalized recommendations based on user priorities
* Benchmark-based scoring using CPU and GPU performance data
* Constraint validation for unrealistic requirements
* Gemini-powered summaries and trade-off analysis
* Support for gaming laptops, thin and light laptops, premium laptops, and Copilot+ PCs

## Current Dataset

* 74+ laptop models
* Price range from ₹40,000 to ₹2,00,000+
* CPU benchmark data from NanoReview
* GPU benchmark data from NanoReview
* 8 GB, 16 GB, and 32 GB RAM configurations

## Project Structure

```text
LappyX/
├── name.txt
├── nametojson.py
├── laptops.json
├── cpu_scraper.py
├── gpu_scraper.py
├── CPU_info.json
├── GPU_out.json
├── recommend_cli.py
├── gemini_review.py
├── ALL_process.py
├── recommended_laptops.json
├── final_report.txt
├── README.md
├── requirements.txt
└── .gitignore
```

## How the Project Works

### 1. Raw Data Collection

Laptop listings are collected as unstructured text in `name.txt`.

### 2. Conversion to JSON

The data in `name.txt` is converted into `laptops.json`.

The script `nametojson.py` exists for this purpose, but it still requires additional work to extract specifications accurately.

For now, the recommended approach is to use an AI model to convert the raw text into structured JSON more accurately.

### 3. Benchmark Scraping

Run:

* `cpu_scraper.py`
* `gpu_scraper.py`

These scripts scrape benchmark scores from NanoReview and save them to:

* `CPU_info.json`
* `GPU_out.json`

Some CPUs and GPUs may fail to scrape if NanoReview uses a different URL format. These cases may need to be corrected manually.

### 4. Recommendation Engine

`recommend_cli.py` asks the user a series of questions, including:

1. Maximum budget
2. Primary use case
3. Battery life importance
4. Travel frequency
5. Minimum RAM requirement
6. Dedicated GPU requirement
7. Expected years of usage

The script filters eligible laptops and calculates a score using benchmark data and user priorities.

### 5. Gemini Review

`gemini_review.py` analyzes the recommended laptops and generates a concise summary of:

* Strengths
* Weaknesses
* Trade-offs
* Best overall choice

### 6. Full Automation

`ALL_process.py` runs:

1. `recommend_cli.py`
2. `gemini_review.py`

This produces both recommendations and AI-generated analysis in one step.

## Installation

### Clone the Repository

```bash
git clone https://github.com/invaderAs/LappyX.git
cd LappyX
```

### Create a Virtual Environment (Optional)

```bash
python -m venv .venv
```

### Activate the Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Requirements

```text
requests
beautifulsoup4
google-genai
```

## Usage

### Recommendation Engine Only

If you do not want to use Gemini, run:

```bash
python recommend_cli.py
```

### Gemini Review Only

Run after recommendations have been generated:

```bash
python gemini_review.py
```

### Full Workflow

Run both recommendation and Gemini analysis:

```bash
python ALL_process.py
```

### Scrape Benchmark Data

```bash
python cpu_scraper.py
python gpu_scraper.py
```

## Gemini Setup

To use Gemini summaries, open `gemini_review.py` and replace:

```python
api_key = "YOUR_GEMINI_API_KEY"
```

with your own Gemini API key.

If you do not want to use Gemini, simply run:

```bash
python recommend_cli.py
```

## Output Files

Generated files include:

* `recommended_laptops.json`
* `final_report.txt`

These files are created automatically during execution.

## Notes

* Development is in the initial stage.
* `nametojson.py` is still being improved and may not always extract data accurately.
* Converting `name.txt` to `laptops.json` is currently done manually or with the help of an AI model.
* Some benchmark scraping failures are expected because NanoReview URL formats are not always consistent.
* Recommendation quality will improve as more laptop data is added.

## Future Improvements

* Improve `nametojson.py`
* Add more laptops to the dataset
* Improve CPU and GPU URL matching
* Build a web application
* Add RAM and SSD upgradeability support
* Add automated testing
* Add real-time price updates

## License

This project is released under the MIT License.
