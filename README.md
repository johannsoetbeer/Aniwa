# Aniwa

<p align="left">
  <img
    src="https://raw.githubusercontent.com/ReginaldErzoah/Aniwa/main/assets/aniwa-logo.png"
    width="220"
    alt="Aniwa Logo"
  >
</p>

> **See your data clearly.**

Aniwa is an open-source universal dataset profiling and intelligence tool designed for developers, analysts, data engineers, researchers, and modern data teams.

Aniwa helps you instantly understand datasets through:
- schema profiling
- data quality analysis
- statistical summaries
- intelligent insights
- rich terminal reports
- shareable HTML reports

Whether you're working with CSV files, Excel spreadsheets, JSON datasets, or Parquet files, Aniwa gives you a fast and elegant way to inspect and understand data.

---

# Why Aniwa?

Data professionals constantly work with unknown datasets.

Before trusting a dataset, people need to know:

- What columns exist?
- What data types are present?
- Are there missing values?
- Are there duplicates?
- Are there suspicious patterns?
- Which columns might contain IDs or PII?
- Is the dataset healthy?

Aniwa makes answering those questions simple.

---

# Quick Installation

Install Aniwa from PyPI:

```bash
pip install aniwa
````

Verify installation:

```bash
aniwa --help
```

Upgrade Aniwa:

```bash
pip install --upgrade aniwa
```

---

# Quick Start

Profile a dataset:

```bash
aniwa customers.csv
```

Generate a JSON report:

```bash
aniwa customers.csv --report json --output profile.json
```

Generate an HTML report:

```bash
aniwa customers.csv --report html --output profile.html
```

Run lightweight profiling:

```bash
aniwa customers.csv --mode fast
```

Run full profiling:

```bash
aniwa customers.csv --mode deep
```

---

# Supported Formats

Aniwa currently supports:

* CSV
* Excel (.xlsx)
* JSON
* Parquet


---

# Features

## Universal Dataset Support

Aniwa supports multiple modern dataset formats:

- CSV
- Excel
- JSON
- Parquet

Future releases will include:
- PostgreSQL
- MySQL
- DuckDB
- BigQuery
- Snowflake

---

## Core Profiling

Aniwa provides:

### Dataset Summary
- row counts
- column counts
- dataset size analysis

### Schema Profiling
- type inference
- mixed type detection
- schema overview

### Data Quality Analysis
- null analysis
- duplicate detection
- uniqueness analysis
- sparse column detection

### Statistical Profiling
- minimum values
- maximum values
- mean
- median
- standard deviation

### Intelligent Insights
- possible ID detection
- high-cardinality warnings
- sparse column warnings
- suspicious quality patterns

---

## Reporting

### Rich Terminal Reports

Aniwa uses Rich-powered terminal interfaces for beautiful developer-friendly output.

### JSON Export

Machine-readable profiling results.

### HTML Reports

Generate shareable profiling reports for teams, audits, and debugging workflows.

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/ReginaldErzoah/Aniwa.git
cd Aniwa
```

---

## Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment:

### Windows

```bash
source .venv/Scripts/activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Install Aniwa locally:

```bash
pip install -e .
```

---

# Usage

## Basic Profiling

```bash
aniwa examples/customers.csv
```

---

## Generate JSON Report

```bash
aniwa examples/customers.csv --report json --output profile.json
```

---

## Generate HTML Report

```bash
aniwa examples/customers.csv --report html --output profile.html
```

---

## Fast Profiling Mode

```bash
aniwa examples/customers.csv --mode fast
```

---

## Deep Profiling Mode

```bash
aniwa examples/customers.csv --mode deep
```

---

# Example Console Output

```text
┌──────────────────────────────┐
│      Aniwa Dataset Profile   │
├──────────────────────────────┤
│ Rows: 5                      │
│ Columns: 5                   │
│ Duplicate Rows: 1            │
└──────────────────────────────┘
```

---

# Project Structure

```text
Aniwa/
│
├── aniwa/
│   ├── cli.py
│   ├── core/
│   ├── io/
│   ├── models/
│   ├── reports/
│   └── utils/
│
├── tests/
├── examples/
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
└── pyproject.toml
```

---

# Roadmap

## v0.1.1 - MVP Foundation

### Core Features
[x] CSV support
[x] Excel support
[x] JSON support
[x] Parquet support
[x] schema profiling
[x] null analysis
[x] duplicate detection
[x] statistical profiling
[x] console reports
[x] JSON export
[x] HTML reports

### Developer Experience
[x] Rich terminal UI
[x] fast and deep modes
[x] profiling insights

---

## v0.1.2 - More Outputs & File Supports

- Markdown report
- CSV summary report
- PDF report
- Excel report
- charts in HTML
- report templates
- custom report sections


---

## v0.2.0 - Intelligence Release

- correlation analysis
- outlier detection
- semantic detection
- improved insights
- Markdown reports

---

## v0.3.0 - Universal Connectivity

- PostgreSQL support
- MySQL support
- DuckDB support
- BigQuery support
- profiling history
- snapshot management

---

## v0.4.0 - Extensibility

- plugin system
- custom profiling modules
- community extensions

---

## v0.5.0 - AI Intelligence

- dataset summarization
- semantic understanding
- AI-powered recommendations
- anomaly explanations

---

# Philosophy

Aniwa is built around a few core principles:

- universal
- developer-first
- fast
- modular
- intelligent
- beautiful
- automation-friendly

---


# Contributing

Contributions are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- development setup
- contribution guidelines
- pull request workflow
- testing instructions

---

# License

Aniwa is released under the MIT License.

See [LICENSE](LICENSE) for details.
