import requests
from bs4 import BeautifulSoup
import re

def get_codeforces_user_data(username):
    print(f"Fetching data for: {username}")
    url = f"https://codeforces.com/profile/{username}"
    try:
        # Use a timeout and headers to mimic a browser slightly more
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (404, 500, etc.)

        soup = BeautifulSoup(response.text, "html.parser")

        # --- Username ---
        # Handle both rated and unrated user spans
        username_element = soup.select_one(".main-info .rated-user, .main-info .unrated-user")
        scraped_username = username_element.text.strip() if username_element else None
        if not scraped_username:
             # Fallback if the standard selectors fail but page exists
             title_tag = soup.find('title')
             if title_tag and 'Profile -' in title_tag.text:
                 scraped_username = title_tag.text.split(' - ')[1].strip()


        # --- Rating and Rank ---
        # Use a more robust selector if possible (e.g., check parent ul)
        info_list = soup.select(".info ul li") # Get all list items in the info block
        current_contest_rating = None
        user_rank = None
        max_rating_info = None # To potentially grab max rank/rating too

        rating_li = None
        contribution_li = None
        friend_li = None

        # Iterate through list items to find the correct ones robustly
        for item in info_list:
            text = item.text.strip()
            if text.startswith("Contest rating:") or "Unrated" in text and not text.startswith("Contribution"):
                rating_li = item
            elif text.startswith("Contribution:"):
                contribution_li = item
            elif text.startswith("Friend of:"):
                friend_li = item

        if rating_li:
            raw_rating_text = rating_li.text.strip()
            if "Unrated" in raw_rating_text:
                current_contest_rating = "0" # Represent unrated numerically? Or keep "Unrated"?
                user_rank = "Unrated"
            else:
                # Extract current rating using regex
                rating_match = re.search(r"Contest rating:\s*(\d+)", raw_rating_text)
                if rating_match:
                    current_contest_rating = rating_match.group(1)

                # Extract rank from parentheses (handle different formats)
                # Format 1: (Rank Name, Rating) e.g. (Legendary Grandmaster, 3828)
                # Format 2: (Rank Name) e.g. (Candidate Master) - less common now maybe?
                rank_match = re.search(r"\((.*?)\)", raw_rating_text)
                if rank_match:
                    rank_string = rank_match.group(1).strip()
                    # Split by comma if present to get just the name
                    user_rank = rank_string.split(",")[0].strip()
        else:
            # If no rating li found, user might be very new or page structure changed
             current_contest_rating = "0" # Default assumptions
             user_rank = "Unrated"


        # --- Contribution ---
        contribution = "0" # Default to 0
        if contribution_li:
            contribution_element = contribution_li.select_one("span") # Usually inside a span
            if contribution_element:
                 contribution = contribution_element.text.strip()


        # --- Friend Count ---
        number_of_friends = "0" # Default to 0
        if friend_li:
            raw_friend_text = friend_li.text.strip()
            # Original JS logic just removed the prefix. Let's extract the number.
            friend_match = re.search(r"(\d+)\s+user", raw_friend_text)
            if friend_match:
                number_of_friends = friend_match.group(1)
            # Handle "Friend of: 0 users" or if regex fails
            elif " 0 users" in raw_friend_text:
                 number_of_friends = "0"


        # Make sure we found a username at least, otherwise it's likely not a valid profile page
        if not scraped_username:
             raise ValueError("Could not extract username, profile page might be invalid.")

        return {
            "username": scraped_username,
            "userRank": user_rank,
            # Ensure rating is a string, even if 0
            "currentContestRating": str(current_contest_rating) if current_contest_rating is not None else None,
            "numberOfFriends": number_of_friends,
            "contribution": contribution,
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"User '{username}' not found (404 Error)."
        else:
            return f"HTTP Error fetching profile for {username}: {e}"
    except requests.exceptions.RequestException as e:
        # Catch network errors, timeouts, etc.
        return f"Network error fetching profile for {username}: {e}"
    except Exception as e:
        # Catch any other error during parsing (AttributeError, ValueError, etc.)
        # Including the original TypeError if checks were missed
        import traceback
        print(traceback.format_exc()) # Print full traceback for debugging
        return f"Error parsing profile data for {username}: {e}"


if __name__ == "__main__":
    print("--- Testing orzdevinwang ---")
    result = get_codeforces_user_data("orzdevinwang")
    print(result)

    print("\n--- Testing Petr ---")
    result = get_codeforces_user_data("Petr")
    print(result)

    print("\n--- Testing Codeforces (Unrated) ---")
    result = get_codeforces_user_data("Codeforces") # Often unrated or special case
    print(result)

    print("\n--- Testing Non-existent user ---")
    result = get_codeforces_user_data("non_existent_user_123456789")
    print(result)

    print("\n--- Testing User with 0 Friends (Example - needs verification) ---")
    # You might need to find an actual user with 0 friends listed for a real test
    # result = get_codeforces_user_data("some_user_with_zero_friends")
    # print(result)