\# LappyX



\*\*LappyX\*\* is a Python-based laptop recommendation engine designed to help users navigate the often-confusing world Filtering: Finds the best value within your price range.



\* \*\*Personalized Recommendations:\*\* Tailors suggestions based on what \*you\* care about most.

\* \*\*Benchmark-driven Scoring:\*\* Uses real CPU and GPU performance data rather than just marketing specs.

\* \*\*Constraint Validation:\*\* Gently lets you know if your requirements are unrealistic for your budget.

\* \*\*Gemini-powered Analysis:\*\* Provides AI-generated summaries of trade-offs for each recommendation.

\* \*\*Diverse Category Support:\*\* Covers gaming rigs, thin-and-lights, premium ultrabooks, and Copilot+ PCs.



\---



\## 📊 Current Dataset



\* \*\*Models:\*\* 74+ laptop models.

\* \*\*Price Range:\*\* ₹40,000 to ₹2,00,000+.

\* \*\*Data Sources:\*\* CPU and GPU benchmarks scraped from \*\*NanoReview\*\*.

\* \*\*Memory:\*\* Configurations including 8 GB, 16 GB, and 32 GB RAM.



\---



\## 📂 Project Structure



```text

LappyX/

├── name.txt             # Unstructured raw 🛠️ Installation



1\.  \*\*Clone the Repository:\*\*

&#x20;   ```bash

&#x20;   git clone \[https://github.com/YOUR\_USERNAME/Lappy](https://github.com/YOUR\_USERNAME/Lappy) laptop listings

├── nametojson.py        # Script to parse listings into JSON

├── laptops.json         # The main laptop database

├── cpu\_X.git

&#x20;   cd LappyX

&#x20;   ```



2\.  \*\*Create a Virtual Environment (Optional):\*\*

&#x20;   ```bash

&#x20;   pythonscraper.py       # Scraper for CPU benchmarks

├── gpu\_scraper.py       # Scraper for GPU benchmarks

├── CPU\_info.json        # -m venv .venv

&#x20;   ```



3\.  \*\*Activate the Environment:\*\*

&#x20;   \*   \*\*Windows:\*\* `.venv\\Scripts\\activate Scraped CPU scores

├── GPU\_out.json         # Scraped GPU scores

├── recommend\_cli.py     # Main CLI for user interaction

├── gemini\_review`

&#x20;   \*   \*\*Linux/macOS:\*\* `source .venv/bin/activate`



4\.  \*\*Install Dependencies:\*\*

&#x20;   ```bash

.py     # AI analysis script

├── ALL\_process.py       # Master script to run full workflow

├── README.md            # Project documentation

├── requirements.txt    pip install -r requirements.txt

&#x20;   ```



\---



\## 🖥️ Usage



| Option | Command | Description |

| :--- | :---     # Python dependencies

└── .gitignore           # Git ignore rules



```



\---



\## ⚙️ How It Works



1\. \*\*Raw Data Collection:\*\* Laptop listings are stored as unstructured text in `name.txt`.

2\. \*\*JSON Conversion:\*\* `nametojson.py` converts text to structured data. \*Current tip: Use an LLM for more accurate parsing while the script is being optimized.\*

3\. \*\*Benchmark Scraping:\*\* `cpu\_scraper.py` and `gpu\_scraper.py` pull the latest scores from NanoReview.

4\. \*\*Recommendation Engine:\*\* `recommend\_cli.py` filters the database and scores laptops based on your specific workload.

5\. \*\*Gemini Review:\*\* `gemini\_review.py` creates a concise summary of strengths, weaknesses, and trade-offs.

6\. \*\*Full Automation:\*\* `ALL\_process.py` runs the recommendation engine and the AI review in one go.



\---



\## 🛠️ Installation



\### 1. Clone the Repository



```bash

git clone https://github.com/YOUR\_USERNAME/LappyX.-readable summary and AI analysis.git

cd LappyX



```



\### 2. Set Up Environment (Recommended)



\*\*Windows:\*\*



```bash

python -m venv .venv

.venv\\Scripts\\activate



```



\*\*Linux/macOS:\*\*



```bash

python -m venv .venv

source .venv/bin/activate



```



\### 3. Install Dependencies



```bash

pip install -r requirements.txt



```



\---



\## 📖 Usage



| Option | Command | Description |

| --- | --- | --- |

| \*\*Full Workflow\*\* | `python ALL\_process.py` | Runs recommendations + Gemini AI analysis. |

| \*\*Engine Only\*\* | `python recommend\_cli.py` | Get recommendations without AI summaries. |

| \*\*AI Review Only\*\* | `python gemini\_review.py` | Generate analysis for existing recommendations. |

| \*\*Scrape Data\*\* | `python cpu\_scraper.py` | Update CPU/GPU benchmark databases. |



\### Gemini Setup



To enable AI summaries, edit `gemini\_review.py` and add your API key:

`api\_key = "YOUR\_GEMINI\_API\_KEY"`



\---



\## 📝 Output Files



Execution results in the following files:



\* `recommended\_laptops.json`: The raw filtered data.

\* `final\_report.txt`: The human-readable report including AI analysis.

