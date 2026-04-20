import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io
import os
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

def get_latest_sponsor_url():
    """Scrapes the GOV.UK page to find the current CSV download link."""
    base_url = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        if '.csv' in link['href']:
            return link['href']
    return None

def ingest_to_bronze():
    """Downloads the CSV and adds the metadata layer."""
    url = get_latest_sponsor_url()
    if not url:
        print("Could not find CSV link.")
        return
    
    print(f"Fetching data from: {url}")
    
    # Using 'latin-1'because UTF-8 handles poorly (like the £ symbol or accents)
    response = requests.get(url)
    df_raw = pd.read_csv(io.BytesIO(response.content), encoding='latin-1', on_bad_lines='warn')
    
    # ADDING THE METADATA (The Quality Analyst approach)
    df_raw['_ingested_at'] = pd.Timestamp.utcnow()
    df_raw['_source_url'] = url
    df_raw['_file_row_number'] = df_raw.index + 1
    
    return df_raw

def persist_raw_sponsors(df_raw,
                         sf_account: str,
                         sf_user: str,
                         sf_password: str,
                         sf_warehouse: str,
                         sf_database: str,
                         sf_schema: str = "BRONZE",
                         table_name: str = "home_office_sponsors"):
    """
    Write df_raw as a full snapshot to BRONZE.home_office_sponsors.
    Existing table is truncated/recreated (overwrite).
    """
    conn = snowflake.connector.connect(
        account=sf_account,
        user=sf_user,
        password=sf_password,
        warehouse=sf_warehouse,
        database=sf_database,
        schema=sf_schema,
        autocommit=True
    )
    try:
        # Optional: explicit cleanup (ensure no stale existing table remains)
        # This is safe because write_pandas with overwrite writes to temp + COPY then drops
        # but explicit drop is acceptable for guaranteed fresh state.
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {sf_schema}.{table_name}")

        # write_pandas does table creation and copy; overwrite is full replacement.
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_raw,
            table_name=table_name,
            database=sf_database,
            schema=sf_schema,
            auto_create_table=True,
            overwrite=True
        )

        if not success:
            raise RuntimeError(f"write_pandas failed for {sf_schema}.{table_name}")

        return {
            "status": "success",
            "rows_loaded": nrows,
            "chunks": nchunks
        }
    finally:
        conn.close()

def main():
    load_dotenv()  # Load environment variables from .env file
    print("Starting UK Sponsor Navigator Ingestion...")

    df_raw = ingest_to_bronze() 
    
    if df_raw is None or df_raw.empty:
        print("Extraction failed. No data to load.")
        return

    df_raw.columns = [c.upper().replace(' ', '_').replace('/', '_') for c in df_raw.columns]
    print(f"Data extracted: {len(df_raw)} rows found.")

    result = persist_raw_sponsors(
        df_raw=df_raw,
        sf_account=os.getenv("SF_ACCOUNT"),
        sf_user=os.getenv("SF_USER"),
        sf_password=os.getenv("SF_PASSWORD"),
        sf_warehouse="TRANSFORM_WH",
        sf_database="UK_SPONSOR_NAVIGATOR",
        sf_schema="BRONZE"
    )

    print(f"Phase 1 Complete: {result['status']}")

if __name__ == "__main__":
    main()