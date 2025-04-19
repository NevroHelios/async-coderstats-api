import requests
from bs4 import BeautifulSoup
import sys
import time
from pprint import pprint
import re # For potential pattern matching if needed

def scrape_kaggle_user_details(username: str):
    """
    Scrapes a Kaggle user's public profile page for details using Requests and BeautifulSoup.

    Args:
        username: The Kaggle username to look up.

    Returns:
        A dictionary containing the scraped details, or None if the profile
        cannot be fetched or parsed.

    NOTE: This scraper is FRAGILE and depends on Kaggle's current website structure.
          It WILL likely break if Kaggle updates its site design.
    """
    profile_url = f"https://www.kaggle.com/{username}"
    print(f"Attempting to scrape profile: {profile_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    details = {"username": username, "profile_url": profile_url, "scraped_data": {}}

    try:
        # Add a small delay to be polite
        time.sleep(1)
        response = requests.get(profile_url, headers=headers, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: Kaggle profile for '{username}' not found (404).")
        else:
            print(f"Error: HTTP error fetching profile: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to Kaggle: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during request: {e}")
        return None

    try:
        soup = BeautifulSoup(response.text, 'lxml') # Use lxml parser

        # --- Scrape Specific Details ---
        # Selectors MUST be updated if Kaggle changes its HTML/CSS.
        # These selectors are based on inspection *at the time of writing* and are examples.

        # 1. Display Name
        try:
            # Often in an element with specific class, might be an h1 or div
            # Example selector (NEEDS VERIFICATION/ADJUSTMENT):
            name_element = soup.find('h1', class_=re.compile(r'profile-header__display-name')) # Use regex for potentially dynamic class parts
            details["scraped_data"]["display_name"] = name_element.text.strip() if name_element else "Not Found"
        except Exception as e:
            print(f"Warning: Could not parse display name: {e}")
            details["scraped_data"]["display_name"] = "Error Parsing"

        # 2. Bio / Tagline
        try:
             # Often a div or p element under the name
             # Example selector (NEEDS VERIFICATION/ADJUSTMENT):
             bio_element = soup.find('p', class_=re.compile(r'profile-header__bio'))
             details["scraped_data"]["bio"] = bio_element.text.strip() if bio_element else "Not Found/No Bio"
        except Exception as e:
            print(f"Warning: Could not parse bio: {e}")
            details["scraped_data"]["bio"] = "Error Parsing"

        # 3. Location, Occupation, Employer (Often grouped together)
        try:
            # These might be list items or divs with specific icons/classes
            # Example selector (NEEDS VERIFICATION/ADJUSTMENT):
            info_list = soup.find('ul', class_=re.compile(r'profile-header__metadata'))
            if info_list:
                items = info_list.find_all('li')
                metadata = {}
                for item in items:
                    text = item.get_text(strip=True)
                    # Simple keyword matching (might need improvement)
                    if 'Location' in item.prettify() or 'map-pin' in item.prettify(): # Check class/icon hints
                        metadata['location'] = text
                    elif 'Occupation' in item.prettify() or 'briefcase' in item.prettify():
                         metadata['occupation'] = text
                    elif 'Employer' in item.prettify() or 'building' in item.prettify():
                         metadata['employer'] = text
                    elif 'link' in item.prettify(): # Website link
                         link_tag = item.find('a')
                         metadata['website'] = link_tag['href'] if link_tag else text
                    elif 'Joined' in text: # Join Date (might be less reliable)
                         metadata['joined_approx'] = text.replace('Joined', '').strip()

                details["scraped_data"]["metadata"] = metadata
            else:
                 details["scraped_data"]["metadata"] = {"status": "Metadata section not found"}
        except Exception as e:
            print(f"Warning: Could not parse metadata (location/job etc): {e}")
            details["scraped_data"]["metadata"] = {"status": "Error Parsing"}


        # 4. Tiers and Ranks (Competitions, Datasets, Notebooks, Discussions)
        # This is often structured in sections. Find the container for all stats.
        # Example selector (NEEDS VERIFICATION/ADJUSTMENT):
        tiers_data = {}
        try:
            # Find the main progression/tiers section
            progression_section = soup.find('div', class_=re.compile(r'profile-progression')) # Example class
            if progression_section:
                # Find individual tier items (Competitions, Datasets, etc.)
                tier_items = progression_section.find_all('a', class_=re.compile(r'profile-progression-medal')) # Link around the medal/info
                if not tier_items: # Fallback: maybe they are divs/lis?
                     tier_items = progression_section.find_all('div', class_=re.compile(r'profile-progression-medal'))

                for item in tier_items:
                    category = "Unknown"
                    tier = "Unknown"
                    rank = "Unranked"
                    points = "N/A"
                    highest_rank = "N/A"

                    # Extract Category (e.g., "Competitions")
                    # Look for a title or identifiable text within the item
                    cat_element = item.find(['h4', 'h5', 'span'], class_=re.compile(r'title|name|category')) # Adjust tags/classes
                    if cat_element:
                         category = cat_element.text.strip()
                    elif item.get('href'): # Try getting from link URL
                        if '/competitions' in item['href']: category = 'Competitions'
                        elif '/datasets' in item['href']: category = 'Datasets'
                        elif '/code' in item['href']: category = 'Notebooks' # Often called Code now
                        elif '/discussion' in item['href']: category = 'Discussions'

                    # Extract Tier (e.g., "Master") - often in a span or div with specific class
                    tier_element = item.find(['span','div'], class_=re.compile(r'tier|level|medal-label')) # Adjust
                    if tier_element:
                        tier = tier_element.text.strip()

                    # Extract Rank (e.g., "#123") - often nearby
                    rank_element = item.find(['span', 'div'], class_=re.compile(r'rank')) # Adjust
                    if rank_element:
                        rank_text = rank_element.text.strip()
                        # Clean up common prefixes like "Rank #"
                        rank = re.sub(r'^(Rank|#)\s*', '', rank_text, flags=re.IGNORECASE)
                        if not rank or rank.lower() == 'unranked':
                           rank = "Unranked" # Standardize

                    # Extract Points (sometimes available)
                    points_element = item.find(['span', 'div'], class_=re.compile(r'points|score')) # Adjust
                    if points_element:
                        points = points_element.text.strip()

                    # Extract Highest Rank/Tier (might be harder, often needs specific text search)
                    highest_rank_element = item.find(string=re.compile(r'Highest Rank|Peak Rank')) # Search for specific text
                    if highest_rank_element:
                       # Try to get the value usually following or nearby this text
                       parent = highest_rank_element.find_parent()
                       if parent:
                           # This logic is highly speculative and needs refinement based on actual HTML
                           possible_ranks = parent.find_all(['span','div'], class_=re.compile(r'rank|value'))
                           if len(possible_ranks) > 1: # Assume the second one might be the highest
                               highest_rank = possible_ranks[-1].text.strip()
                           else: # Or just grab nearby text
                               highest_rank = highest_rank_element.next_sibling.strip() if highest_rank_element.next_sibling else "N/A"
                           highest_rank = re.sub(r'^(Rank|#)\s*', '', highest_rank, flags=re.IGNORECASE)


                    if category != "Unknown":
                        tiers_data[category] = {
                            "tier": tier,
                            "current_rank": rank,
                            "points": points,
                            "highest_rank_scraped": highest_rank # Note: This is often unreliable
                        }
            else:
                 tiers_data = {"status": "Tiers section not found"}

            details["scraped_data"]["progression"] = tiers_data

        except Exception as e:
            print(f"Warning: Could not parse progression/tiers: {e}")
            details["scraped_data"]["progression"] = {"status": "Error Parsing"}


        # 5. Badges (Can be tricky, often images with titles or specific divs)
        badges_list = []
        try:
            # Find sections likely containing badges (might be multiple)
            # Example selector (NEEDS VERIFICATION/ADJUSTMENT): Adjust class name
            badge_sections = soup.find_all('div', class_=re.compile(r'profile__badges|badge-section|achievements'))

            for section in badge_sections:
                # Badges might be 'img' tags with titles, or divs/spans
                # Example selector (NEEDS VERIFICATION/ADJUSTMENT): Find elements *within* the section
                found_badges = section.find_all(['img', 'div', 'span'], title=True) # Look for elements with a title attribute
                if not found_badges: # Fallback: maybe list items?
                     found_badges = section.find_all('li')

                for badge_element in found_badges:
                    badge_name = None
                    if badge_element.get('title'):
                        badge_name = badge_element['title'].strip()
                    elif badge_element.get('alt'): # For images
                         badge_name = badge_element['alt'].strip()
                    elif badge_element.find(['span','div'], title=True): # Nested title
                         badge_name = badge_element.find(['span','div'], title=True)['title'].strip()
                    else: # Fallback: just get text if it's not an image
                         if badge_element.name != 'img':
                             badge_name = badge_element.get_text(strip=True)

                    if badge_name and badge_name not in badges_list: # Avoid duplicates if possible
                         # Basic filtering of non-badge text/titles if needed
                         if len(badge_name) > 3 and 'medal' not in badge_name.lower() and 'tier' not in badge_name.lower(): # Simple filter
                            badges_list.append(badge_name)

            details["scraped_data"]["badges"] = badges_list if badges_list else "No badges found or parsing failed"

        except Exception as e:
            print(f"Warning: Could not parse badges: {e}")
            details["scraped_data"]["badges"] = "Error Parsing Badges"

        # 6. Other Stats (Followers, Following, etc. - might be near name or in stats section)
        # Example selector (NEEDS VERIFICATION/ADJUSTMENT):
        stats = {}
        try:
           # Look for elements containing follower/following counts - often links or spans
           stats_container = soup.find('div', class_=re.compile(r'profile-header__meta|profile-stats')) # Adjust class
           if stats_container:
               # Example: Find links with href containing /followers or /following
               follower_link = stats_container.find('a', href=lambda href: href and f'/{username}/followers' in href)
               following_link = stats_container.find('a', href=lambda href: href and f'/{username}/following' in href)

               if follower_link:
                   # Count is often inside a span or div within the link
                   count_el = follower_link.find(['span', 'div'], class_=re.compile(r'count|value|number'))
                   stats['followers'] = count_el.text.strip() if count_el else follower_link.text.strip() # Fallback to link text
               if following_link:
                   count_el = following_link.find(['span', 'div'], class_=re.compile(r'count|value|number'))
                   stats['following'] = count_el.text.strip() if count_el else following_link.text.strip()

               # Clean possible non-numeric parts (like 'k' for thousands) - optional
               for key in stats:
                   stats[key] = stats[key].split()[0] # Take first part if text is like "1.2k Followers"

           details["scraped_data"]["social_stats"] = stats if stats else {"status": "Social stats not found"}

        except Exception as e:
            print(f"Warning: Could not parse social stats: {e}")
            details["scraped_data"]["social_stats"] = {"status": "Error Parsing"}


        # --- Competitions Won / History ---
        # NOTE: A *full* list of competitions participated/won is typically NOT on the main
        # profile page's initial HTML. It's often loaded dynamically or on a separate sub-page.
        # Scraping that requires more advanced techniques (like Selenium or analyzing network requests).
        # We already scraped the *summary* (tier/rank) in the 'progression' section above.
        # Adding a placeholder here to acknowledge the limitation.
        details["scraped_data"]["competition_history"] = "Full history not scraped (likely requires dynamic loading/separate page)"


        return details

    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        # Optionally include traceback:
        # import traceback
        # print(traceback.format_exc())
        return None


# --- Main Execution ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_username = sys.argv[1]
    else:
        target_username = input("Enter the Kaggle username: ")

    if not target_username:
        print("No username provided. Exiting.")
    else:
        scraped_info = scrape_kaggle_user_details(target_username)

        if scraped_info:
            print("\n" + "="*40)
            print(f" Scraped Kaggle User Details for: {target_username} ")
            print("="*40)
            pprint(scraped_info['scraped_data'])
            print("="*40)
            print("\n⚠️ DISCLAIMER: Scraping is fragile! Results depend on Kaggle's current website")
            print("   structure and may be incomplete or inaccurate. Selectors may need updating.")
            print("   Use the official Kaggle API for more reliable (but less detailed) data.")
        else:
            print(f"\nFailed to retrieve or parse details for {target_username}.")