"""
python3 dump_graphs.py 2022 json
python3 dump_graphs.py 2022 html > reports/output/plan-editor-index.html
"""


import json
import re
import sys
from typing import Dict, List, Tuple
from departments import departments, dept_schools
from output import MajorOutput
from parse import major_codes, major_plans
from university import university


def render_plan_json(year: int) -> None:
    plan_jsons: Dict[str, str] = {}
    for year in range(2015, 2050):
        all_plans = major_plans(year)
        if all_plans == {}:
            break
        for major_code, major_plan in all_plans.items():
            output = MajorOutput(major_plan)
            for college in university.college_codes:
                if college in major_plan.colleges:
                    plan_jsons[f"{year}.{major_code}.{college}"] = re.sub(
                        r",*\n",
                        "",
                        output.output(college).replace("\r\n", "\n"),
                    )
    json.dump(plan_jsons, sys.stdout, separators=(",", ":"))


def render_plan_urls(year: int) -> None:
    qs_by_dept: Dict[str, Dict[str, Dict[str, Dict[int, List[Tuple[str, str]]]]]] = {}
    years: List[int] = []
    for year in range(2015, 2050):
        all_plans = major_plans(year)
        if all_plans == {}:
            break
        years.insert(0, year)
        for major_code, major_plan in all_plans.items():
            department = departments[major_codes()[major_code].department]
            school = dept_schools.get(major_codes()[major_code].department) or ""
            if school not in qs_by_dept:
                qs_by_dept[school] = {}
            if department not in qs_by_dept[school]:
                qs_by_dept[school][department] = {}
            if major_code not in qs_by_dept[school][department]:
                qs_by_dept[school][department][major_code] = {}
            if year not in qs_by_dept[school][department][major_code]:
                qs_by_dept[school][department][major_code][year] = []
            for college in university.college_codes:
                if college in major_plan.colleges:
                    qs_by_dept[school][department][major_code][year].append(
                        (college, f"?plan={year}.{major_code}.{college}")
                    )
    print("<script>")
    print("const plan = new URL(window.location.href).searchParams.get('plan')")
    print("if (plan) {")
    print("  window.stop()")
    print("  fetch('./plan-graph-index.json')")
    print("    .then(r => r.json())")
    print(
        "    .then(({ [plan]: csv }) => window.location.replace(`./graph-demo.html?defaults=ca#${encodeURIComponent(csv)}`))"
    )
    print("}</script>")
    print("<table><tr><th>School</th><th>Department</th><th>Major</th>")
    for year in years:
        print(f"<th>{year}</th>")
    print("</tr>")
    for school, depts in sorted(qs_by_dept.items(), key=lambda entry: entry[0]):
        major_count = sum(len(majors) for majors in depts.values())
        print(f'<tr><th scole="col" rowspan="{major_count}">{school}</th>')
        for i, (department, majors) in enumerate(
            sorted(depts.items(), key=lambda entry: entry[0])
        ):
            if i > 0:
                print("<tr>")
            print(f'<th scole="col" rowspan="{len(majors)}">{department}</th>')
            for j, (major_code, history) in enumerate(
                sorted(majors.items(), key=lambda entry: entry[0])
            ):
                if j > 0:
                    print("<tr>")
                print(f"<td><strong>{major_code}</strong>", end="")
                major_name = major_codes()[major_code].name
                if major_name:
                    print(f": {major_name}")
                print("</td>")
                for year in years:
                    if year not in history:
                        print("<td></td>")
                        continue
                    print("<td>")
                    for college, path in history[year]:
                        print(
                            f'<a href="{path}">{university.college_names[college]}</a><br>'
                        )
                    print("</td>")
                print("</tr>")
    print("</table>")


if __name__ == "__main__":
    if sys.argv[2] == "json":
        render_plan_json(int(sys.argv[1]))
    else:
        render_plan_urls(int(sys.argv[1]))
