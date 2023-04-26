import re
import traceback
import pandas as pd


class Schedule:
    def __init__(self, schedule_string: str, schedule_type: str = "Primary") -> None:
        # schedule_string format = "Tue  Thurs    10:10 AM – 11:30 AM Olin 203"

        matches = re.search(
            "(.*?)(\d{1,2}:\d{1,2})\s*?([AP]M)\s*?.\s*?(\d{1,2}:\d{1,2})\s*?([AP]M)\s*(.*)",
            schedule_string,
        )
        day_of_week = matches.group(1).split()  # split with whitespace
        start_time = matches.group(2)
        start_am_pm = matches.group(3)
        end_time = matches.group(4)
        end_am_pm = matches.group(5)
        location = matches.group(6)

        self.location = location
        self.day_of_week = day_of_week
        self.start_time = self.convert_to_24_hour(start_time, start_am_pm)
        self.end_time = self.convert_to_24_hour(end_time, end_am_pm)
        self.type = schedule_type

    def convert_to_24_hour(self, time: str, am_pm: str) -> str:
        if am_pm == "PM":
            hour, min = time.split(":")
            if int(hour) < 12:  # edge case for 12pm
                hour = str(int(hour) + 12)
            return hour + ":" + min
        return time

    def __str__(self) -> str:
        # day_of_week, start_time, end_time, location
        return f"{' '.join(self.day_of_week)}, {self.start_time}, {self.end_time}, \"{self.location}\""

    def brief_str(self) -> str:
        # day_of_week start_time-end_time location
        return f"{' '.join(self.day_of_week)} {self.start_time}-{self.end_time} {self.location}"


class Course:
    def __init__(
        self,
        title: str,
        course_number: str,
        crn_number: str,
        professor: str,
        class_cap: int,
        credits: int,
        description: str,
        distributional_area: str,
        crosslists: str,
        program: str,
        source: str,
        schedules: list[Schedule],
    ) -> None:
        self.title = title
        self.course_number = course_number
        self.crn_number = crn_number
        self.professor = professor
        self.class_cap = class_cap
        self.credits = credits
        self.description = description.replace(
            '"', "“"
        )  # replace quotes to curly quotes
        self.distributional_area = distributional_area
        self.crosslists = crosslists
        self.program = program
        self.source = source
        self.schedules = schedules

    def __str__(self) -> str:
        # CSV colums ->
        # course_number, title, professor, credits, class_cap, primary_schedule, secondary_schedule,
        # distributional_area, crosslists, additional_schedule, description,
        # crn_number, program, source

        # schedule column -> day_of_week, start_time, end_time, location
        primary_schedule = self.schedules[0]
        secondary_schedule = self.schedules[1] if len(self.schedules) == 2 else None
        additional_schedule = self.schedules[1:] if len(self.schedules) > 2 else None

        primary_schedule_str = str(primary_schedule)
        secondary_schedule_str = (
            str(secondary_schedule) if secondary_schedule is not None else ",,,"
        )
        additional_schedule_str = (
            ", ".join([s.brief_str() for s in additional_schedule])
            if additional_schedule is not None
            else ""
        )

        s = f'{self.course_number},"{self.title}","{self.professor}",{self.credits},{self.class_cap},{primary_schedule_str},{secondary_schedule_str},"{self.distributional_area}","{self.crosslists}","{additional_schedule_str}","{self.description}",{self.crn_number},"{self.program}",{self.source}'

        return re.sub("\s+", " ", " ".join(s.splitlines()))

    def longer(self, a, b):
        try:
            return a if len(a) > len(b) else b
        except:
            return a

    def merge(self, other):
        self.description = self.longer(self.description, other.description)
        self.distributional_area = self.longer(
            self.distributional_area, other.distributional_area
        )
        self.crosslists = self.longer(self.crosslists, other.crosslists)

        return self


# Entire dictionary of courses
courses = {}

# Read the CSV file into a pandas dataframe
df = pd.read_csv("scrape.csv", dtype=str)

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
        schedules = [Schedule(row["schedule"].replace("\n", " "))]

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

                    schedules.append(Schedule(value, type))
                    continue
            except:
                continue

        course = Course(
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

        if course_number in courses:
            # TODO: check whether this removes all duplicates
            courses[course_number].merge(course)
        else:
            courses[course_number] = course

    except:
        print(traceback.format_exc())

with open("scrape_clean.csv", "w") as file:
    file.write(
        f"course_number,course_title,professor,credits,class_cap,primary_schedule_day,primary_schedule_start_time,primary_schedule_end_time,primary_schedule_location,secondary_schedule_day,secondary_schedule_start_time,secondary_schedule_end_time,secondary_schedule_location,distributional_area,crosslists,additional_schedule,description,crn_number,program,source\n"
    )
    for key in courses:
        line = str(courses[key])

        file.write(line + "\n")
        # print(line)
