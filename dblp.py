import requests
import xml.etree.ElementTree as ET
import time
import json
import argparse
import os
import re
import random
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def format_author_name(author_name):
    """Format author name for DBLP API queries by removing dots and replacing spaces with underscores."""
    author_name = re.sub(r"\.\s*", "_", author_name)  # Remove dots in initials and replace with underscore
    return author_name.replace(" ", "_")  # Replace spaces with underscores



def get_dblp_venue_url(venue_key):
    """Generate the DBLP venue page URL based on the publication key."""
    if venue_key.startswith("journals/"):
        venue_name = venue_key.split("/")[1]  # Extract journal name
        return f"https://dblp.org/db/journals/{venue_name}/"
    elif venue_key.startswith("conf/"):
        venue_name = venue_key.split("/")[1]  # Extract conference name
        return f"https://dblp.org/db/conf/{venue_name}/"
    return None

def get_venue_metadata(venue_url, venue_name, pub_type):
    """Fetch full venue name (for conferences) and ISSN (for journals)."""
    if not venue_url:
        return venue_name, "Unknown"

    try:
        response = requests.get(venue_url, timeout=10)
        response.raise_for_status()
        html = response.text

        # Extract full venue name
        name_match = re.search(r"<h1>(.*?)</h1>", html)
        full_name = name_match.group(1).strip() if name_match else venue_name

        # Extract ISSN (only for journals)
        issn = "N/A"
        if pub_type == "Journal":
            issn_match = re.search(r"ISSN(?:-L)?:?\s*([\dX\-]+)", html, re.IGNORECASE)
            if issn_match:
                issn = issn_match.group(1)

        return full_name, issn

    except requests.RequestException:
        return venue_name, "Unknown"

def query_dblp(author_name, max_retries=5, backoff_factor=2):
    """Query DBLP for an author's publications, ensuring full author match and filtering by year >= 2020."""
    formatted_name = format_author_name(author_name)
    url = f"https://dblp.org/search/publ/api?q=author:{formatted_name}&h=100&format=xml"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            publications = []

            for hit in root.findall(".//hit"):
                title = hit.find(".//title").text if hit.find(".//title") is not None else "Unknown Title"
                year = hit.find(".//year").text if hit.find(".//year") is not None else "Unknown Year"

                # Filter out publications before 2020
                if year.isdigit() and int(year) < 2020:
                    continue

                # Extract venue details
                venue_short = hit.find(".//venue").text if hit.find(".//venue") is not None else "Unknown Venue"
                venue_full = hit.find(".//booktitle").text if hit.find(".//booktitle") is not None else \
                             hit.find(".//journal").text if hit.find(".//journal") is not None else venue_short

                key = hit.find(".//key").text if hit.find(".//key") is not None else ""
                authors = [e.text for e in hit.findall(".//author")]

                # Ensure the exact author name is in the list of authors
                if author_name not in authors:
                    continue

                pub_type = "Conference" if key.startswith("conf/") else "Journal" if key.startswith("journals/") else "Other"
#                qualis = query_qualis(venue_full) if args.qualis else "Unknown"

                # Fetch correct venue name & ISSN
                venue_url = get_dblp_venue_url(key)
                if pub_type in ["Conference", "Journal"]:
                    venue_full, issn = get_venue_metadata(venue_url, venue_full, pub_type)
                else:
                    issn = "N/A"

                publications.append({
                    "title": title,
                    "year": year,
                    "venue": venue_full,  # Full name now correctly retrieved
                    "venue_short": venue_short,  # Stores the short acronym
                    "venue_url": venue_url,  # Direct link to DBLP venue page
                    "issn": issn,  # Now correctly fetching ISSN for journals
                    "type": pub_type,
 #                   "qualis": qualis,
                    "authors": authors
                })

            return publications

        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"Attempt {attempt + 1} failed for {author_name}: {e}")
        except ET.ParseError:
            print(f"Failed to parse XML response from DBLP for {author_name}. Skipping.")

        # Apply exponential backoff before retrying
        if attempt < max_retries - 1:
            time.sleep(backoff_factor ** attempt)
        else:
            print(f"Max retries reached for {author_name}. Skipping.")
            return []

# def query_qualis(venue):
#     """Query OpenAI API for the Qualis ranking of a venue."""
#     if not OPENAI_API_KEY:
#         print("Error: OpenAI API key not set.")
#         return "Unknown"

#     prompt = f"What is the Qualis ranking for the venue '{venue}' in Computer Science?"
#     url = "https://api.openai.com/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {OPENAI_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": "gpt-4o",  # Using the best available model
#         "messages": [{"role": "user", "content": prompt}],
#         "max_tokens": 50
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
#         qualis_info = response.json()["choices"][0]["message"]["content"]
#         return qualis_info.strip()

#     except requests.RequestException as e:
#         print(f"Error querying OpenAI API: {e}")
#         return "Unknown"

def load_authors(filename):
    """Load author names from a file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []

def main():
    parser = argparse.ArgumentParser(description="Fetch publications from DBLP and optionally retrieve Qualis ranking from OpenAI.")
    parser.add_argument("--qualis", action="store_true", help="Query OpenAI for Qualis ranking.")
    global args
    args = parser.parse_args()

    authors = load_authors("docentes.txt")
    if not authors:
        print("No authors to process.")
        return

    results = {}

    for author in authors:
        if author.startswith("#"):
            continue
        print(f"Fetching publications for {author}...")
        results[author] = query_dblp(author)
        time.sleep(random.randint(2, 10))


    with open("publications-dblp.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("Results saved to publications-dblp.json")

if __name__ == "__main__":
    main()
