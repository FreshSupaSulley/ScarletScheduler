from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from osu import fetch_osu_api
from rmp import fetch_rmp

app = FastAPI(
    title="Course Intelligence API",
    version="1.0.0"
)

# Request / Response Models
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

# THE tool calling endpoint
@app.post("/tools/getCourseProfessorData", response_model=CourseResponse)
async def get_course_professor_data(req: CourseRequest):
    course_code = req.courseCode

    # Fetch OSU API
    professors = await fetch_osu_api(course_code)

    # Enrich with RMP data
    enriched = []

    for prof in professors:
        rmp_data = await fetch_rmp(course_code, prof["name"])

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

# Sanity check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
