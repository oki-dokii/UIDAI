#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Interactive CLI Tool
A professional command-line interface for Aadhaar data analysis.

Usage:
    python uidai.py analyze --state "Delhi"
    python uidai.py dashboard
    python uidai.py forecast
    python uidai.py anomalies
    python uidai.py report --state "Maharashtra"
"""

import os
import sys
import warnings
from typing import Optional

warnings.filterwarnings('ignore')

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.tree import Tree
from rich.columns import Columns

import typer
import pandas as pd
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "integrated_analysis", "integrated_data.csv")

console = Console()
app = typer.Typer(
    name="uidai",
    help="🎯 UIDAI Data Hackathon 2026 - Interactive Analysis CLI",
    add_completion=False
)

# ============================================================================
# DATA LOADING
# ============================================================================
def load_data():
    """Load the integrated dataset."""
    if not os.path.exists(DATA_FILE):
        console.print(f"[red]❌ Data file not found: {DATA_FILE}[/red]")
        console.print("[yellow]Run integrated_analysis.py first.[/yellow]")
        raise typer.Exit(1)
    
    df = pd.read_csv(DATA_FILE)
    return df

# ============================================================================
# COMMANDS
# ============================================================================

@app.command()
def dashboard():
    """📊 Display national-level dashboard with key metrics."""
    
    console.print(Panel.fit(
        "[bold blue]UIDAI DATA HACKATHON 2026[/bold blue]\n"
        "[dim]Unlocking Societal Trends in Aadhaar Data[/dim]",
        border_style="blue"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Loading data...", total=None)
        df = load_data()
    
    # National KPIs
    total_enrol = df['total_enrol'].sum()
    total_updates = df['total_updates'].sum()
    total_demo = df['total_demo'].sum()
    total_bio = df['total_bio'].sum()
    ratio = total_updates / total_enrol if total_enrol > 0 else 0
    avg_gap = df['child_attention_gap'].mean()
    n_states = df['state'].nunique()
    n_districts = df[['state', 'district']].drop_duplicates().shape[0]
    
    # KPI Table
    kpi_table = Table(title="📈 National Key Performance Indicators", box=box.ROUNDED)
    kpi_table.add_column("Metric", style="cyan", no_wrap=True)
    kpi_table.add_column("Value", style="green", justify="right")
    kpi_table.add_column("Insight", style="dim")
    
    kpi_table.add_row("Total Enrolments", f"{total_enrol:,.0f}", "New Aadhaar registrations")
    kpi_table.add_row("Total Updates", f"{total_updates:,.0f}", "Demo + Biometric combined")
    kpi_table.add_row("Demographic Updates", f"{total_demo:,.0f}", f"{total_demo/total_updates*100:.1f}% of updates")
    kpi_table.add_row("Biometric Updates", f"{total_bio:,.0f}", f"{total_bio/total_updates*100:.1f}% of updates")
    kpi_table.add_row("Update-to-Enrol Ratio", f"[bold yellow]{ratio:.1f}x[/bold yellow]", "⚠️ Based on sample data")
    kpi_table.add_row("Child Attention Gap", f"[bold red]{avg_gap:.3f}[/bold red]", "Negative = under-served")
    kpi_table.add_row("States/UTs Covered", f"{n_states}", "")
    kpi_table.add_row("Districts Covered", f"{n_districts:,}", "")
    
    console.print(kpi_table)
    
    # Top 5 States
    state_summary = df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'child_attention_gap': 'mean'
    }).reset_index().nlargest(10, 'total_enrol')
    
    state_table = Table(title="\n🏆 Top 10 States by Enrolment Volume", box=box.SIMPLE)
    state_table.add_column("Rank", style="dim", width=4)
    state_table.add_column("State", style="cyan")
    state_table.add_column("Enrolments", justify="right")
    state_table.add_column("Updates", justify="right")
    state_table.add_column("Child Gap", justify="right")
    
    for i, (_, row) in enumerate(state_summary.iterrows(), 1):
        gap_color = "red" if row['child_attention_gap'] < 0 else "green"
        state_table.add_row(
            str(i),
            row['state'][:25],
            f"{row['total_enrol']:,.0f}",
            f"{row['total_updates']:,.0f}",
            f"[{gap_color}]{row['child_attention_gap']:+.3f}[/{gap_color}]"
        )
    
    console.print(state_table)
    
    # Worst Child Gaps
    worst_gaps = df.groupby(['state', 'district']).agg({
        'child_attention_gap': 'mean',
        'total_enrol': 'sum'
    }).reset_index().nsmallest(5, 'child_attention_gap')
    
    alert_table = Table(title="\n🚨 Top 5 Districts Needing Intervention", box=box.HEAVY_EDGE, border_style="red")
    alert_table.add_column("District", style="bold red")
    alert_table.add_column("State")
    alert_table.add_column("Child Gap", justify="right", style="red")
    
    for _, row in worst_gaps.iterrows():
        alert_table.add_row(
            row['district'][:20],
            row['state'][:15],
            f"{row['child_attention_gap']:.3f}"
        )
    
    console.print(alert_table)
    
    console.print("\n[dim]Run 'python uidai.py --help' for more commands[/dim]")


@app.command()
def analyze(
    state: str = typer.Option(None, "--state", "-s", help="Filter by state name"),
    district: str = typer.Option(None, "--district", "-d", help="Filter by district name"),
    top: int = typer.Option(20, "--top", "-n", help="Number of results to show")
):
    """🔍 Analyze specific state or district data."""
    
    df = load_data()
    
    if state:
        # Filter by state (case-insensitive partial match)
        mask = df['state'].str.lower().str.contains(state.lower())
        df_filtered = df[mask]
        
        if len(df_filtered) == 0:
            console.print(f"[red]No data found for state: {state}[/red]")
            raise typer.Exit(1)
        
        state_name = df_filtered['state'].iloc[0]
        
        console.print(Panel.fit(
            f"[bold cyan]State Analysis: {state_name}[/bold cyan]",
            border_style="cyan"
        ))
        
        # State-level stats
        total_enrol = df_filtered['total_enrol'].sum()
        total_updates = df_filtered['total_updates'].sum()
        n_districts = df_filtered['district'].nunique()
        avg_gap = df_filtered['child_attention_gap'].mean()
        
        stats_table = Table(box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green", justify="right")
        
        stats_table.add_row("Total Enrolments", f"{total_enrol:,.0f}")
        stats_table.add_row("Total Updates", f"{total_updates:,.0f}")
        stats_table.add_row("Districts", f"{n_districts}")
        gap_color = "red" if avg_gap < 0 else "green"
        stats_table.add_row("Avg Child Gap", f"[{gap_color}]{avg_gap:+.3f}[/{gap_color}]")
        
        console.print(stats_table)
        
        # District breakdown
        district_summary = df_filtered.groupby('district').agg({
            'total_enrol': 'sum',
            'total_updates': 'sum',
            'child_attention_gap': 'mean'
        }).reset_index().sort_values('child_attention_gap')
        
        dist_table = Table(title=f"\n📍 Districts in {state_name} (sorted by Child Gap)", box=box.SIMPLE)
        dist_table.add_column("District", style="cyan")
        dist_table.add_column("Enrolments", justify="right")
        dist_table.add_column("Updates", justify="right")
        dist_table.add_column("Child Gap", justify="right")
        dist_table.add_column("Status")
        
        for _, row in district_summary.head(top).iterrows():
            gap = row['child_attention_gap']
            if gap < -0.5:
                status = "[red]🔴 Critical[/red]"
            elif gap < -0.3:
                status = "[yellow]🟠 Severe[/yellow]"
            elif gap < -0.1:
                status = "[yellow]🟡 Moderate[/yellow]"
            else:
                status = "[green]🟢 Good[/green]"
            
            gap_color = "red" if gap < 0 else "green"
            dist_table.add_row(
                row['district'][:25],
                f"{row['total_enrol']:,.0f}",
                f"{row['total_updates']:,.0f}",
                f"[{gap_color}]{gap:+.3f}[/{gap_color}]",
                status
            )
        
        console.print(dist_table)
    
    else:
        # Show all states summary
        console.print(Panel.fit("[bold]All States Summary[/bold]", border_style="cyan"))
        
        state_summary = df.groupby('state').agg({
            'total_enrol': 'sum',
            'total_updates': 'sum',
            'child_attention_gap': 'mean',
            'district': 'nunique'
        }).reset_index().sort_values('total_enrol', ascending=False)
        
        table = Table(title="States Overview", box=box.ROUNDED)
        table.add_column("State", style="cyan")
        table.add_column("Enrolments", justify="right")
        table.add_column("Updates", justify="right")
        table.add_column("Districts", justify="right")
        table.add_column("Child Gap", justify="right")
        
        for _, row in state_summary.head(top).iterrows():
            gap_color = "red" if row['child_attention_gap'] < 0 else "green"
            table.add_row(
                row['state'][:20],
                f"{row['total_enrol']:,.0f}",
                f"{row['total_updates']:,.0f}",
                str(row['district']),
                f"[{gap_color}]{row['child_attention_gap']:+.3f}[/{gap_color}]"
            )
        
        console.print(table)


@app.command()
def anomalies(
    method: str = typer.Option("isolation", "--method", "-m", help="Detection method: zscore, iqr, isolation"),
    top: int = typer.Option(20, "--top", "-n", help="Number of anomalies to show")
):
    """🤖 Detect anomalous districts using ML-based Isolation Forest."""
    
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    
    console.print(Panel.fit(
        "[bold red]🤖 Anomaly Detection Engine[/bold red]\n"
        f"[dim]Method: {method.upper()}[/dim]",
        border_style="red"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Loading data...", total=100)
        df = load_data()
        progress.update(task, advance=30)
        
        # Aggregate to district level
        district_agg = df.groupby(['state', 'district']).agg({
            'total_enrol': 'sum',
            'total_updates': 'sum',
            'total_demo': 'sum',
            'total_bio': 'sum',
            'child_attention_gap': 'mean',
            'demo_intensity': 'mean',
            'bio_intensity': 'mean'
        }).reset_index()
        progress.update(task, advance=20)
        
        # Compute additional features
        district_agg['demo_bio_ratio'] = district_agg['total_demo'] / (district_agg['total_bio'] + 1)
        district_agg['update_intensity'] = district_agg['total_updates'] / (district_agg['total_enrol'] + 1)
        
        progress.update(task, advance=10, description="Running ML model...")
        
        # Features for anomaly detection
        features = ['total_enrol', 'total_updates', 'demo_bio_ratio', 
                    'update_intensity', 'child_attention_gap']
        
        X = district_agg[features].fillna(0).values
        X = np.log1p(np.abs(X))  # Log transform for stability
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        if method == "isolation":
            # Isolation Forest
            model = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
            district_agg['anomaly_score'] = -model.fit_predict(X_scaled)  # 1 = anomaly
            district_agg['is_anomaly'] = model.fit_predict(X_scaled) == -1
        elif method == "zscore":
            # Z-score method
            from scipy import stats
            z_scores = np.abs(stats.zscore(X_scaled))
            district_agg['anomaly_score'] = z_scores.max(axis=1)
            district_agg['is_anomaly'] = district_agg['anomaly_score'] > 3
        else:  # iqr
            # IQR method
            Q1 = np.percentile(X_scaled, 25, axis=0)
            Q3 = np.percentile(X_scaled, 75, axis=0)
            IQR = Q3 - Q1
            outlier_mask = ((X_scaled < (Q1 - 1.5 * IQR)) | (X_scaled > (Q3 + 1.5 * IQR))).any(axis=1)
            district_agg['anomaly_score'] = outlier_mask.astype(int)
            district_agg['is_anomaly'] = outlier_mask
        
        progress.update(task, advance=40, description="Complete!")
    
    # Results
    anomalies_df = district_agg[district_agg['is_anomaly']].nlargest(top, 'anomaly_score')
    
    n_anomalies = district_agg['is_anomaly'].sum()
    console.print(f"\n[bold]Found {n_anomalies} anomalous districts[/bold] ({n_anomalies/len(district_agg)*100:.1f}% of total)\n")
    
    table = Table(title=f"Top {min(top, len(anomalies_df))} Anomalies", box=box.HEAVY_EDGE, border_style="red")
    table.add_column("District", style="red")
    table.add_column("State")
    table.add_column("Enrolments", justify="right")
    table.add_column("Updates", justify="right")
    table.add_column("D:B Ratio", justify="right")
    table.add_column("Score", justify="right", style="yellow")
    
    for _, row in anomalies_df.iterrows():
        table.add_row(
            row['district'][:20],
            row['state'][:15],
            f"{row['total_enrol']:,.0f}",
            f"{row['total_updates']:,.0f}",
            f"{row['demo_bio_ratio']:.2f}",
            f"{row['anomaly_score']:.2f}"
        )
    
    console.print(table)
    
    # Save anomalies
    output_path = os.path.join(SCRIPT_DIR, "anomalies_detected.csv")
    anomalies_df.to_csv(output_path, index=False)
    console.print(f"\n[dim]Saved to: {output_path}[/dim]")


@app.command()
def forecast():
    """📈 Display 6-month forecasts and declining districts."""
    
    console.print(Panel.fit(
        "[bold green]📈 Predictive Analytics Dashboard[/bold green]\n"
        "[dim]6-Month Prophet ML Forecasts[/dim]",
        border_style="green"
    ))
    
    # Check if forecast data exists
    forecast_dir = os.path.join(SCRIPT_DIR, "forecast_plots")
    declining_file = os.path.join(forecast_dir, "declining_districts.csv")
    
    if os.path.exists(declining_file):
        declining = pd.read_csv(declining_file)
        
        table = Table(title="🚨 Districts with Steepest Decline", box=box.ROUNDED, border_style="yellow")
        table.add_column("District", style="yellow")
        table.add_column("State")
        table.add_column("Monthly Decline", justify="right", style="red")
        table.add_column("Status")
        
        for _, row in declining.head(15).iterrows():
            decline = row.get('relative_slope', row.get('slope', 0))
            if decline < -10:
                status = "[red]🔴 Critical[/red]"
            elif decline < -5:
                status = "[yellow]🟠 Severe[/yellow]"
            else:
                status = "[yellow]🟡 Watch[/yellow]"
            
            table.add_row(
                str(row['district'])[:20],
                str(row['state'])[:15],
                f"{decline:.1f}%",
                status
            )
        
        console.print(table)
    else:
        console.print("[yellow]Run forecast_analysis.py first to generate forecasts.[/yellow]")
    
    # Show forecast images available
    console.print("\n[bold]Available Forecast Visualizations:[/bold]")
    if os.path.exists(forecast_dir):
        for f in os.listdir(forecast_dir):
            if f.endswith('.png'):
                console.print(f"  📊 {f}")


@app.command()
def report(
    state: str = typer.Option(None, "--state", "-s", help="Generate report for specific state"),
    all_states: bool = typer.Option(False, "--all", "-a", help="Generate reports for all states")
):
    """📄 Generate state-level report cards."""
    
    df = load_data()
    output_dir = os.path.join(SCRIPT_DIR, "state_reports")
    os.makedirs(output_dir, exist_ok=True)
    
    if all_states:
        states = df['state'].unique()
    elif state:
        states = [s for s in df['state'].unique() if state.lower() in s.lower()]
        if not states:
            console.print(f"[red]No state found matching: {state}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[yellow]Specify --state or --all[/yellow]")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Generating reports...", total=len(states))
        
        for state_name in states:
            state_df = df[df['state'] == state_name]
            
            # Calculate metrics
            total_enrol = state_df['total_enrol'].sum()
            total_updates = state_df['total_updates'].sum()
            n_districts = state_df['district'].nunique()
            avg_gap = state_df['child_attention_gap'].mean()
            worst_district = state_df.groupby('district')['child_attention_gap'].mean().idxmin()
            worst_gap = state_df.groupby('district')['child_attention_gap'].mean().min()
            
            # Generate markdown report
            report_content = f"""# 📊 State Report Card: {state_name}

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Enrolments | {total_enrol:,.0f} |
| Total Updates | {total_updates:,.0f} |
| Districts | {n_districts} |
| Avg Child Gap | {avg_gap:+.3f} |

