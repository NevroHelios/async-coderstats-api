import requests
import json
from datetime import datetime

BASE_URL = "https://leetcode-stats-api.herokuapp.com/"

def get_leetcode_stats(username: str):
    """Get LeetCode stats for a given username.

    Args:
        username (str): The LeetCode username to fetch stats for.

    Returns:
        dict: A dictionary containing the user's LeetCode stats.
    """
    url = f"{BASE_URL}{username}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'submissionCalendar' in data and isinstance(data['submissionCalendar'], dict):
            formatted_calendar = {}
            for timestamp_str, count in data['submissionCalendar'].items():
                try:
                    timestamp_int = int(timestamp_str)
                    dt_object = datetime.fromtimestamp(timestamp_int)
                    formatted_date = dt_object.strftime("%Y-%m-%d")
                    formatted_calendar[formatted_date] = count
                except ValueError:
                    formatted_calendar[timestamp_str] = count 
            data['submissionCalendar'] = formatted_calendar
        return data
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")



if __name__ == "__main__":
    # Example usage
    username = "nevrohelios"
    try:
        stats = get_leetcode_stats(username)
        print(json.dumps(stats, indent=4))
    except Exception as e:
        print(f"Error: {e}")