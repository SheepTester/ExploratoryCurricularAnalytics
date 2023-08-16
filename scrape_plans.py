import json
from typing import Any, Hashable, List, Literal, Optional, TypedDict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from util import CsvWriter


HOST = "https://plans.ucsd.edu/controller.php?"


class PlanDepartment(TypedDict):
    code: str
    description: str
    "Same as `code`."
    name: str


class PlanCollege(TypedDict):
    code: str
    name: str


class LoadSearchControlsResponse(TypedDict):
    years: List[int]
    departments: List[PlanDepartment]
    "Alphabetized by name rather than code."
    colleges: List[PlanCollege]
    "Ordered by founding date."


class PlanMajor(TypedDict):
    """
    A major in a department. Note that the API returns all majors that ever
    existed, even historical or future ones.

    A major is considered available if the major has a plan available for the
    specified `year` and `college`. If either of these aren't specified, all
    majors are considered unavailable.
    """

    major: str
    "Of the format `<name>* (<code>)`. `*` is present if the plan is available."
    major_code: str
    "`NONE` if plan is not available."


LoadMajorsResponse = List[PlanMajor]


class PlanCourse(TypedDict):
    course_id: int
    plan_id: int
    course_name: str
    units: str
    "A float represented as a string, eg `4.0`."
    course_type: Literal["COLLEGE", "DEPARTMENT"]
    year_taken: int
    quarter_taken: int
    display_order: int
    ge_major_overlap: bool


class PlanComment(TypedDict):
    comment_id: int
    plan_id: int
    author: str
    comment_text: str
    "HTML."
    comment_type: Literal["COLLEGE", "DEPARTMENT"]
    last_modified: str
    "Format: `YYYY-MM-DD HH:MM:SS`. Probably in Pacific Time."


class LoadPlanResponse(TypedDict):
    planId: int
    courses: List[List[List[PlanCourse]]]
    comments: List[PlanComment]
    college_code: str
    college_name: str
    college_url: str
    major_code: str
    department: str
    start_year: int
    department_url: str
    "May be `NONE`."
    major_title: str
    finalized_time: str
    "Format: `YYYY-MM-DD HH:MM:SS`. Probably in Pacific Time."
    plan_length: int
    "Number of years in plan."


LoadPlansResponse = List[LoadPlanResponse]


class PlansApi:
    @staticmethod
    def _request(action: str, **kwargs: Hashable) -> Any:
        with urlopen(
            Request(
                HOST + urlencode({"action": action, **kwargs}),
                headers={"Accept": "application/json"},
            )
        ) as response:
            return json.load(response)

    @staticmethod
    def load_search_controls() -> LoadSearchControlsResponse:
        return PlansApi._request("LoadSearchControls")

    @staticmethod
    def load_all_majors(department: str = "") -> LoadMajorsResponse:
        """
        If `department` is omitted, the API returns majors for all departments.
        NOTE: All majors will be considered unavailable.
        """
        return PlansApi._request("LoadMajors", department=department)

    @staticmethod
    def load_majors(
        year: int, college: str, department: str = ""
    ) -> LoadMajorsResponse:
        """
        If `department` is omitted, the API returns majors for all departments.
        The majors listed by this API request is the same regardless of year and
        college. However, majors don't have plans for every year-college
        combination, so some majors will be considered unavailable.
        """
        return PlansApi._request(
            "LoadMajors", year=year, college=college, department=department
        )

    @staticmethod
    def load_plan(plan_id: int) -> LoadPlanResponse:
        return PlansApi._request("LoadPlan", planId=plan_id)

    @staticmethod
    def load_plans(year: int, major: str, college: str) -> LoadPlansResponse:
        return PlansApi._request("LoadPlans", year=year, major=major, college=college)


# Potentially could've included "Plan Length," but our provided data do not
# include this.
HEADER = [
    "Department",
    "Major",
    "College",
    "Course",
    "Units",
    "Course Type",
    "GE/Major Overlap",
    "Start Year",
    "Year Taken",
    "Quarter Taken",
    "Term Taken",
]


def _display_term(start_year: int, course: PlanCourse) -> str:
    quarter_taken = course["quarter_taken"]
    year_taken = course["year_taken"]
    quarter: str
    if quarter_taken == 1:
        quarter = "FA"
        year_taken -= 1
    elif quarter_taken == 2:
        quarter = "WI"
    elif quarter_taken == 3:
        quarter = "SP"
    elif quarter_taken == 4:
        quarter = "SU"
    else:
        return "ERROR"
    return quarter + str(start_year + year_taken)[-2:]


def plans_to_csv(
    year: int, writer: Optional[CsvWriter] = None, header: bool = True
) -> CsvWriter:
    if writer is None:
        writer = CsvWriter(len(HEADER))
    if header:
        writer.row(*HEADER)
    search_controls = PlansApi.load_search_controls()
    for college in search_controls["colleges"]:
        major_codes = sorted(
            major["major_code"]
            for major in PlansApi.load_majors(year, college["code"])
            if major["major_code"] != "NONE"
        )
        for major in major_codes:
            for plan in PlansApi.load_plans(year, major, college["code"]):
                for plan_year in plan["courses"]:
                    for term in plan_year:
                        for course in term:
                            writer.row(
                                plan["department"],
                                major,
                                college["code"],
                                # `units` is a string, but printing it
                                # directly into the CSV is fine
                                course["units"],
                                course["course_type"],
                                "Y" if course["ge_major_overlap"] else "N",
                                str(year),
                                str(course["year_taken"]),
                                str(course["quarter_taken"]),
                                _display_term(year, course),
                            )
    return writer


if __name__ == "__main__":
    import sys

    plans_to_csv(2023, CsvWriter(len(HEADER), sys.stdout))
