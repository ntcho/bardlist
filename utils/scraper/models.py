import re


class Schedule:
    def __init__(self, location, day_of_week, start_time, end_time, type) -> None:
        self.location = location
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.type = type

    @classmethod
    def full(self, schedule_string: str, schedule_type: str = "Primary"):
        # schedule_string format = "Tue  Thurs    10:10 AM – 11:30 AM Olin 203"

        matches = re.search(
            "(.*?)(\d{1,2}:\d{1,2})\s*?([AP]M)\s*?.\s*?(\d{1,2}:\d{1,2})\s*?([AP]M)\s*(.*)",
            schedule_string,
        )
        if matches is None:
            return None

        day_of_week = matches.group(1).split()  # split with whitespace
        start_time = matches.group(2)
        start_am_pm = matches.group(3)
        end_time = matches.group(4)
        end_am_pm = matches.group(5)
        location = matches.group(6)

        return Schedule(
            location,
            day_of_week,
            self.convert_to_24_hour(self, start_time, start_am_pm),
            self.convert_to_24_hour(self, end_time, end_am_pm),
            schedule_type,
        )

    @classmethod
    def simple(self, m, t, w, th, f, sat, sun, start, end):
        day_of_week = []

        if m == "M":
            day_of_week.append("Mon")
        if t == "T":
            day_of_week.append("Tue")
        if w == "W":
            day_of_week.append("Wed")
        if th == "Th":
            day_of_week.append("Thurs")
        if f == "F":
            day_of_week.append("Fri")
        if sat == "Sat":
            day_of_week.append("Sat")
        if sun == "Sun":
            day_of_week.append("Sun")

        try:
            return Schedule(
                location="",
                day_of_week=day_of_week,
                start_time=self.convert_to_24_hour(
                    self, start.split()[0], start.split()[1]
                ),
                end_time=self.convert_to_24_hour(self, end.split()[0], end.split()[1]),
                type="",
            )
        except:
            pass

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
        self.title = "" if title is None else title
        self.course_number = "" if course_number is None else course_number
        self.crn_number = "" if crn_number is None else crn_number
        self.professor = "" if professor is None else professor
        self.class_cap = "" if class_cap is None else class_cap
        self.credits = "" if credits is None else credits
        self.description = (
            "" if description is None else description.replace('"', "“")
        )  # replace quotes to curly quotes
        self.distributional_area = (
            ""
            if distributional_area is None
            else re.findall("([A-Z+]{2,3})", distributional_area)
        )  # split distributional area into list of acronyms
        self.crosslists = "" if crosslists is None else crosslists
        self.program = "" if program is None else program
        self.source = "" if source is None else source
        self.schedules = [] if schedules is None else schedules

    def __str__(self) -> str:
        # CSV colums ->
        # course_number, title, professor, credits, class_cap, primary_schedule, secondary_schedule,
        # distributional_area, crosslists, additional_schedule, description,
        # crn_number, program, source

        # schedule column -> day_of_week, start_time, end_time, location
        primary_schedule = self.schedules[0] if self.schedules[0] is not None else ",,,"
        secondary_schedule = self.schedules[1] if len(self.schedules) == 2 else None
        additional_schedule = self.schedules[1:] if len(self.schedules) > 2 else None

        primary_schedule_str = str(primary_schedule)
        secondary_schedule_str = (
            str(secondary_schedule) if secondary_schedule is not None else ",,,"
        )
        additional_schedule_str = ""
        try:
            additional_schedule_str = (
                ", ".join([s.brief_str() for s in additional_schedule])
                if additional_schedule is not None
                else ""
            )
        except:
            pass

        distributional_area_str = ", ".join(self.distributional_area)

        quote = lambda s: f'"{s}"'

        # Turn into CSV format
        s = ",".join(
            [
                self.course_number,
                quote(self.title),
                quote(self.professor),
                self.credits,
                self.class_cap,
                primary_schedule_str,
                secondary_schedule_str,
                quote(distributional_area_str),
                quote(self.crosslists),
                quote(additional_schedule_str),
                quote(self.description),
                self.crn_number,
                self.program,
                self.source,
            ]
        )

        if "" in [
            self.course_number,
            self.title,
            self.credits,
            self.crn_number,
        ]:
            print("Error: Skipped", re.sub("\s+", " ", " ".join(s.splitlines())))
            return ""

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


class CourseList:
    def __init__(self) -> None:
        self.courses = {}
        self.record = {"add": 0, "merge": 0}

    def add(self, course: Course) -> None:
        self.record["add"] += 1

        if course.crn_number in self.courses:
            # TODO: check whether this removes all duplicates
            self.courses[course.crn_number].merge(course)
            self.record["merge"] += 1
        else:
            self.courses[course.crn_number] = course

    def get_record(self) -> str:
        return f"{len(self.courses)} courses ({self.record['add']} added, {self.record['merge']} merged)"

    def __getitem__(self, key: str) -> Course:
        return self.courses[key]

    def __contains__(self, key: str) -> bool:
        return key in self.courses

    def __iter__(self) -> Course:
        for key in self.courses:
            yield key
