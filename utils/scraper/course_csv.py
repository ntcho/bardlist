import re
import traceback
import pandas as pd

from models import Schedule, Course, CourseList


def read_scrape(
    filename: str = "scrape.csv", courses: CourseList = None, verbose: bool = False
):
    if courses is None:
        raise ValueError

    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(filename, dtype=str)

    # Fill NaN values with empty string
    df = df.fillna("")

    # Iterate over the rows of the dataframe
    for index, row in df.iterrows():
        try:
            if row["title"] == "null":
                raise ValueError

            # Default properties
            title = row["title"]
            course_number = row["number"]
            crn_number = row["crn"]
            professor = row["professor"]
            class_cap = row["class_cap"]
            credits = row["credits"]
            description = row["description"]
            program = row["programs"]
            source = row["programs-href"]
            schedules = [Schedule.full(row["schedule"].replace("\n", " "))]

            # Optional properties
            distributional_area = None
            crosslists = None

            for i in range(1, 5):
                # property types are one of the following:
                # - "Dist*": Distribution area
                # - "Lab*":
                # - "Screen*":
                # - "Cross*":
                # - "null": Additional Location & Time

                try:
                    type = row[f"property_{i}_type"]
                    value = row[f"property_{i}_value"].replace("\n", " ")

                    # Distribution area
                    if type.startswith("Dist"):
                        # TODO: split into different areas
                        distributional_area = value
                        continue

                    # Crosslists
                    if type.startswith("Cross"):
                        crosslists = value
                        continue

                    # Probably schedule (contains AM or PM)
                    if bool(re.search("[AP]M", value)):
                        if type == "null":
                            type = "Additional"

                        schedules.append(Schedule.full(value, type))
                        continue
                except:
                    continue

            courses.add(
                Course(
                    title,
                    course_number,
                    crn_number,
                    professor,
                    class_cap,
                    credits,
                    description,
                    distributional_area,
                    crosslists,
                    program,
                    source,
                    schedules,
                )
            )

        except:
            if verbose:
                print(traceback.format_exc())


def read_table(
    filename: str = "scrape.csv", courses: CourseList = None, verbose: bool = False
):
    if courses is None:
        raise ValueError

    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(filename, dtype=str, sep="\t")

    # Fill NaN values with empty string
    df = df.fillna("")

    # List of course numbers that has been inserted
    insert_record = []

    # Iterate over the rows of the dataframe
    for index, row in df.iterrows():
        try:
            # Default properties
            course_number = " ".join([row["SUBJ"], row["CRSE"], row["SECTION"]])
            crn_number = row["CRN"]
            title = row["TITLE"]
            credits = row["CREDITS"]
            professor = row["PROFESSOR"]
            class_cap = row["CLASS_CAP"]
            schedule = Schedule.simple(
                row["M"],
                row["T"],
                row["W"],
                row["TH"],
                row["F"],
                row["SAT"],
                row["SUN"],
                row["START"],
                row["END"],
            )

            # Additional schedule or missing professor information
            if row[6] == "and":
                previous_course = courses[insert_record[-1]]
                
                if schedule is not None:
                    previous_course.schedules.append(schedule)

                if previous_course.professor == "":
                    previous_course.professor = professor
                continue

            # Optional properties
            distributional_area = " ".join([row["DISTRIBUTION"], row["DJ"]])

            course = Course(
                title,
                course_number,
                crn_number,
                professor,
                class_cap,
                credits,
                None,
                distributional_area,
                None,
                None,
                None,
                [schedule],
            )

            courses.add(course)
            insert_record.append(crn_number)

        except:
            if verbose:
                print(traceback.format_exc())


def write(filename="result.csv", courses: CourseList = None, verbose=False):
    if courses is None:
        raise ValueError

    with open(filename, "w") as file:
        # write CSV header
        file.write(
            ",".join(
                [
                    "course_number",
                    "course_title",
                    "professor",
                    "credits",
                    "class_cap",
                    "primary_schedule_day",
                    "primary_schedule_start_time",
                    "primary_schedule_end_time",
                    "primary_schedule_location",
                    "secondary_schedule_day",
                    "secondary_schedule_start_time",
                    "secondary_schedule_end_time",
                    "secondary_schedule_location",
                    "distributional_area",
                    "crosslists",
                    "additional_schedule",
                    "description",
                    "crn_number",
                    "program",
                    "source",
                ]
            )
            + "\n"
        )
        for crn_number in courses:
            line = str(courses[crn_number])
            
            if len(line) > 1:
                file.write(line + "\n")

            if verbose:
                print(line)
