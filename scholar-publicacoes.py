import os
import json
import time
import random
from serpapi import GoogleSearch


class MissingEnvironmentVariable(Exception):
    pass

# Your SerpApi Key (replace with your actual key)
SERPAPI_KEY = os.environ["SERPAPI_KEY"]

if SERPAPI_KEY is None:
    raise MissingEnvironmentVariable(f"{var_name} does not exist")

def get_author_publications(author_name):
    """Retrieve all publications for a given author using SerpApi."""
    # Step 1: Find the author's Google Scholar ID
    search_params = {
        "engine": "google_scholar_profiles",
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "mauthors": author_name
    }

    search = GoogleSearch(search_params)
    results = search.get_dict()

    if "profiles" not in results or not results["profiles"]:
        print(f"Author '{author_name}' not found.")
        return None

    author_id = results["profiles"][0]["author_id"]

    # Step 2: Retrieve all publications with pagination
    publications = []
    start = 0
    num_results = 20  # Max results per page
    while True:
        params = {
            "engine": "google_scholar_author",
            "api_key": SERPAPI_KEY,
            "hl": "en",
            "author_id": author_id,
            "start": start,  # Pagination offset
            "num": num_results  # Fetch up to 20 results per request
        }

        search = GoogleSearch(params)
        author_data = search.get_dict()

        if "articles" not in author_data or not author_data["articles"]:
            break  # Stop if no more publications

        for article in author_data["articles"]:
            publications.append({
                "Title": article.get("title", "Unknown Title"),
                "Co-authors": article.get("authors", "Unknown"),
                "Year": article.get("year", "Unknown Year"),
                "Venue": article.get("publication", "Unknown Venue"),
                "Citations": article.get("cited_by", {}).get("value", 0)
            })

        # Check if there are more results
        if len(author_data["articles"]) < num_results:
            break  # Stop if the last page has fewer than `num_results` results

        start += num_results  # Move to the next batch
        time.sleep(random.randint(2, 5))  # Avoid rate limits

    return {
        "Author": author_name,
        "Publications": publications
    }

def main():
    """Main function to process authors and save results."""
    try:
        # Read authors from file
        with open('docentes-scholar.txt', 'r', encoding='utf-8') as file:
            author_names = [line.strip() for line in file.readlines() if line.strip()]

        all_authors_data = []
        for author_name in author_names:
            author_data = get_author_publications(author_name)
            if author_data:
                all_authors_data.append(author_data)

            # Avoid hitting rate limits
            time.sleep(random.randint(2, 5))

        # Save to JSON file
        with open('publications5.json', 'w', encoding='utf-8') as json_file:
            json.dump(all_authors_data, json_file, indent=4, ensure_ascii=False)

        print("Publications data saved to 'publications5.json'.")

    except FileNotFoundError:
        print("Error: 'docentes-scholar.txt' file not found.")

if __name__ == "__main__":
    main()
 
