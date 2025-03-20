import json
import csv
import difflib
import re

# File paths
publications_dblp = "./data/2025/publications-dblp.json"
periodicos_qualis = "./data/2025/periodicos-qualis.csv"
conferencias_qualis = "./data/2025/conferencias-qualis.csv"

def clean_venue_name(venue):
    """Removes acronym at the end of the venue name (e.g., (TSE))."""
    return re.sub(r"\s*\([A-Z0-9]+\)\s*$", "", venue).strip().upper()

def parse_periodicos_qualis_file(qualis_filename):
    """Parses the Qualis CSV as a text file using regex to extract ISSN, title, and Qualis classification."""
    qualis_dict = {}
    with open(qualis_filename, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^([\d]{4}-[\d]{3}[\dX]);\s*(.+?);\s*(A[1-4]|B[1-4]|C)$", line.strip())
            if match:
                issn, title, qualis = match.groups()
                qualis_dict[title.upper()] = {"ISSN": issn, "Qualis CAPES": qualis}
            else:
                print(f"⚠ Skipping malformed line: {line.strip()}")
    return qualis_dict

def parse_conferencias_qualis_file(qualis_filename):
    """Parses the Qualis CSV as a text file using regex to extract ISSN, title, and Qualis classification."""
    qualis_dict = {}

    with open(qualis_filename) as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='\"')
        for row in rows:
            (short, title, qualis) = row
            qualis_dict[title.upper()] = {"short" : short, "Qualis CAPES": qualis}
    return qualis_dict

# Load JSON file
with open(publications_dblp, "r", encoding="utf-8") as f:
    publications = json.load(f)

# Parse Qualis file as text
periodicos_qualis_dict = parse_periodicos_qualis_file(periodicos_qualis)
conferencias_qualis_dict = parse_conferencias_qualis_file(conferencias_qualis)

# Prepare results list
merged_data = []

# Iterate over all authors' publications in the JSON
for author, pubs in publications.items():
    for pub in pubs:
        if not (pub["type"] in ("Journal", "Conference")):
            continue
        title = pub["title"]
        year = pub["year"]
        venue = pub["venue"]
        venue_short = pub["venue_short"]
        authors = ";".join(pub["authors"])
        ty = pub["type"]

        venue_normalized = clean_venue_name(venue)

        issn = "-"
        qualis = "N/A"
        
        if pub["type"] == "Journal":
            matches = difflib.get_close_matches(venue_normalized, periodicos_qualis_dict.keys(), n=1, cutoff=0.8)
            if matches:
                match = matches[0]
                issn = periodicos_qualis_dict[match]["ISSN"]
                qualis = periodicos_qualis_dict[match]["Qualis CAPES"]
        else:
            matches = difflib.get_close_matches(venue_normalized, conferencias_qualis_dict.keys(), n=1, cutoff=0.8)
            if matches:
                match = matches[0]
                qualis = conferencias_qualis_dict[match]["Qualis CAPES"]        
    
        merged_data.append([title, year, venue, venue_short, ty, authors, issn, qualis])

# Save to CSV
output_file = "./data/2025/merged_all_publications.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # Automatically handles double quotes where needed
    writer.writerow(["Title", "Year", "Venue", "Venue Short", "Type", "Authors", "ISSN", "Qualis CAPES"])
    writer.writerows(merged_data)

print(f"✅ Merged data saved to {output_file} with correct double quotes.")
