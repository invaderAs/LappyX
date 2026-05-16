import subprocess
import sys


def run_script(script_name):
    print(f"\nRunning {script_name}...\n")

    result = subprocess.run([sys.executable, script_name])

    if result.returncode != 0:
        print(f"\nError while running {script_name}")
        sys.exit(1)


def main():
    # Step 1: Generate recommendations
    run_script("recommend_cli.py")

    # Step 2: Generate Gemini summary
    run_script("gemini_reviews.py")

    print("\nPipeline completed successfully.")
    print("Final output saved in final_report.txt")


if __name__ == "__main__":
    main()