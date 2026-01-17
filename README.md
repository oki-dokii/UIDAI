# Aadhaar Data Analysis Project 🇮🇳

## Overview
This project performs a comprehensive data analysis of Aadhaar enrolment and update trends in India. By synthesizing diverse datasets (Enrolment, Biometric Updates, Demographic Updates), we derive actionable insights into:
- **Operational efficiency** of Aadhaar centers.
- **Regional disparities** in service adoption.
- **Societal interaction patterns** (e.g., migration-driven updates).

## Key Features
- **Data Pipeline**: Robust cleaning, normalization (State names), and merging of large-scale CSV datasets.
- **Metrics Engine**: Computation of `Update Intensity`, `Biometric vs Demographic Share`, and `Volatility Index`.
- **Advanced Analytics**:
  - **Pareto Analysis**: Identifying critical districts driving national volume.
  - **Seasonality**: Uncovering weekly operational patterns.
  - **Trivariate Analysis**: Exploring complex State x Time x Volume interactions.
- **Visualizations**: Heatmaps, Bubble Charts, Risk Matrices, and Time Series.

## Repository Structure
- `aadhaar_analysis.py`: Main ETL and Analysis script.
- `aadhaar_plots/`: generated high-quality visualizations (PNG).
- `requirements.txt`: Python dependencies.

## Key Insights (Preview)
1.  **Weekly Pattern**: A surge in updates on Saturdays followed by a sharp drop on Sundays indicates effective weekend camps.
2.  **Pareto Principle**: While not a strict 80/20, the top 30% of districts drive the majority of update traffic.
3.  **Risk Matrix**: We classify districts into "High Stress/Volatile" (Campaign mode) vs "High Load/Stable" (Mature centers) for targeted resource allocation.

## Installation & Usage

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/oki-dokii/UIDAI.git
    cd UIDAI
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Analysis**:
    Ensure your data is in the expected `Downloads` structure (or modify `DATA_BASE_DIR` in the script).
    ```bash
    python aadhaar_analysis.py
    ```

## Outputs
Plots will be generated in the `aadhaar_plots/` directory.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
