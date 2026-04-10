"""
cleaner.py
----------
Data cleaning utilities for the Gendered Job Language audit project.
Handles text normalization and sector classification.
"""

import re
import pandas as pd


# ---------------------------------------------------------------------------
# Sector mapping — keyword-based classification from job title
# ---------------------------------------------------------------------------

SECTOR_KEYWORDS = {
    "tech": [
        "engineer", "developer", "software", "cloud",
        "devops", "machine learning", "backend", "frontend", "it support",
    ],
    "data": [
        "data scientist", "data analyst", "data engineer",
        "analytics", "business intelligence",
    ],
    "finance": [
        "finance", "financial", "accountant", "accounting",
        "investment", "banking", "risk analyst",
    ],
    "marketing": [
        "marketing", "content", "seo", "social media",
        "brand", "growth", "copywriter",
    ],
    "hr": [
        "recruiter", "recruiting", "human resources",
        "talent acquisition", "people ops",
    ],
    "care": [
        "nurse", "nursing", "healthcare", "medical", "clinical",
        "therapist", "physician",
    ],
}


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Normalize raw job description text.

    Steps:
        - Lowercase
        - Strip HTML tags and entities
        - Remove URLs
        - Collapse whitespace

    Args:
        text: Raw string (may be NaN).

    Returns:
        Cleaned lowercase string, or empty string if input is null.
    """
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"<[^>]+>", " ", text)       # HTML tags
    text = re.sub(r"&[a-z]+;", " ", text)      # HTML entities
    text = re.sub(r"http\S+", "", text)         # URLs
    text = re.sub(r"\s+", " ", text)            # extra whitespace
    return text.strip()


# ---------------------------------------------------------------------------
# Sector classification
# ---------------------------------------------------------------------------

def assign_sector(title: str) -> str | None:
    """
    Map a job title to one of the predefined sectors using keyword matching.

    The function iterates over SECTOR_KEYWORDS in definition order and returns
    the first matching sector. Returns None if no keyword matches.

    Args:
        title: Job title string (will be lowercased internally).

    Returns:
        Sector label (str) or None.
    """
    title = str(title).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(kw in title for kw in keywords):
            return sector
    return None


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def load_and_clean(filepath: str) -> pd.DataFrame:
    """
    Load raw job postings CSV, clean text fields, assign sectors,
    and apply quality filters.

    Expected input columns: title, description, company_name,
    location, formatted_experience_level, normalized_salary,
    formatted_work_type, remote_allowed.

    Args:
        filepath: Path to the raw CSV file.

    Returns:
        Cleaned DataFrame with added columns:
            - title_clean
            - description_clean
            - sector
    """
    df = pd.read_csv(filepath)

    df["title_clean"] = df["title"].apply(clean_text)
    df["description_clean"] = df["description"].apply(clean_text)
    df["sector"] = df["title_clean"].apply(assign_sector)

    # Quality filters
    df = df.dropna(subset=["sector", "description_clean"])
    df = df[df["description_clean"].str.len() > 200]
    df = df.reset_index(drop=True)

    keep_cols = [
        "title_clean", "description_clean", "sector",
        "company_name", "location",
        "formatted_experience_level", "normalized_salary",
        "formatted_work_type", "remote_allowed",
    ]
    # Keep only columns that exist in this dataset
    keep_cols = [c for c in keep_cols if c in df.columns]

    return df[keep_cols].copy()


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cleaner.py <path_to_raw_csv>")
        sys.exit(1)

    df = load_and_clean(sys.argv[1])
    print(f"✅ Loaded and cleaned: {len(df)} postings")
    print(df["sector"].value_counts())