# 🎧 Spotify ELT Data Pipeline — GCP + Snowflake + dbt + Streamlit

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Built with](https://img.shields.io/badge/Built%20with-GCP%20%2B%20Snowflake-blue)
![Data Engineering](https://img.shields.io/badge/domain-Data%20Engineering-orange.svg)

---

## 📖 Overview

> **Architecture Note**  
> This project follows a **medallion-style ELT architecture** where **Snowflake is the primary and sole analytical data warehouse**, responsible for storing and processing all curated layers — Bronze, Silver, and Gold.
>
> The architectural flow is intentionally simple and deterministic:
> - Raw JSON data is ingested daily from the Spotify API and stored immutably in **Google Cloud Storage (GCS)** as Bronze snapshots.
> - Snowflake ingests these snapshots and materializes an **incremental Bronze table**.
> - dbt performs all transformations **inside Snowflake**, producing Silver (cleaned entities) and Gold (analytical aggregates).
>
> Bronze serves as the immutable source of truth, while Silver and Gold are **fully reproducible deterministic layers** stored only in Snowflake to avoid redundant persistence and unnecessary operational complexity.

This project implements a modern ELT pipeline that extracts daily artist insights
from the Spotify API, stores raw JSON in GCS, transforms data in Snowflake using dbt,
and exposes curated analytical insights through an interactive Streamlit application
that queries Gold-layer datasets directly from Snowflake.

The pipeline includes:

- serverless ingestion (Cloud Run Jobs)
- CI/CD orchestration (GitHub Actions)
- ELT modeling with dbt (Bronze → Silver → Gold)
- analytics computed and stored in Snowflake
- visualization via Streamlit

---
## 🧠 Key Engineering Decisions

- **GitHub Actions as the orchestration layer**  
  GitHub Actions is used as the primary scheduler and CI/CD orchestrator, enabling
  reproducible, version-controlled pipelines without introducing additional
  workflow infrastructure.

- **Cloud Run Jobs for serverless ingestion**  
  Data ingestion is executed via Cloud Run Jobs, allowing stateless, on-demand
  batch execution with automatic scaling and no always-on compute.

- **Bronze stored immutably in GCS as the source of truth**  
  Raw Spotify API responses are persisted as immutable JSON snapshots in GCS,
  ensuring full reproducibility and auditability of downstream transformations.

- **Snowflake as the single analytical data warehouse**  
  Snowflake hosts all Bronze, Silver, and Gold tables and executes every
  transformation, avoiding unnecessary data duplication across systems.

- **Silver and Gold modeled as deterministic, reproducible layers**  
  Curated layers are not exported outside Snowflake, as they can be fully
  recomputed from Bronze, reducing storage overhead and operational complexity.

- **Incremental modeling with merge semantics in Silver**  
  Daily snapshots are deduplicated using incremental merge strategies to ensure
  correct historical tracking while supporting late or repeated ingestions.

- **Ranking logic handled at query-time in the application layer**  
  Gold tables preserve analytical facts without hardcoded ranking filters,
  allowing market-aware and context-specific rankings to be computed dynamically.

- **Market-aware analytics to avoid post-filtered rankings**  
  Rankings are computed per market (ALL, BR, GB) before limiting results, ensuring
  correct analytical behavior instead of filtered subsets.

- **Track-level analytics keyed by `track_id`**  
  All time series and aggregations rely on Spotify `track_id` rather than
  `track_name`, preventing semantic collisions between homonymous tracks.

## 🎄 Dataset Scope

This project tracks **Spotify artists and their top tracks during the 2025 Christmas season**, focusing on the period from **November to December 2025**.

The dataset includes:

- A curated list of **globally relevant and Brazil-relevant artists during Christmas season**
- Daily snapshots of:
  - artist popularity and follower counts
  - top tracks per artist
  - track popularity evolution over time
- Historical tracking to capture **seasonality and popularity dynamics** as Christmas approaches

The goal is to analyze how music consumption evolves during the holiday season,
compare market behavior (Global vs Brazil), and identify the most dominant artists
and tracks over time.

---

## ⚙️ Tech Stack

### Ingestion & Orchestration
* **GitHub Actions** — scheduled automation + CI/CD  
* **Cloud Run Jobs** — serverless batch ingestion  

### Storage & Warehouse
* **Google Cloud Storage (GCS)**  
  - Immutable Bronze snapshots (raw JSON)  
* **Snowflake**  
  - **Primary data warehouse**
  - Hosts Bronze, Silver, and Gold tables  
  - Executes all dbt transformations  

### Transformation
* **dbt (Fusion / Core)** — SQL models, incremental logic, tests, documentation  

### Visualization
* **Streamlit** — interactive analytics powered by Snowflake queries  

---

## 📊 Streamlit Analytics Application

This project includes an interactive Streamlit dashboard that consumes curated
Gold tables directly from Snowflake.

The application focuses on **analytical storytelling**, highlighting:

- most popular tracks by market
- tracks with highest popularity growth
- daily popularity evolution over time
- artist-level performance comparison

All rankings are **computed dynamically at query time**, ensuring that market filters
(ALL, BR, GB) produce correct results rather than post-filtered subsets.

The application connects directly to Snowflake using the Python connector and is
fully compatible with Snowflake-native Streamlit deployments if required.

---

## 🧩 Streamlit Development Workflow

The Streamlit application is developed and versioned locally using GitHub, providing
a clean development experience with full IDE support.

The app queries Snowflake directly for all analytical data. No intermediate exports
or materialized views outside Snowflake are required, keeping Snowflake as the single
source of truth for analytics.

---

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
                           │
                           ▼
            ────────────────────────────┐
            │        Streamlit App      │
            │  Interactive Analytics    │
            │  (Gold-layer consumption) │
            └───────────────────────────┘

---
## 🚀 Pipeline Automation (GitHub Actions)

### 1️⃣ Daily Ingestion Workflow (Spotify → GCS)

Runs on schedule via GitHub Actions:

- Executes a Cloud Run Job
- Cloud Run container:
  - Calls Spotify API
  - Extracts artist and track data
  - Writes raw JSON snapshots to GCS Bronze folders

Example paths:  
`gs://<bucket>/bronze/artists/YYYY-MM-DD/snapshot.json`  
`gs://<bucket>/bronze/tracks/YYYY-MM-DD/snapshot.json`

---

### 2️⃣ Daily Transformation Workflow (dbt → Snowflake)

GitHub Actions executes:

- `dbt deps`
- `dbt build` (models + tests)

Snowflake produces:

- **Bronze**: incremental ingestion tables  
- **Silver**: cleaned, deduplicated entities  
- **Gold**: analytical aggregates and KPIs  

All transformations and data quality tests are enforced daily via CI/CD.

---

## 📚 dbt Documentation & Lineage

This project leverages dbt’s built-in documentation and lineage features to ensure
transparency, traceability, and data quality.

All models, sources, and tests are documented using dbt schema files. During each
execution, dbt generates metadata artifacts such as:

- `manifest.json`
- `catalog.json`

These artifacts describe:

- full lineage (Bronze → Silver → Gold)
- column-level documentation
- applied data quality tests
- model dependencies

The project uses **dbt Fusion**, which generates these artifacts during execution
and allows visualization via compatible documentation and lineage tools.

---

## 📊 Data Flow Summary

1. **Extract:** Spotify → Cloud Run → GCS (raw JSON Bronze)
2. **Load:** Snowflake ingests Bronze snapshots
3. **Transform:** dbt on Snowflake (Bronze → Silver → Gold)
4. **Persist:** Silver and Gold stored in Snowflake
5. **Visualize:** Streamlit querying Snowflake

---

## 📚 Project Goals

This project demonstrates:

- serverless ingestion on GCP  
- ELT pipelines with Snowflake + dbt  
- CI/CD-driven data workflows  
- deterministic medallion architecture  
- analytics-focused dashboarding via Streamlit  
- real-world data variability handling  

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
