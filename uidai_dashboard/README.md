# 🖥️ UIDAI Dashboard

## Professional Django Dashboard for the UIDAI Data Hackathon 2026

A beautiful, interactive dashboard that showcases all analysis insights from the Aadhaar enrolment and updates data.

---

## ✨ Features

- **📊 KPI Cards**: Total enrolments, updates, ratios at a glance
- **📈 Interactive Charts**: Chart.js visualizations with real data
- **🗺️ State Analysis**: Drill-down into state-level metrics
- **🧩 Cluster Views**: District behavioral segmentation
- **💡 Insights Page**: Key findings and recommendations
- **📱 Responsive**: Works on desktop and mobile
- **🎨 Professional UI**: Bootstrap 5 + custom styling

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd uidai_dashboard
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python manage.py runserver
```

### 3. Open in Browser

Navigate to: **http://127.0.0.1:8000/**

---

## 📁 Project Structure

```
uidai_dashboard/
├── manage.py                    # Django entry point
├── requirements.txt             # Python dependencies
├── uidai/                       # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── reports/                     # Main dashboard app
    ├── views.py                 # Data loading & rendering
    ├── urls.py                  # URL routes
    └── templates/reports/
        ├── base.html            # Base template with sidebar
        ├── dashboard.html       # Main dashboard
        ├── state_detail.html    # State drill-down
        ├── clusters.html        # Cluster analysis
        └── insights.html        # Key insights
```

---

## 🔌 Data Integration

The dashboard automatically loads data from the parent directory's analysis outputs:

- `integrated_analysis/integrated_data.csv`
- `integrated_analysis/state_summary.csv`
- `integrated_analysis/kpis.csv`
- `biometric_analysis/district_clusters.csv`
- `demographic_analysis/district_clusters.csv`
- `enrolment_analysis/district_clusters.csv`

### Replacing with Your Data

Edit `reports/views.py` to point to your data files:

```python
DATA_DIR = Path('/path/to/your/data')
```

---

## 📸 Screenshots

### Dashboard
- 7 KPI metric cards
- National trend line chart
- Child attention gap bar chart
- State comparison chart
- Key insights section

### Clusters Page
- Biometric clusters table
- Demographic clusters table
- Enrolment clusters table

### Insights Page
- Highlight metrics
- Actionable recommendations
- Priority-based action items

---

## 🌐 Deployment

### PythonAnywhere

1. Upload the project
2. Create a web app with Django
3. Configure WSGI path
4. Set `DEBUG = False` in settings

### Render

1. Push to GitHub
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn uidai.wsgi:application`

---

## 📄 License

MIT License - UIDAI Data Hackathon 2026
