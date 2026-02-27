import httpx
from datetime import date

async def fetch_osu_api(subject: str, course_code: str):
    """
    Replace with real OSU Mobile API call.
    """
    print("Got subject", subject, "and course code", course_code)
    # Fetch
    response = httpx.get(f"https://content.osu.edu/v2/classes/search?q={course_code}")
    response.raise_for_status() # in case it shits on us
    courses = response.json()['data']['courses']

    # Convert to string to make endswith() happy
    year = f"{date.today().year}"
    semester = "Spring" # for PoC

    # Top level "course" object is filtered by course # (2221) and subject (CSE)
    # We are also for PoC purposes only doing Columbus campus (not because I went to Newark and I am spiting them)
    print("Got back", len(courses), "raw courses")
    filtered_top_level = [c['sections'] for c in courses if c['course']['term'] == f"{semester} {year}" and c['course']['subject'] == subject and c['course']['catalogNumber'] == course_code and c['course']['campusCode'] == 'COL']
    print("Filtered down to", len(filtered_top_level), "courses")

    # Collect professors as the top level JSON object which points to arrays
    professors = {}

    for section_list in filtered_top_level:
        for section in section_list:
            meetings = section.get('meetings', [])

            if len(meetings) != 1:
                continue

            meeting = meetings[0]

            instructors = meeting.get('instructors', [])
            valid_instructors = [i for i in instructors if i.get('displayName')]
            if not valid_instructors:
                continue

            instructor_name = valid_instructors[0]['displayName']

            if instructor_name not in professors:
                professors[instructor_name] = []

            days = "".join([
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
            
            # Yes this can happen apparently
            # ^ nvm this probably means async
            # if not days:
            #     continue
            
            professors[instructor_name].append({
                "section": section['section'],
                "building": meeting['buildingDescription'],
                "startTime": meeting['startTime'],
                "endTime": meeting['endTime'],
                "days": days
            })

    # Example mock data
    return professors
