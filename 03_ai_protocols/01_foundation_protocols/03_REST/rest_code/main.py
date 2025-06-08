import requests
import json

# Using JSONPlaceholder, a free fake online REST API for testing and prototyping.
BASE_URL = "https://jsonplaceholder.typicode.com"

# --- GET request to fetch a single post ---
def get_post(post_id):
    print(f"\\n--- GET Request for post/{post_id} ---")
    try:
        response = requests.get(f"{BASE_URL}/posts/{post_id}")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        print(f"Status Code: {response.status_code}")
        post_data = response.json()
        print(f"Post Title: {post_data.get('title')}")
        # print(f"Full Response Data: {post_data}")
        return post_data
    except requests.exceptions.HTTPError as errh:
        print(f"  Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"  Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"  Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"  Something Else Went Wrong: {err}")
    return None

# --- POST request to create a new post ---
def create_post(title, body, user_id):
    print("\\n--- POST Request to /posts ---")
    new_post_payload = {
        "title": title,
        "body": body,
        "userId": user_id
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    try:
        response = requests.post(f"{BASE_URL}/posts", data=json.dumps(new_post_payload), headers=headers, timeout=5)
        response.raise_for_status()

        print(f"Status Code: {response.status_code}") # Should be 201 Created
        created_post_data = response.json()
        print(f"Created Post ID: {created_post_data.get('id')}")
        print(f"Created Post Title: {created_post_data.get('title')}")
        return created_post_data
    except requests.exceptions.RequestException as e:
        print(f"  POST request failed: {e}")
    return None

if __name__ == "__main__":
    get_post(1)
    get_post(9999) # Example of a resource not found (should trigger 404)

    created_post = create_post("My New Post", "This is the body of my amazing new post.", 101)
    if created_post:
        print(f"Successfully created post with ID: {created_post.get('id')}")
