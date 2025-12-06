# 🎧 Spotify ELT Data Pipeline — GCP + Snowflake + dbt + Streamlit

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Built with](https://img.shields.io/badge/Built%20with-Databricks%20%2B%20GCP-blue)
![Data Engineering](https://img.shields.io/badge/domain-Data%20Engineering-orange.svg)

---

## 📖 Overview

> **Note on Architecture Decision**
> While classical medallion architecture keeps all layers (Bronze, Silver, Gold) fully inside the data warehouse, this project adopts a hybrid warehouse pattern.
Snowflake now acts as the primary data warehouse, hosting:
>- Bronze — semi-structured raw tables loaded from GCS
>- Silver — cleaned and normalized entities
>- Gold — analytical & metric tables 

>At the same time, all three layers are also exported back to Google Cloud Storage (GCS) in Parquet format as a resilience and longevity strategy.
This dual-storage approach provides:
>- Full analytics power inside Snowflake (warehouse, compute, SQL, dbt modeling)
>- Long-term data ownership in GCS, even if Snowflake access becomes temporary
>- Portability to migrate the project in the future to BigQuery, DuckDB, Databricks, or Polars
>- Decoupling between compute (Snowflake) and durable storage (GCS)



This project implements a modern cloud-native data pipeline that extracts daily artist insights from the Spotify Web API, stores raw JSON data in Google Cloud Storage (GCS), transforms it into analytics-ready tables using Snowflake + dbt, and finally exposes insights through a Streamlit dashboard.

* The pipeline showcases real-world engineering practices:

  * serverless ingestion (Cloud Run Jobs)
  * CI/CD-based orchestration (GitHub Actions)
  * ELT modeling with dbt (bronze → silver → gold)
  * analytics on Snowflake
  * interactive visualization with Streamlit

---

## ⚙️ Tech Stack

### Ingestion & Orchestration

* **GitHub Actions** – scheduled automation + CI/CD
* **Cloud Run Jobs** – serverless batch ingestion (Python)

### Storage & Warehouse

* **Google Cloud Storage (GCS)** – raw/bronze snapshots + persisted Silver & Gold layers (Parquet)
* **Snowflake** – used as a **compute engine** for transformations

### Transformation

* **dbt Core** — SQL models, lineage, tests, documentation

### Visualization

* **Streamlit** — interactive dashboard powered by Snowflake queries

### Data Source

* **Spotify API** – artists, popularity, genres, and top tracks

---

## 🧩 Architecture

```
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
                ┌────────────────────────────┐
                │       Snowflake + dbt      │
                │     Compute-only ELT       │
                │ Bronze → Silver → Gold     │
                └──────────────┬─────────────┘
                               │ (export parquet)
                               ▼
                ┌────────────────────────────┐
                │ Google Cloud Storage (GCS) │
                │  Silver + Gold (Parquet)   │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │        Streamlit App       │
                │   Analytics & Visuals      │
                └────────────────────────────┘
```

---

## 🚀 Pipeline Automation (GitHub Actions)

This project uses two separate workflows for simplicity, modularity, and observability.

### 1️⃣ Daily Ingestion Workflow (Ingest Spotify → GCS)

* Scheduled via GitHub Actions cron
* Executes the Cloud Run Job
* Cloud Run Job runs a Python container:

  * calls the Spotify API
  * extracts artist & track data
  * writes bronze snapshots to GCS

Snapshot folder structure:
`gs://<bucket>/bronze/artists/YYYY-MM-DD/snapshot.json`
`gs://<bucket>/bronze/tracks/YYYY-MM-DD/snapshot.json`

### 2️⃣ Daily Transformation Workflow (dbt → Snowflake)

GitHub Actions runs:

* dbt deps
* dbt run (bronze → silver → gold)
* dbt test

The Snowflake pipeline creates:

* **Silver:** cleaned artist & track tables
* **Gold:** analytical metrics for:

  * popularity evolution
  * top artists of the season
  * christmas trend analysis (Nov–Dec)
  * ranking + KPIs

---

## 📊 Data Flow Summary

1. **Extract:** Spotify → Cloud Run Jobs → Python ingestion
2. **Load (Raw):** Python → GCS (Raw JSON)
3. **Transform:** dbt on Snowflake → normalization, cleansing, enrichment, analytics
4. **Persist:** Silver & Gold exported from Snowflake → GCS (Parquet)
5. **Visualize:** Streamlit webapp reading from Snowflake

---

## 📚 Project Goals

This project demonstrates:

* serverless batch ingestion on GCP
* modern ELT workflow using Snowflake + dbt
* CI/CD-driven orchestration
* data modeling best practices (bronze → silver → gold + lakehouse export)
* dashboarding with Streamlit
* a complete, production-inspired data engineering pipeline with long-term data durability.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
