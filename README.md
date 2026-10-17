# MudFlow OS v2.5: Drilling Mud Engineering & Wellbore Hydraulics Suite

[![Version](https://img.shields.io/badge/MudFlow%20OS-v2.5.0--PROD-0ea5e9.svg)](https://github.com/mudflow-os/drilling-suite)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-38bdf8.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-059669.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Production%20Ready-2563eb.svg)](https://www.docker.com/)
[![Standard](https://img.shields.io/badge/API%20Standards-RP%2013D%20%7C%2013C%20%7C%2016D-f59e0b.svg)](https://www.api.org/)

**MudFlow OS v2.5** is an enterprise-grade, full-stack drilling fluid engineering, wellbore hydraulics, solids management, and well control operations platform. Engineered specifically for mud engineers, operations drilling engineers, rig supervisors, and superintendents operating on land rigs and offshore floating installations.

---

## 🚀 Architectural Overview

MudFlow OS follows a high-throughput, decoupled, micro-service ready architecture built for zero-downtime rig telemetry and local field autonomy:

- **Backend**: **Python FastAPI** asynchronous application layer with **Pydantic v2** strict data validation and **SQLAlchemy 2.0** ORM over an embedded **SQLite** operational database.
- **Frontend**: High-contrast, industrial dark-mode Single Page Application (SPA) styled with **Tailwind CSS**, vanilla JavaScript, and interactive **Chart.js** telemetry visualizers.
- **AI Mud Doctor Engine**: Real-time heuristic diagnostic expert system evaluating rheological balance, LGS build-up, and chemical treatment requirements.
- **Well Control Kill Sheet Engine**: API RP 59 / 16D standard well control solver computing Kill Mud Weight (KWM), Initial Circulating Pressure (ICP), and Final Circulating Pressure (FCP).
- **Engineering Standards Compliance**:
  - **API Recommended Practice 13D**: Rheology, Yield-Power Law (Herschel-Bulkley), and Hydraulics modeling.
  - **API Recommended Practice 13C**: Drilling Fluid Processing Systems Evaluation (Solids Control & Retort Mass Balance).
  - **API Recommended Practice 13B**: Field Testing of Drilling Fluids (Water-Based and Oil-Based).
  - **API Recommended Practice 16D / 59**: Well Control Operations & Influx Circulation.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         MUDFLOW OS v2.5 CLIENT UI                        │
│   (Industrial Dark-Mode Dashboard • Tailwind CSS • Chart.js Telemetry)   │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ HTTP / REST JSON
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI APPLICATION LAYER                       │
│    FastAPI Routers • CORS Middleware • Pydantic v2 Request Validation    │
├───────────────────┬───────────────────┬──────────────────┬───────────────┤
│ Viscometer & Rheo │ Hydraulics & ECD  │ Volumetrics & WU │ Retort Solids │
│   RP 13D Engine   │ Nozzles & Regime  │ Pits & Dilution  │ Mass Balance  │
├───────────────────┴───────────────────┴──────────────────┴───────────────┤
│              AI Mud Doctor Diagnostic Engine (/api/ai-mud-doctor)        │
│          Well Control Kill Sheet Solver (/api/well-control/kill-sheet)   │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ SQLAlchemy ORM
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   PERSISTENT RIG DATA STORAGE & EXPORT                   │
│         SQLite Embedded Database (mudflow.db) • ReportLab PDF            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Project Layout

```text
mudflow-os/
│
├── Dockerfile                    # Multi-stage production container image (Python 3.10-slim)
├── docker-compose.yml            # Local development orchestration with volume sync & live reload
├── requirements.txt              # Production locked dependency manifest
├── run.py                        # Standalone local launcher script
├── test_backend.py               # Automated verification test suite
│
├── app/
│   ├── config.py                 # Paths, database URI, and v2.5 system constants
│   ├── database.py               # SQLAlchemy database session maker and declarative Base
│   ├── main.py                   # FastAPI initialization, static mounts, Mud Doctor & Kill Sheet APIs
│   ├── seed_data.py              # North Sea / Permian Basin well datasets & initial historical logs
│   │
│   ├── models/                   # SQLAlchemy ORM Models
│   │   ├── well.py               # Well, Rig, Field, Operator metadata schema
│   │   └── report.py             # DailyMudReport entity with rheology, hydraulics, and retort fields
│   │
│   ├── schemas/                  # Pydantic v2 Request & Response Data Contracts
│   │   ├── rheology.py           # Viscometer readings, flow indices, curve coordinates
│   │   ├── hydraulics.py         # Bit nozzles, annular velocities, pressure profile points
│   │   ├── volumetrics.py        # System capacities, Barite/Hematite weight up, base dilution
│   │   ├── solids.py             # Retort phase balance, ASG, %HGS, %LGS, active clay
│   │   └── report.py             # Daily mud report CRUD contracts
│   │
│   ├── services/                 # Pure Engineering Calculation Engines
│   │   ├── rheology_engine.py    # Bingham Plastic, Power Law, Herschel-Bulkley, Gels
│   │   ├── hydraulics_engine.py  # Hydrostatic, ECD, Bit TFA/HHP/HSI, Flow Regime
│   │   ├── volumetrics_engine.py # String/annulus capacities, Barite sacks, dilution volumes
│   │   ├── solids_engine.py      # Retort mass balance, ASG, active smectite clay
│   │   └── pdf_generator.py      # Publication-grade Daily Mud Report PDF builder
│   │
│   ├── routers/                  # Modular REST API Endpoints
│   │   ├── rheology.py           # /api/rheology/calculate & /defaults
│   │   ├── hydraulics.py         # /api/hydraulics/calculate & /pressure-profile
│   │   ├── volumetrics.py        # /api/volumetrics/hole-volumes, /weight-up, /dilution
│   │   ├── solids.py             # /api/solids/analyze
│   │   └── reports.py            # /api/wells & /api/reports (CRUD & PDF stream)
│   │
│   └── templates/                # Server-rendered / static template storage
│       └── index.html            # Synchronized dark-mode single-page application
│
├── static/                       # Field-Ready Industrial Single Page Application Assets
│   ├── index.html                # Telemetry dashboard, interactive calculators, slide-out drawer & modals
│   ├── css/
│   │   └── style.css             # Industrial high-contrast rig theme & telemetry indicators
│   └── js/
│       ├── app.js                # Global state manager, active well routing, Mud Doctor & Kill Sheet
│       ├── rheology.js           # Rheology engine bindings & Chart.js shear curve
│       ├── hydraulics.js         # Hydraulics solver, nozzle matrix & depth pressure profile
│       ├── volumetrics.js        # Pit volumes, weight-up slider & dilution calculator
│       ├── solids.js             # Retort phase doughnut chart & solids diagnostics
│       └── reports.js            # Historical mud report table, detail modal & PDF download
│
└── data/                         # SQLite database storage (mudflow.db) & generated PDF reports
```

---

## 🛠️ Core Functional Modules

### 1. Viscometer & Rheology Engine (API RP 13D)
- **Fann 35 Dial Readings ($\theta$)**: 600, 300, 200, 100, 6, 3 RPM with 10-sec, 10-min, and 30-min gel strengths.
- **Key Parameters Calculated**:
  - Plastic Viscosity: $PV = \theta_{600} - \theta_{300}$ (cP)
  - Yield Point: $YP = 2\theta_{300} - \theta_{600}$ ($\text{lb}/100\text{ ft}^2$)
  - Apparent Viscosity: $AV = \theta_{600} / 2$ (cP)
  - $YP/PV$ ratio diagnostic for hole cleaning vs. surge pressure optimization.
- **Mathematical Flow Models**:
  - **Bingham Plastic**: $\tau = PV \cdot \gamma + YP$
  - **Power Law (Ostwald-de Waele)**: Flow behavior index ($n$) and consistency index ($K$).
  - **Herschel-Bulkley (Yield Power Law, API RP 13D)**: Yield stress $\tau_0$, $n_{hb}$, and $K_{hb}$ fitted with $R^2$ goodness-of-fit indicator.
  - **Gel Profile Diagnostics**: Classifies gel behavior as *Flat / Stable*, *Progressive (Swab / Surge Risk)*, or *Fragile*.
- **Interactive Visualization**: Dynamic Chart.js curve plotting experimental dial points against Bingham, Power Law, and Herschel-Bulkley fits across shear rates up to $1021.4\text{ s}^{-1}$.

### 2. Hydraulics & Wellbore Pressure Profile Engine
- **Input Parameters**: Mud Weight ($MW$), True Vertical Depth ($TVD$), Measured Depth ($MD$), Flow Rate ($Q$), Hole ID, Drill Pipe OD, Drill Collar OD, Bit Nozzle Matrix, Pump Pressure, and Annular Pressure Loss.
- **Hydraulics Outputs**:
  - Hydrostatic Pressure: $P_{\text{hyd}} = 0.052 \times MW \times TVD$ (psi)
  - Equivalent Circulating Density: $ECD = MW + \frac{\Delta P_{\text{ann}}}{0.052 \times TVD}$ (ppg)
  - Annular Velocities ($AV_{\text{dp}}$ and $AV_{\text{dc}}$ in $\text{ft/min}$)
  - Total Flow Area: $TFA = \frac{\sum N_i^2}{1303.8}$ ($\text{in}^2$)
  - Jet Nozzle Velocity: $V_n = \frac{Q}{3.117 \times TFA}$ ($\text{ft/s}$)
  - Bit Pressure Drop: $\Delta P_b = \frac{MW \times Q^2}{10858 \times TFA^2}$ (psi)
  - Bit Hydraulic Horsepower: $HHP = \frac{\Delta P_b \times Q}{1714}$
  - Horsepower per Square Inch: $HSI = \frac{HHP}{\frac{\pi}{4} \times \text{BitSize}^2}$
  - Jet Impact Force: $IF = \frac{MW \times Q \times V_n}{1930}$ (lbf)
  - Annular Flow Regime classification (*Laminar*, *Transitional*, *Turbulent*) based on Reynolds number.
- **Depth Pressure Profile**: Interactive chart plotting hydrostatic vs. circulating pressure profile from surface ($0\text{ ft}$) to TD ($TVD$).

### 3. Pit Volume & Weight-Up / Dilution Manager
- **System Capacity Accounting**:
  - Drill pipe and drill collar internal capacities, annular volumes, active pits, reserve pits, trip tank, and total circulating volume.
- **Weight-Up Engine**:
  - Toggle between **Barite** ($SG = 4.20$, density $35.0\text{ ppg}$) and **Hematite** ($SG = 5.00$, density $41.7\text{ ppg}$).
  - Sacks per 100 bbl formula:
    $$\text{Sacks/100 bbl} = \frac{1470 \times (MW_2 - MW_1)}{35.0 - MW_2} \quad \text{(Barite)}$$
    $$\text{Sacks/100 bbl} = \frac{1751 \times (MW_2 - MW_1)}{41.7 - MW_2} \quad \text{(Hematite)}$$
  - Outputs total 100-lb sacks, metric tonnage, slurry volume expansion, and estimated material cost.
- **Base Fluid Dilution Engine**:
  - Computes required volume of synthetic base oil, diesel, fresh water, or seawater to cut mud weight or reduce Low Gravity Solids (LGS).
  - Computes additional Barite sacks required to restore target density after LGS dilution.

### 4. Retort & Solids Control Analysis (API RP 13C)
- **Phase Balance**: % Water, % Oil, and % Total Solids volume partitioning.
- **Solids Diagnostic Metrics**:
  - Oil-to-Water Ratio ($OWR$)
  - Average Specific Gravity of Solids ($ASG$)
  - High Gravity Solids (% HGS and ppb)
  - Low Gravity Solids (% LGS and ppb)
  - Active Smectite Clay concentration from Methylene Blue Test (% vol and ppb)
  - Inactive Drill Solids (% vol) and Active Clay Ratio ($MBT / LGS$)
  - Solids control equipment efficiency recommendations and doughnut phase distribution chart.

### 5. AI Mud Doctor Engine (`/api/ai-mud-doctor`)
- **Automated Expert Diagnostic Advisor**:
  - Analyzes current fluid parameters: Plastic Viscosity ($PV$), Yield Point ($YP$), Mud Weight ($MW$), and Low Gravity Solids ($LGS\%$).
  - Checks critical drilling fluid danger zones:
    - $LGS\% > 5.5\%$ (elevated solids, filter cake thickening, differential sticking risk) and $> 7.0\%$ (critical contamination).
    - $PV > 30\text{ cP}$ (high mechanical friction) and $> 35\text{ cP}$ (severe ECD surge risk).
    - Low $YP/PV < 0.50$ (poor cuttings transport and barite sag risk) or high $YP/PV > 1.30$ (chemical flocculation).
  - Determines overall health urgency status: `OPTIMAL`, `WARNING`, or `CRITICAL`.
  - Delivers prioritized, actionable chemical treatment and solids equipment advice via an industrial slide-out drawer UI.

### 6. Well Control Kill Sheet Engine (`/api/well-control/kill-sheet`)
- **Standard Well Control Solver (API RP 59 / 16D)**:
  - Computes:
    $$\text{Kill Mud Weight (KWM)} = \text{Current } MW + \frac{\text{SIDPP}}{0.052 \times TVD}$$
    $$\text{Initial Circulating Pressure (ICP)} = \text{Slow Pump Press} + \text{SIDPP}$$
    $$\text{Final Circulating Pressure (FCP)} = \text{Slow Pump Press} \times \frac{\text{KWM}}{\text{Current } MW}$$
  - Computes Kick Intensity ($\Delta \text{ppg}$) and Initial Formation Bottomhole Pressure (BHP in psi).
  - Dynamically renders results in high-visibility alert cards on the Well Control Modal and provides a complete 7-step operating instruction checklist for Driller's Method / Wait & Weight procedures.

### 7. Historical Reports & Database
- SQLite database persistence for wells, rigs, operators, and daily mud logs.
- Automated autofill from active calculations directly into Daily Mud Reports.
- Streaming PDF export for Daily Mud Reports formatted to operator standards.

---

## 🌐 API Reference Matrix

| HTTP Method | Route | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status, version, and engine state |
| `POST` | `/api/ai-mud-doctor` | Diagnostic expert analysis on $PV$, $YP$, $MW$, and $LGS\%$ |
| `POST` | `/api/well-control/kill-sheet` | Solves KWM, ICP, FCP, kick intensity, and instructions |
| `POST` | `/api/rheology/calculate` | Computes Bingham, Power Law, Herschel-Bulkley parameters & curve points |
| `GET` | `/api/rheology/defaults` | Baseline field presets (OBM, WBM, HPHT) |
| `POST` | `/api/hydraulics/calculate` | Solves hydrostatic, ECD, nozzle TFA, velocity, HHP, HSI, and regime |
| `POST` | `/api/hydraulics/pressure-profile` | Generates TVD depth profile comparing Hydrostatic vs. ECD |
| `POST` | `/api/volumetrics/hole-volumes` | Computes pipe, collar, annular, pit, and total system volumes |
| `POST` | `/api/volumetrics/weight-up` | Computes Barite/Hematite sacks, tonnage, and volume expansion |
| `POST` | `/api/volumetrics/dilution` | Computes base fluid dilution for mud weight or LGS reduction |
| `POST` | `/api/solids/analyze` | Retort phase balance, ASG, %HGS, %LGS, active clay, and efficiency |
| `GET` | `/api/wells` | Lists all active drilling wells |
| `POST` | `/api/wells` | Creates a new well context |
| `GET` | `/api/reports?well_id={id}` | Retrieves daily mud reports for a target well |
| `POST` | `/api/reports` | Saves a new daily mud report |
| `GET` | `/api/reports/{id}/pdf` | Downloads formatted Daily Mud Report PDF |

---

## 🚀 Deployment Instructions

### Option A: Local Deployment (Python Virtual Environment)

#### 1. System Requirements
- Python 3.10 or 3.11
- Recommended: Virtual environment manager (`venv` or `uv`)

#### 2. Setup Virtual Environment
```bash
# Navigate to project root
cd mudflow-os

# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate
```

#### 3. Install Locked Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run Automated Backend Test Suite
```bash
python test_backend.py
```
Expected output:
```text
1. Creating database tables...
2. Seeding database...
-> Wells in DB: 3, Reports in DB: 4
3. Testing Rheology Engine...
-> PV: 23.0 cP, YP: 19.0 lb/100ft2, AV: 32.5 cP, n: 0.63, K: 0.8802, Tau0: 3.2
4. Testing Hydraulics Engine...
-> Hydrostatic: 6500.0 psi, ECD: 12.79 ppg, TFA: 0.451 sq in, HHP: 412.8 hp, Flow: Laminar Flow
5. Testing PDF Generator...
-> Generated Daily Mud Report PDF: 6581 bytes!
6. Testing AI Mud Doctor Engine...
-> AI Mud Doctor Urgency: WARNING, Recs: 3, Ratio: 0.5
7. Testing Well Control Kill Sheet Engine...
-> KWM: 12.96 ppg, ICP: 1300.0 psi, FCP: 864.1 psi
BACKEND VERIFICATION COMPLETE: ALL SYSTEMS NOMINAL!
```

#### 5. Launch Application Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 9001 --reload
```
Navigate to:
- **Application Dashboard**: [http://localhost:9001](http://localhost:9001)
- **Interactive OpenAPI Documentation**: [http://localhost:9001/docs](http://localhost:9001/docs)

---

### Option B: Production Docker Deployment

#### 1. Build the Docker Image
```bash
docker build -t mudflow-os:v2.5 .
```

#### 2. Run the Container
```bash
docker run -d \
  --name mudflow_os_app \
  -p 9001:9001 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  mudflow-os:v2.5
```

#### 3. Verify Container Health
```bash
curl -s http://localhost:9001/api/health
```
Response:
```json
{
  "status": "healthy",
  "app": "MudFlow OS - Drilling Mud Engineering & Hydraulics Suite",
  "version": "2.5.0-PROD",
  "engine": "active"
}
```

---

### Option C: Docker Compose (Local Persistence & Live Reloading)

`docker-compose.yml` mounts the application code for live reloading while mounting `./data` to preserve the SQLite database and generated PDF reports.

#### 1. Start Service with Docker Compose
```bash
docker compose up -d --build
```

#### 2. View Live Logs
```bash
docker compose logs -f mudflow-os
```

#### 3. Stop the Service
```bash
docker compose down
```

---

## 🔒 Security & Data Integrity
- **Embedded SQLite Persistence**: Database state is stored in `data/mudflow.db`, allowing simple volume backup and container migrations.
- **Input Validation**: All numerical calculations enforce strict physical limits via Pydantic schema validation ($TVD > 0$, $MW > 0$, $Q > 0$).
- **Zero Cloud Dependence**: Designed to operate fully offline on rig networks without external telemetry dependencies.

---

## 📄 License & Attribution
MudFlow OS is developed for drilling and fluids engineering operations. Formulated according to American Petroleum Institute (API) Recommended Practices 13D, 13C, 13B, and 16D.
