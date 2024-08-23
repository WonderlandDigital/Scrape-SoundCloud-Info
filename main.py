import requests
from bs4 import BeautifulSoup
import json
import re
import random


def get_soundcloud_user_info(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the script tag containing the JSON data
    script_tag = soup.find("script", string=re.compile(r'window\.__sc_hydration'))

    if script_tag:
        # Extract the JSON data from the script
        script_text = script_tag.string
        json_data = re.search(r'\[{.*}\]', script_text)
        
        if json_data:
            json_data = json_data.group()
            
            # Load the JSON data
            data = json.loads(json_data)
            
            # Find the "user" data
            user_data = next((item["data"] for item in data if item["hydratable"] == "user"), None)
            
            if user_data:
                # Extract visuals
                visual_url = None
                if "visuals" in user_data:
                    visuals = user_data["visuals"]
                    if visuals and isinstance(visuals, list):
                        for visual in visuals:
                            if "visual_url" in visual and visual["visual_url"].startswith("https://i1.sndcdn.com/visuals-"):
                                visual_url = visual["visual_url"]
                                break
                
                # Sort and format user information
                sorted_user_info = {
                    "Avatar Link": user_data.get("avatar_url"),
                    "City": user_data.get("city"),
                    "Comment Count": user_data.get("comments_count"),
                    "Country Code": user_data.get("country_code"),
                    "Account Creation": user_data.get("created_at"),
                    "Biography": user_data.get("description"),
                    "Followers": user_data.get("followers_count"),
                    "Following Count": user_data.get("followings_count"),
                    "First Name": user_data.get("first_name"),
                    "Last Name": user_data.get("last_name"),
                    "Full Name": user_data.get("full_name"),
                    "User ID": user_data.get("id"),
                    "Account type": ", ".join([key.capitalize() for key, value in user_data.get("badges", {}).items() if value]),
                    "Last Account Modification": user_data.get("last_modified"),
                    "Liked track count": user_data.get("likes_count"),
                    "Account Link": user_data.get("permalink_url"),
                    "Playlist Count": user_data.get("playlist_count"),
                    "Track Count": user_data.get("track_count"),
                    "Repost Count": user_data.get("reposts_count"),
                    "Account Name": user_data.get("username"),
                    "Verified": user_data.get("verified"),
                    "Background Link": visual_url
                }
                return sorted_user_info
            else:
                return "User data not found in the script."
        else:
            return "JSON data not found in the script."
    else:
        return "Script tag containing the JSON data not found."


def save_user_info_to_file(user_info, file_path):
    with open(file_path, 'w') as file:
        for key, value in user_info.items():
            file.write(f"{key}: {value}\n")

def send_discord_webhook(webhook_url, user_info):
    import requests
    import random
    
    # Generate a random embed color
    embed_color = random.choice([0xFF0000, 0xFF7F00, 0xFFFF00, 0x00FF00, 0x0000FF, 0x4B0082, 0x9400D3])
    
    # Initialize the embed
    embed = {
        "title": f"{user_info['Account Name']}'s Soundcloud Information",
        "description": "Here's the information of the SoundCloud user:",
        "color": embed_color,
        "fields": [],
        "thumbnail": {"url": user_info.get("Avatar Link"), "align": "center"},
    }

    # Check if Background Link is available
    background_link = user_info.get("Background Link")
    if background_link:
        embed["image"] = {"url": background_link, "align": "center"}

    # Add fields with non-empty values
    for key, value in user_info.items():
        if value:
            embed["fields"].append({"name": key, "value": str(value), "inline": True})
    
    # Prepare the payload
    payload = {"embeds": [embed]}
    
    # Send the webhook
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print("Successfully sent webhook")
    else:
        print(f"Failed to send webhook: {response.status_code} - {response.text}")
        print(response.content)  # Print the response content for further inspection


# Example usage:
url = input("Enter URL HERE: ") # Enter the full URL, of the soundcloud page.
webhook_url = ""  # Replace this with your Discord webhook URL
user_info = get_soundcloud_user_info(url)
file_path = f"{user_info['Account Name']}.txt"
if isinstance(user_info, dict):
    save_user_info_to_file(user_info, file_path)
    send_discord_webhook(webhook_url, user_info)
else:
    print(user_info)
