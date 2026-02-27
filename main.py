from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import httpx
import asyncio

app = FastAPI(
    title="Course Intelligence API",
    version="1.0.0"
)

# -------------------------
# Request / Response Models
# -------------------------

class CourseRequest(BaseModel):
    courseCode: str


class Professor(BaseModel):
    name: str
    section: str
    rating: float
    reviewCount: int
    difficulty: float


class CourseResponse(BaseModel):
    courseCode: str
    professors: List[Professor]


# -------------------------
# Mock External Calls
# Replace these with real logic
# -------------------------

async def fetch_osu_api(course_code: str):
    """
    Replace with real OSU Mobile API call.
    """
    # Example mock data
    return [
        {"name": "Dr. Jane Smith", "section": "001"},
        {"name": "Dr. John Doe", "section": "002"},
    ]


async def fetch_rmp(prof_name: str):
    """
    Replace with real RateMyProfessor scraping logic.
    """
    # Mock data
    return {
        "rating": 4.5,
        "reviewCount": 120,
        "difficulty": 3.2,
    }


# -------------------------
# Tool Endpoint
# -------------------------

@app.post("/tools/getCourseProfessorData", response_model=CourseResponse)
async def get_course_professor_data(req: CourseRequest):
    course_code = req.courseCode

    # 1️⃣ Fetch OSU API
    professors = await fetch_osu_api(course_code)

    # 2️⃣ Enrich with RMP data
    enriched = []

    for prof in professors:
        rmp_data = await fetch_rmp(prof["name"])

        enriched.append(
            Professor(
                name=prof["name"],
                section=prof["section"],
                rating=rmp_data["rating"],
                reviewCount=rmp_data["reviewCount"],
                difficulty=rmp_data["difficulty"],
            )
        )

    return CourseResponse(
        courseCode=course_code,
        professors=enriched
    )


# -------------------------
# Health Check (Optional)
# -------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}
