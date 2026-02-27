import httpx
from datetime import date

async def fetch_osu_api(subject: str, course_code: str):
    """
    Replace with real OSU Mobile API call.
    """
    # Fetch
    response = httpx.get(f"https://content.osu.edu/v2/classes/search?q={course_code}")
    response.raise_for_status() # in case it shits on us
    courses = response.json()['data']['courses']

    # Convert to string to make endswith() happy
    year = f"{date.today().year}"

    # Top level "course" object is filtered by course # (2221) and subject (CSE)
    # We are also for PoC purposes only doing Columbus campus (not because I went to Newark and I am spiting them)
    filtered_top_level = [c['sections'] for c in courses if c['course']['term'].endswith(year) and c['course']['subject'] == subject and c['course']['catalogNumber'] == course_code and c['course']['campusCode'] == 'COL']
    filtered_sections = []

    for section_list in filtered_top_level:
        for section in section_list:
            meetings = section.get('meetings', [])
            # Only consider sections with exactly one meeting
            # In the future, if we had shark tank money, this wouldn't be a concern
            if len(meetings) != 1:
                continue
            meeting = meetings[0]
            # Get the first valid instructor (displayName truthy)
            instructors = meeting.get('instructors', [])
            valid_instructors = [i for i in instructors if i.get('displayName')]
            if not valid_instructors:
                continue
            instructor = valid_instructors[0]  # take the first one
            # Append the filtered section
            filtered_sections.append({
                "instructor": instructor.get('displayName'),
                "section": section['section'],  # section id or name
                "building": meeting['buildingDescription'],
                # Time
                "startTime": meeting['startTime'],
                "endTime": meeting['endTime'],
                # Days
                "days": "".join([
                    d for d, key in [
                        ("M", "monday"),
                        ("Tu", "tuesday"),
                        ("W", "wednesday"),
                        ("Th", "thursday"),
                        ("F", "friday"),
                        ("Sa", "saturday"),
                        ("Su", "sunday"),
                    ]
                    if meeting.get(key)
                ])
            })

    # Example mock data
    return filtered_sections
