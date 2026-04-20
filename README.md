# 🇬🇧 UK Visa Sponsor Navigator

An automated, end-to-end data pipeline and analytics dashboard designed to help international talent find licensed "Skilled Worker" sponsors in the UK. 

### Architecture
The project follows a **Medallion Architecture** (Bronze, Silver, Gold) to transform messy government CSV data into a production-ready data product.

* **Extraction:** Python (BeautifulSoup) dynamic scraper to fetch the latest Home Office data.
* **Ingestion:** Python (Pandas + Snowflake Connector) automated load into Snowflake.
* **Transformation:** dbt (Data Build Tool) for modular SQL modelling.
* **Storage:** Snowflake Cloud Data Warehouse.
* **Presentation:** Streamlit (Python) high-performance interactive dashboard.

### Tech Stack
- **Languages:** Python 3.13, SQL
- **Cloud Data Warehouse:** Snowflake
- **Data Transformation:** dbt Cloud
- **Frontend:** Streamlit
- **DevOps:** GitHub, Dotenv (Secrets Management)

### Key Engineering Features & Challenges
- **Compute Efficiency:** Filtered 140k+ records at the Staging layer to reduce Snowflake credit consumption.
- **Data Integrity:** Implemented a `QUALIFY` clause with `row_number()` to remove 711+ duplicate records, ensuring a "Golden Record" per sponsor.
- **Semantic Mapping:** Transformed messy string ratings into a numeric 5-star scoring system for UI/UX consistency.
- **Robustness:** Handled special characters (ampersands/spaces) in raw headers using quoted identifiers.

### Setup & Installation
1. **Clone the repo:**
   `git clone https://github.com/SaravanaPrashanth/uk-sponsor-navigator.git`
2. **Setup Environment:**
   Create a `.env` file with your Snowflake credentials (User, Password, Account, Warehouse, Database, Schema).
3. **Run Pipeline:**
   - Execute `main.py` for ingestion.
   - Run `dbt build` to transform and test data.
4. **Launch Dashboard:**
   `streamlit run app.py`

---
Built by **Saravana Prashanth**