## 🚨 Priority District

**{worst_district}** has the worst child attention gap: **{worst_gap:.3f}**

## District Summary

| District | Enrolments | Updates | Child Gap | Status |
|----------|------------|---------|-----------|--------|
"""
            # Add district rows
            district_summary = state_df.groupby('district').agg({
                'total_enrol': 'sum',
                'total_updates': 'sum',
                'child_attention_gap': 'mean'
            }).reset_index().sort_values('child_attention_gap')
            
            for _, row in district_summary.iterrows():
                gap = row['child_attention_gap']
                if gap < -0.5:
                    status = "🔴 Critical"
                elif gap < -0.3:
                    status = "🟠 Severe"
                elif gap < -0.1:
                    status = "🟡 Moderate"
                else:
                    status = "🟢 Good"
                
                report_content += f"| {row['district'][:20]} | {row['total_enrol']:,.0f} | {row['total_updates']:,.0f} | {gap:+.3f} | {status} |\n"
            
            report_content += f"\n---\n*Generated: UIDAI Data Hackathon 2026*\n"
            
            # Save report
            safe_name = state_name.replace(' ', '_').replace('/', '_')
            report_path = os.path.join(output_dir, f"{safe_name}_report.md")
            with open(report_path, 'w') as f:
                f.write(report_content)
            
            progress.update(task, advance=1, description=f"Generated: {state_name[:20]}...")
    
    console.print(f"\n[green]✅ Generated {len(states)} state reports in:[/green]")
    console.print(f"   [cyan]{output_dir}[/cyan]")


@app.command()
def maps():
    """🗺️ Generate interactive HTML maps (opens in browser)."""
    
    console.print(Panel.fit(
        "[bold blue]🗺️ Interactive Map Generator[/bold blue]\n"
        "[dim]Creating Folium HTML maps...[/dim]",
        border_style="blue"
    ))
    
    # Run the map generation
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        console.print("[red]Folium not installed. Run: pip install folium[/red]")
        raise typer.Exit(1)
    
    df = load_data()
    output_dir = os.path.join(SCRIPT_DIR, "interactive_maps")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create state-level summary
    state_summary = df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'child_attention_gap': 'mean'
    }).reset_index()
    
    # State coordinates (approximate centers)
    state_coords = {
        'Andhra Pradesh': [15.9129, 79.7400],
        'Arunachal Pradesh': [28.2180, 94.7278],
        'Assam': [26.2006, 92.9376],
        'Bihar': [25.0961, 85.3131],
        'Chhattisgarh': [21.2787, 81.8661],
        'Delhi': [28.7041, 77.1025],
        'Goa': [15.2993, 74.1240],
        'Gujarat': [22.2587, 71.1924],
        'Haryana': [29.0588, 76.0856],
        'Himachal Pradesh': [31.1048, 77.1734],
        'Jharkhand': [23.6102, 85.2799],
        'Karnataka': [15.3173, 75.7139],
        'Kerala': [10.8505, 76.2711],
        'Madhya Pradesh': [22.9734, 78.6569],
        'Maharashtra': [19.7515, 75.7139],
        'Manipur': [24.6637, 93.9063],
        'Meghalaya': [25.4670, 91.3662],
        'Mizoram': [23.1645, 92.9376],
        'Nagaland': [26.1584, 94.5624],
        'Odisha': [20.9517, 85.0985],
        'Punjab': [31.1471, 75.3412],
        'Rajasthan': [27.0238, 74.2179],
        'Sikkim': [27.5330, 88.5122],
        'Tamil Nadu': [11.1271, 78.6569],
        'Telangana': [18.1124, 79.0193],
        'Tripura': [23.9408, 91.9882],
        'Uttar Pradesh': [26.8467, 80.9462],
        'Uttarakhand': [30.0668, 79.0193],
        'West Bengal': [22.9868, 87.8550],
    }
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Creating map...", total=None)
        
        # Create base map centered on India
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='cartodbpositron')
        
        # Add markers for each state
        for _, row in state_summary.iterrows():
            state = row['state']
            
            # Find coordinates
            coords = None
            for key, val in state_coords.items():
                if key.lower() in state.lower() or state.lower() in key.lower():
                    coords = val
                    break
            
            if coords is None:
                continue
            
            # Color based on child gap
            gap = row['child_attention_gap']
            if gap < -0.5:
                color = 'red'
            elif gap < -0.2:
                color = 'orange'
            elif gap < 0:
                color = 'yellow'
            else:
                color = 'green'
            
            # Popup content
            popup_html = f"""
            <div style="width:200px">
                <h4>{state}</h4>
                <b>Enrolments:</b> {row['total_enrol']:,.0f}<br>
                <b>Updates:</b> {row['total_updates']:,.0f}<br>
                <b>Child Gap:</b> <span style="color:{color}">{gap:+.3f}</span>
            </div>
            """
            
            # Add circle marker
            folium.CircleMarker(
                location=coords,
                radius=max(5, min(30, np.log1p(row['total_enrol']) * 2)),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)
        
        # Add legend
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                    background-color: white; padding: 10px; border-radius: 5px;
                    border: 2px solid grey;">
            <b>Child Attention Gap</b><br>
            <span style="color:red">●</span> Critical (&lt; -0.5)<br>
            <span style="color:orange">●</span> Severe (-0.5 to -0.2)<br>
            <span style="color:yellow">●</span> Moderate (-0.2 to 0)<br>
            <span style="color:green">●</span> Good (&gt; 0)
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        map_path = os.path.join(output_dir, "india_child_gap_map.html")
        m.save(map_path)
    
    console.print(f"\n[green]✅ Interactive map created![/green]")
    console.print(f"   [cyan]{map_path}[/cyan]")
    console.print("\n[dim]Open in browser to explore interactively[/dim]")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    app()
