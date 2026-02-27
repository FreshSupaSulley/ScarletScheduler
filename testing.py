import asyncio
from rmp import fetch_rmp

async def main():
    course_code = "CSE2431"
    prof_name = "Adam Champion"
    result = await fetch_rmp(course_code, prof_name)
    
    # Write to file with formatted output
    with open("rmp_results.txt", "w", encoding="utf-8") as f:
        if result:
            f.write(f"Professor: {result['name']}\n")
            if course_code:
                f.write(f"Course Filter: {course_code}\n")
            f.write(f"Rating: {result['rating']}/5.0\n")
            f.write(f"Difficulty: {result['difficulty']}/5.0\n")
            f.write(f"Would Take Again: {result['wouldTakeAgainPercent']}%\n")
            f.write(f"Total Reviews: {result['reviewCount']}\n")
            f.write(f"Filtered Reviews Shown: {len(result['reviews'])}\n")
            f.write("\n" + "="*80 + "\n")
            f.write("REVIEWS:\n")
            f.write("="*80 + "\n\n")
            
            for i, review in enumerate(result['reviews'], 1):
                f.write(f"Review #{i}\n")
                f.write(f"Course: {review['course']}\n")
                f.write(f"Quality: {review['quality']}/5\n")
                f.write(f"Difficulty: {review['difficulty']}/5\n")
                f.write(f"Date: {review['date']}\n")
                f.write(f"Comment: {review['comment']}\n")
                f.write("-"*80 + "\n\n")
        else:
            f.write("No results found.\n")
    
    print(f"Results written to rmp_results.txt")

if __name__ == "__main__":
    asyncio.run(main())
    