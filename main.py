from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from osu import fetch_osu_api
from rmp import fetch_rmp

app = FastAPI(
    title="Course Intelligence API",
    version="1.0.0"
)

# Request / Response Models
class CourseRequest(BaseModel):
    subject: str
    courseCode: str

class Section(BaseModel):
    section: str
    building: str
    startTime: str
    endTime: str
    days: str

class Professor(BaseModel):
    name: str
    sections: List[Section]
    rating: float # how you rate the guy
    difficulty: float # how hard the prof is
    reviewCount: int
    reviews: Optional[List[str]]

class CourseResponse(BaseModel):
    courseCode: str
    professors: List[Professor]

# THE tool calling endpoint
@app.post("/tools/getCourseProfessorData", response_model=CourseResponse)
async def get_course_professor_data(req: CourseRequest):
    course_code = req.courseCode

    # Fetch sections from OSU Mobile App API
    professors = await fetch_osu_api(req.subject, course_code)
    # Enrich with RMP data
    enriched = []

    for prof in professors:
        rmp_data = await fetch_rmp(prof)
        if not rmp_data:
            continue
        print("RMP'ing", prof)
        enriched.append(
            Professor(
                name=prof,
                sections=professors[prof],
                rating=rmp_data["rating"],
                reviewCount=rmp_data["reviewCount"],
                difficulty=rmp_data["difficulty"],
                reviews=rmp_data["reviews"]
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
