#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - FORECAST ANALYSIS
Implements time-series forecasting using Prophet/statsmodels for:
1. National Enrolment Forecast (6-month projection)
2. National Updates Forecast
3. District Risk Analysis (declining trends)

Outputs: Forecast visualizations with confidence intervals
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# Try Prophet first, fall back to statsmodels ARIMA
try:
    from prophet import Prophet
    HAS_PROPHET = True
    print("✅ Using Prophet for forecasting")
except ImportError:
    HAS_PROPHET = False
    try:
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        print("✅ Using statsmodels for forecasting")
    except ImportError:
        print("⚠️ Neither Prophet nor statsmodels available. Using simple trend extrapolation.")

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "integrated_analysis", "integrated_data.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "forecast_plots")

# Forecast parameters
FORECAST_MONTHS = 6

# ============================================================================
# DATA LOADING
# ============================================================================

def load_and_prepare_data():
    """Load and prepare time series data."""
    print(f"📂 Loading data from: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    print(f"   Loaded {len(df):,} records")
    
    # Create date column
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2) + '-01')
    
    # Aggregate to monthly national totals
    monthly = df.groupby('date').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'total_demo': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    
    monthly = monthly.sort_values('date')
    print(f"   {len(monthly)} months of data from {monthly['date'].min()} to {monthly['date'].max()}")
    
    return df, monthly


def prepare_prophet_data(monthly, value_col):
    """Prepare data for Prophet format."""
    prophet_df = monthly[['date', value_col]].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    return prophet_df


# ============================================================================
# FORECASTING FUNCTIONS
# ============================================================================

def forecast_with_prophet(monthly, value_col, periods=FORECAST_MONTHS):
    """Generate forecast using Prophet."""
    if not HAS_PROPHET:
        return None, None
    
    # Prepare data
    prophet_df = prepare_prophet_data(monthly, value_col)
    
    # Train model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.80
    )
    model.fit(prophet_df)
    
    # Make future dataframe
    future = model.make_future_dataframe(periods=periods, freq='MS')
    
    # Predict
    forecast = model.predict(future)
    
    return model, forecast


def forecast_with_simple_trend(monthly, value_col, periods=FORECAST_MONTHS):
    """Simple linear trend extrapolation as fallback."""
    
    ts = monthly.set_index('date')[value_col]
    
    # Calculate linear trend
    x = np.arange(len(ts))
    y = ts.values
    
    # Remove any NaN/inf
    mask = np.isfinite(y)
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 2:
        return None
    
    # Fit linear model
    coeffs = np.polyfit(x_clean, y_clean, 1)
    
    # Generate future dates
    last_date = monthly['date'].max()
    future_dates = [last_date + pd.DateOffset(months=i+1) for i in range(periods)]
    
    # Predict
    future_x = np.arange(len(ts), len(ts) + periods)
    predictions = np.polyval(coeffs, future_x)
    
    # Calculate simple confidence interval (based on historical std)
    std = np.std(y_clean)
    
    forecast = pd.DataFrame({
        'ds': future_dates,
        'yhat': predictions,
        'yhat_lower': predictions - 1.96 * std,
        'yhat_upper': predictions + 1.96 * std
    })
    
    return forecast


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_forecast(monthly, forecast, value_col, title, output_file, color='#1f77b4'):
    """Create forecast visualization with confidence intervals."""
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Historical data
    ax.plot(monthly['date'], monthly[value_col], 
            'o-', color=color, linewidth=2, markersize=6, 
            label='Historical', alpha=0.8)
    
    # Forecast
    if forecast is not None:
        # Convert ds to datetime if needed
        if 'ds' in forecast.columns:
            forecast_dates = pd.to_datetime(forecast['ds'])
        else:
            forecast_dates = forecast.index
        
        # Only plot future values
        last_historical = monthly['date'].max()
        future_mask = forecast_dates > last_historical
        
        if future_mask.sum() > 0:
            future_dates = forecast_dates[future_mask]
            future_values = forecast['yhat'][future_mask]
            future_lower = forecast['yhat_lower'][future_mask]
            future_upper = forecast['yhat_upper'][future_mask]
            
            # Plot forecast line
            ax.plot(future_dates, future_values, 
                    '--', color='#d62728', linewidth=2.5, 
                    label=f'{FORECAST_MONTHS}-Month Forecast')
            
            # Plot confidence interval
            ax.fill_between(future_dates, future_lower, future_upper, 
                           color='#d62728', alpha=0.2, label='80% Confidence Interval')
            
            # Add forecast values as annotations
            for date, val in zip(future_dates, future_values):
                ax.annotate(f'{val/1e6:.1f}M', 
                           (date, val),
                           textcoords='offset points',
                           xytext=(0, 10),
                           ha='center', fontsize=9, color='#d62728')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Format y-axis in millions
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
    
    # Grid and legend
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', framealpha=0.9)
    
    # Vertical line at forecast start
    ax.axvline(x=monthly['date'].max(), color='gray', linestyle=':', alpha=0.7)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


