# 🎧 Spotify ELT Data Pipeline — GCP + Snowflake + dbt + Streamlit

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Built with](https://img.shields.io/badge/Built%20with-GCP%20%2B%20Snowflake-blue)
![Data Engineering](https://img.shields.io/badge/domain-Data%20Engineering-orange.svg)

---

## 📖 Overview

> **Architecture Note**  
> This project follows a **hybrid medallion architecture** where **Snowflake is the primary data warehouse**, responsible for storing and processing all curated layers — Bronze, Silver, and Gold.  
>
> The flow operates as follows:
> - Raw JSON data lands first in **Google Cloud Storage (GCS)** as Bronze snapshots.
> - Snowflake ingests these Bronze files and **materializes an incremental Bronze table**.
> - dbt transforms Bronze → Silver → Gold **inside Snowflake**, where all curated data is stored and queried.
> - Silver & Gold are also **exported to GCS (Parquet)** only as *resilient backups* and for future portability (BigQuery, DuckDB, Databricks, Polars, etc.).
>
> This ensures:
> - **Full analytical power and long-term storage in Snowflake**  
> - **Durable, portable backups in GCS**  
> - A decoupled architecture where Snowflake is the warehouse and transformation engine, while GCS provides raw ingestion and long-term durability.

This project implements a modern ELT pipeline that extracts daily artist insights
from the Spotify API, stores raw JSON in GCS, transforms data in Snowflake using dbt,
and exposes curated analytical insights through an interactive Streamlit application
that queries Gold-layer datasets directly from Snowflake.

The pipeline includes:

- serverless ingestion (Cloud Run Jobs)
- CI/CD orchestration (GitHub Actions)
- ELT modeling with dbt (Bronze → Silver → Gold)
- analytics stored and computed in Snowflake
- visualization via Streamlit

---

## 🎄 Dataset Scope

This project tracks **Christmas-related Spotify artists and their top tracks** during the **2025 holiday season**, focusing on the period from **November to December 2025**.

The dataset includes:

- A curated list of **globally and Brazil-relevant Christmas artists**
- Daily snapshots of:
  - artist popularity and follower counts
  - top tracks per artist
  - track popularity evolution over time
- Historical tracking to capture **seasonality and popularity spikes** as Christmas approaches

The goal is to analyze how Christmas music consumption evolves over time, compare markets (Global vs Brazil), and identify the most dominant artists and tracks during the holiday season.

## ⚙️ Tech Stack

### Ingestion & Orchestration
* **GitHub Actions** – scheduled automation + CI/CD  
* **Cloud Run Jobs** – serverless batch ingestion  

### Storage & Warehouse
* **Google Cloud Storage (GCS)**  
  - Raw Bronze snapshots (JSON)  
  - Backups of Snowflake Silver & Gold (Parquet)  
* **Snowflake**  
  - **Primary data warehouse**
  - Hosts Bronze, Silver, Gold tables  
  - dbt models run directly on Snowflake compute  

### Transformation
* **dbt Core** — SQL models, lineage, tests, documentation  

### Visualization
* **Streamlit** — dashboard powered by Snowflake queries  
## 📊 Streamlit Analytics Application

This project includes an interactive Streamlit application that consumes curated
Gold tables directly from Snowflake.

The dashboard focuses on analytical storytelling rather than raw visualization,
highlighting:
- peak popularity vs popularity growth
- market-specific rankings (ALL, BR, GB)
- temporal evolution of track popularity
- artist-level performance comparison

All rankings are recomputed dynamically based on the selected market, ensuring
accurate analytical behavior rather than post-filtered results.

## 🧩 Streamlit Development Workflow

The Streamlit application is developed and versioned locally using GitHub, allowing
a clean development experience with full IDE support.

The app connects directly to Snowflake using the Python connector to query Gold-layer
tables. The same application logic is compatible with Snowflake-native Streamlit
deployments (via Snowpark sessions), enabling flexible execution without code changes.

This approach separates development from execution concerns while keeping Snowflake
as the single source of truth for analytics.

### Data Source
* **Spotify API** — artists, popularity, genres, tracks  

---

## 🧩 Architecture

            ┌────────────────────────────┐
            │        GitHub Actions      │
            │   Daily orchestration      │
            └──────────────┬─────────────┘
                           │
                     (cron trigger)
                           │
                           ▼
            ┌────────────────────────────┐
            │       Cloud Run Job        │
            │   Python ingestion script  │
            └──────────────┬─────────────┘
                           │
                           ▼
            ┌────────────────────────────┐
            │ Google Cloud Storage (GCS) │
            │ Bronze - Raw JSON          │
            └──────────────┬─────────────┘
                           │
                           ▼
            ┌────────────────────────────────────┐
            │        Snowflake + dbt             │
            │ Primary Data Warehouse + ELT Engine│
            │ Bronze → Silver → Gold             │
            └──────────────┬─────────────────────┘
                           │ (backup export)
                           ▼
            ┌────────────────────────────┐
            │ Google Cloud Storage (GCS) │
            │ Silver + Gold Backups      │
            │ (Parquet for portability)  │
            └──────────────┬─────────────┘
                           │
                           ▼
            ────────────────────────────┐
            │        Streamlit App      │
            │  Interactive Analytics    │
            │  (Gold-layer consumption) │
            └───────────────────────────┘


---

## 🚀 Pipeline Automation (GitHub Actions)

This project uses two workflows for modularity and clarity.

---

### 1️⃣ Daily Ingestion Workflow (Spotify → GCS)

Runs on schedule via GitHub Actions:

- Executes Cloud Run Job
- Cloud Run container:
  - Calls Spotify API
  - Extracts artist & track data
  - Writes raw snapshots to GCS Bronze folder

Example paths: \
`gs://<bucket>/bronze/artists/YYYY-MM-DD/snapshot.json` \
`gs://<bucket>/bronze/tracks/YYYY-MM-DD/snapshot.json`

---

### 2️⃣ Daily Transformation Workflow (dbt → Snowflake)

GitHub Actions executes:

- `dbt deps`
- `dbt run`
- `dbt test`

Snowflake produces:

- **Bronze**: incremental ingestion tables  
- **Silver**: cleaned entities  
- **Gold**: analytical aggregates and KPIs  

---

## 📊 Data Flow Summary

1. **Extract:** Spotify → Cloud Run → GCS (raw JSON Bronze)
2. **Load to Warehouse:** Snowflake loads Bronze snapshots
3. **Transform:** dbt on Snowflake (Bronze → Silver → Gold)
4. **Persist:** Silver & Gold **stored in Snowflake**
5. **Backup:** Silver & Gold **exported to GCS (Parquet)**
6. **Visualize:** Streamlit querying Snowflake

---

## 📚 Project Goals

This project demonstrates:

- serverless ingestion on GCP  
- ELT with Snowflake + dbt  
- CI/CD-driven data workflows  
- medallion architecture in a hybrid storage pattern  
- dashboarding via Streamlit  
- long-term data durability with cloud object storage backups  

---

> **Data Availability Note**  
> During the ingestion window, Brazilian artists were not returned by the Spotify API
> on Nov 26–28, 2025. The pipeline executed successfully, but the source API returned
> incomplete results for this market.
>
> The dataset intentionally preserves this behavior to reflect real-world data
> availability and avoid artificial imputation.

## 📜 License
This project is licensed under the **MIT License**.