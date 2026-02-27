import httpx

async def fetch_osu_api(course_code: str):
    """
    Replace with real OSU Mobile API call.
    """
    response = httpx.get(f"https://content.osu.edu/v2/classes/search?q={course_code}")
    response.raise_for_status() # in case it shits on us
    print(response)
    # Example mock data
    return [
        {"name": "Dr. Jane Smith", "section": "001"},
        {"name": "Dr. John Doe", "section": "002"},
    ]
