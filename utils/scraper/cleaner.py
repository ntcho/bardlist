import course_csv
from models import CourseList

# Entire dictionary of courses
courses = CourseList()

course_csv.read_scrape("fall2023_scrape.csv", courses, verbose=True)
course_csv.read_table("fall2023_table.csv", courses, verbose=True)

course_csv.write("fall2023_results.csv", courses)
print(courses.get_record())
