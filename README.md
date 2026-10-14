# Restaurant Location-Based Analysis

**Cognifyz Technologies — Machine Learning Task 4**

An interactive dashboard to explore restaurant coordinates, distribution by city/locality, ratings, cuisines, and price ranges using the supplied restaurant dataset.

## Features

- Interactive restaurant map using latitude and longitude.
- Filters for city, locality, aggregate rating, and price range.
- Restaurant count, number of cities, average rating, and mapped restaurant KPIs.
- City-level concentration and average-rating comparisons.
- Locality-level summary table.
- Most common cuisines, price-range distribution, and average-cost histogram.
- Download filtered restaurant data and city summary as CSV files.
- Handles missing coordinates and excludes (0, 0) coordinates from the map.

## Project structure

```text
cognifyz_location_analysis/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── Dataset.csv
```

## Requirements

- Python 3.10 or newer
- Internet connection when installing packages (the map tiles also need an internet connection)

## Run in VS Code (Windows)

1. Extract the ZIP file.
2. Open the extracted `cognifyz_location_analysis` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

5. Activate it in Command Prompt:

   ```bat
   .venv\Scripts\activate
   ```

   If PowerShell is used:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

6. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

7. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

8. Streamlit will print a local URL, normally `http://localhost:8501`. Open it in your browser.

## Run in Google Colab

This project is designed as a local Streamlit application. The simplest approach is to run it in VS Code. In Colab, you would need extra setup to expose the Streamlit server.

## Task objective mapping

| Cognifyz task requirement | Implemented in |
|---|---|
| Explore latitude/longitude and visualize restaurant distribution | Restaurant Map tab |
| Group restaurants by city or locality | City & Locality tab |
| Compare average ratings by area | City & Locality tab |
| Analyze cuisines by city/locality | Cuisines & Prices tab and filters |
| Analyze price ranges by area | City & Locality and Cuisines & Prices tabs |
| Identify location patterns | Map and comparison charts |

## Important data notes

- The dashboard analyzes the supplied dataset; it does not fetch live restaurant information.
- Coordinates that are missing, outside valid latitude/longitude ranges, or exactly `(0, 0)` are excluded from the map.
- Rating averages ignore missing ratings. Dataset rows remain available in the data explorer.
- “Price range” is the dataset's rating/category field, not a universal currency amount. Average cost for two is shown separately.
- Dataset currency values may differ between cities/countries; compare costs within compatible currency groups.

## GitHub upload

1. Create a new public repository, for example `cognifyz-location-based-analysis`.
2. Extract the ZIP and upload the **contents** of the project folder.
3. Include `app.py`, `requirements.txt`, `README.md`, `.gitignore`, and `data/Dataset.csv`.
4. Click **Commit changes**.
5. In the repository, copy the URL and add it to your resume or LinkedIn post.

Avoid uploading `.venv/`, `__pycache__/`, or private credentials. The included dataset is about 2.2 MB, below GitHub's regular 100 MB per-file limit.