def analyze_district_trends(df):
    """Identify districts with declining trends."""
    
    # Group by district and calculate trend
    district_trends = []
    
    for (state, district), group in df.groupby(['state', 'district']):
        if len(group) < 2:
            continue
        
        group = group.sort_values('date')
        
        # Calculate simple trend (slope of total activity)
        x = np.arange(len(group))
        y = group['total_updates'].values + group['total_enrol'].values
        
        if len(x) >= 2 and np.std(y) > 0:
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            
            district_trends.append({
                'state': state,
                'district': district,
                'slope': slope,
                'mean_activity': np.mean(y),
                'n_months': len(group)
            })
    
    trends_df = pd.DataFrame(district_trends)
    
    # Calculate relative slope (% change per month)
    trends_df['relative_slope'] = (trends_df['slope'] / trends_df['mean_activity']) * 100
    
    return trends_df


def plot_declining_districts(trends_df, output_file, n_top=20):
    """Visualize districts with steepest decline."""
    
    # Get most declining districts
    declining = trends_df.nsmallest(n_top, 'relative_slope').copy()
    declining['district_label'] = declining['district'] + '\n(' + declining['state'].str[:3] + ')'
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    colors = ['#d62728' if x < 0 else '#2ca02c' for x in declining['relative_slope']]
    
    bars = ax.barh(declining['district_label'], declining['relative_slope'], 
                  color=colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars, declining['relative_slope']):
        width = bar.get_width()
        ax.annotate(f'{val:.1f}%', 
                   xy=(width, bar.get_y() + bar.get_height()/2),
                   xytext=(-5 if width < 0 else 5, 0),
                   textcoords='offset points',
                   ha='right' if width < 0 else 'left',
                   va='center', fontsize=9, fontweight='bold')
    
    # Styling
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Monthly Change Rate (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_title(f'🚨 Top {n_top} Districts with Declining Activity\n(Requires Immediate Attention)', 
                fontsize=14, fontweight='bold', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    return declining


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("📈 UIDAI FORECAST ANALYSIS")
    print(f"    Generating {FORECAST_MONTHS}-Month Predictions")
    print("=" * 60)
    
    # Load data
    df, monthly = load_and_prepare_data()
    
    print("\n" + "=" * 60)
    print("🔮 GENERATING FORECASTS")
    print("=" * 60)
    
    # 1. Enrolment Forecast
    print("\n1️⃣ Forecasting Total Enrolments...")
    if HAS_PROPHET:
        _, forecast_enrol = forecast_with_prophet(monthly, 'total_enrol')
    else:
        forecast_enrol = forecast_with_simple_trend(monthly, 'total_enrol')
    
    plot_forecast(monthly, forecast_enrol, 'total_enrol',
                 '📊 National Enrolment Forecast\nUIDAI Data Hackathon 2026',
                 '01_enrolment_forecast.png',
                 color='#1f77b4')
    
    # 2. Updates Forecast
    print("\n2️⃣ Forecasting Total Updates...")
    if HAS_PROPHET:
        _, forecast_updates = forecast_with_prophet(monthly, 'total_updates')
    else:
        forecast_updates = forecast_with_simple_trend(monthly, 'total_updates')
    
    plot_forecast(monthly, forecast_updates, 'total_updates',
                 '📊 National Updates Forecast\nUIDAI Data Hackathon 2026',
                 '02_updates_forecast.png',
                 color='#ff7f0e')
    
    # 3. District Risk Analysis
    print("\n3️⃣ Analyzing District Trends...")
    trends = analyze_district_trends(df)
    declining = plot_declining_districts(trends, '03_declining_districts.png')
    
    # Save declining districts to CSV
    declining_path = os.path.join(OUTPUT_DIR, 'declining_districts.csv')
    declining.to_csv(declining_path, index=False)
    print(f"   ✅ Saved: {declining_path}")
    
    # 4. Combined Forecast Summary
    print("\n4️⃣ Creating Forecast Summary...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Enrolment subplot
    axes[0].plot(monthly['date'], monthly['total_enrol'], 'o-', color='#1f77b4', linewidth=2, markersize=5)
    if forecast_enrol is not None:
        last_date = monthly['date'].max()
        future_mask = pd.to_datetime(forecast_enrol['ds']) > last_date
        if future_mask.sum() > 0:
            axes[0].plot(pd.to_datetime(forecast_enrol['ds'][future_mask]), 
                        forecast_enrol['yhat'][future_mask], '--', color='#d62728', linewidth=2)
    axes[0].set_title('Enrolment Forecast', fontweight='bold')
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
    axes[0].grid(True, alpha=0.3)
    
    # Updates subplot
    axes[1].plot(monthly['date'], monthly['total_updates'], 'o-', color='#ff7f0e', linewidth=2, markersize=5)
    if forecast_updates is not None:
        last_date = monthly['date'].max()
        future_mask = pd.to_datetime(forecast_updates['ds']) > last_date
        if future_mask.sum() > 0:
            axes[1].plot(pd.to_datetime(forecast_updates['ds'][future_mask]), 
                        forecast_updates['yhat'][future_mask], '--', color='#d62728', linewidth=2)
    axes[1].set_title('Updates Forecast', fontweight='bold')
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
    axes[1].grid(True, alpha=0.3)
    
    plt.suptitle('📈 UIDAI 6-Month National Forecast\nUIDAI Data Hackathon 2026', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, '04_forecast_summary.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ FORECAST ANALYSIS COMPLETE")
    print(f"   Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    
    # Print insights
    print("\n📊 FORECAST INSIGHTS:")
    
    if forecast_enrol is not None:
        future_enrol = forecast_enrol[pd.to_datetime(forecast_enrol['ds']) > monthly['date'].max()]['yhat'].iloc[-1]
        current_enrol = monthly['total_enrol'].iloc[-1]
        change = ((future_enrol - current_enrol) / current_enrol) * 100
        print(f"\n   📈 Enrolment Forecast ({FORECAST_MONTHS} months):")
        print(f"      Current: {current_enrol/1e6:.2f}M → Projected: {future_enrol/1e6:.2f}M ({change:+.1f}%)")
    
    if forecast_updates is not None:
        future_updates = forecast_updates[pd.to_datetime(forecast_updates['ds']) > monthly['date'].max()]['yhat'].iloc[-1]
        current_updates = monthly['total_updates'].iloc[-1]
        change = ((future_updates - current_updates) / current_updates) * 100
        print(f"\n   📈 Updates Forecast ({FORECAST_MONTHS} months):")
        print(f"      Current: {current_updates/1e6:.2f}M → Projected: {future_updates/1e6:.2f}M ({change:+.1f}%)")
    
    n_declining = len(trends[trends['relative_slope'] < -5])
    print(f"\n   🚨 Districts with >5% monthly decline: {n_declining}")


if __name__ == "__main__":
    main()
