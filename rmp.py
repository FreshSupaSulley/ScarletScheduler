import httpx

SCHOOL_ID = "724"  # Ohio State

async def fetch_rmp(courseCode: str, prof_name: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Authorization": "Basic dGVzdDp0ZXN0"
    }

    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:

        search_url = "https://www.ratemyprofessors.com/graphql"

        search_query = {
            "query": """query TeacherSearchQuery($text: String!, $schoolID: ID!) {
                newSearch {
                    teachers(query: {text: $text, schoolID: $schoolID}) {
                        edges {
                            node {
                                id
                                firstName
                                lastName
                                avgRating
                                numRatings
                                avgDifficulty
                                wouldTakeAgainPercent
                            }
                        }
                    }
                }
            }""",
            "variables": {
                "text": prof_name,
                "schoolID": "U2Nob29sLTcyNA=="
            }
        }

        search_resp = await client.post(search_url, json=search_query)
        search_data = search_resp.json()

        teachers = search_data.get("data", {}).get("newSearch", {}).get("teachers", {}).get("edges", [])
        if not teachers:
            return None

        prof = teachers[0]["node"]
        prof_id = prof["id"]

        rating = float(prof.get("avgRating", 0))
        review_count = int(prof.get("numRatings", 0))

        avg_difficulty = (
            float(prof["avgDifficulty"])
            if prof.get("avgDifficulty") is not None
            else None
        )

        would_take_again_percent = (
            float(prof["wouldTakeAgainPercent"])
            if prof.get("wouldTakeAgainPercent") is not None
            else None
        )

        # Fetch first 20 reviews (filtered by course code if provided)
        if courseCode:
            review_query = {
                "query": """query RatingsPageQuery($id: ID!, $courseCode: String!) {
                    node(id: $id) {
                        ... on Teacher {
                            ratings(first: 20, courseFilter: $courseCode) {
                                edges {
                                    node {
                                        class
                                        qualityRating
                                        difficultyRating
                                        date
                                        comment
                                        wouldTakeAgain
                                    }
                                }
                            }
                        }
                    }
                }""",
                "variables": {"id": prof_id, "courseCode": courseCode}
            }
        else:
            review_query = {
                "query": """query RatingsPageQuery($id: ID!) {
                    node(id: $id) {
                        ... on Teacher {
                            ratings(first: 20) {
                                edges {
                                    node {
                                        class
                                        qualityRating
                                        difficultyRating
                                        date
                                        comment
                                        wouldTakeAgain
                                    }
                                }
                            }
                        }
                    }
                }""",
                "variables": {"id": prof_id}
            }

        review_resp = await client.post(search_url, json=review_query)
        review_data = review_resp.json()

        raw_reviews = review_data.get("data", {}).get("node", {}).get("ratings", {}).get("edges", [])

        reviews = [
            {
                "course": r["node"].get("class"),
                "quality": r["node"].get("qualityRating"),
                "difficulty": r["node"].get("difficultyRating"),
                "date": r["node"].get("date"),
                "comment": r["node"].get("comment"),
            }
            for r in raw_reviews
        ]

        return {
            "name": f"{prof.get('firstName')} {prof.get('lastName')}",
            "rating": rating,
            "reviewCount": review_count,
            "difficulty": avg_difficulty,
            "wouldTakeAgainPercent": would_take_again_percent,
            "reviews": reviews
        }
