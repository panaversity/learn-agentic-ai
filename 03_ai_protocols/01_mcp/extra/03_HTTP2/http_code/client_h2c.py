import httpx
import asyncio

SERVER_URL_H2C = "http://localhost:8000" # Note: http:// for h2c

async def main():
    # For h2c, http2=True is essential. httpx will attempt the h2c upgrade.
    async with httpx.AsyncClient(http2=True, http1=False) as client:
        print(f"--- Testing GET request to {SERVER_URL_H2C}/ (expecting h2c) ---")
        try:
            response_get = await client.get(f"{SERVER_URL_H2C}/")
            response_get.raise_for_status()
            print(f"Status: {response_get.status_code}, HTTP Version: {response_get.http_version}")
            print(f"Response JSON:\n{response_get.json()}\n")
        except Exception as e:
            print(f"GET request to h2c server failed: {type(e).__name__} - {e}")

        print(f"--- Testing POST request to {SERVER_URL_H2C}/data (expecting h2c) ---")
        try:
            post_payload = {"agent_id": "007-h2c", "task": "observe_cleartext"}
            response_post = await client.post(f"{SERVER_URL_H2C}/data", json=post_payload)
            response_post.raise_for_status()
            print(f"Status: {response_post.status_code}, HTTP Version: {response_post.http_version}")
            print(f"Response JSON:\n{response_post.json()}\n")
        except Exception as e:
            print(f"POST request to h2c server failed: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(main())