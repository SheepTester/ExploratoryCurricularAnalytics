/** @jsxImportSource preact */
/// <reference no-default-lib="true"/>
/// <reference lib="dom" />
/// <reference lib="deno.ns" />

import { CourseCode, Prereqs } from '../../util/Prereqs.ts'
import { Course } from '../types.ts'

export type CourseOptionsProps = {
  prereqs: Prereqs
  course: Course
  onCourse: (course: Course) => void
  onRemove: () => void
  pastCourses: CourseCode[]
  concurrentCourses: CourseCode[]
}
export function CourseOptions ({
  prereqs,
  course,
  onCourse,
  onRemove,
  pastCourses,
  concurrentCourses
}: CourseOptionsProps) {
  return (
    <div class='options-wrapper'>
      <div class='options-body'>
        <label class='toggle-wrapper'>
          <input
            type='checkbox'
            checked={course.requirement.major}
            onInput={e =>
              onCourse({
                ...course,
                requirement: {
                  ...course.requirement,
                  major: e.currentTarget.checked
                }
              })
            }
          />
          Major requirement
        </label>
        <label class='toggle-wrapper'>
          <input
            type='checkbox'
            checked={course.requirement.college}
            onInput={e =>
              onCourse({
                ...course,
                requirement: {
                  ...course.requirement,
                  college: e.currentTarget.checked
                }
              })
            }
          />
          College GE requirement
        </label>
        <label class='toggle-wrapper'>
          <input
            type='checkbox'
            checked={course.forCredit}
            onInput={e =>
              onCourse({
                ...course,
                forCredit: e.currentTarget.checked
              })
            }
          />
          Credit received from this course (uncheck if failed or withdrawn)
        </label>
      </div>
      {prereqs[course.title] && (
        <div class='course-note info'>
          <strong>{course.title}</strong> is a valid course code.
        </div>
      )}
      {concurrentCourses.includes(course.title) && (
        <div
          class={`course-note ${prereqs[course.title] ? 'error' : 'warning'}`}
        >
          This course is listed multiple times in the same term.
        </div>
      )}
      {concurrentCourses.includes(course.title) && (
        <div class='course-note warning'>
          Credit for this course has already been received. If you are retaking
          this course, uncheck "Credit received" for the earlier course.
        </div>
      )}
      <button class='remove-course-btn' onClick={onRemove}>
        Remove
      </button>
    </div>
  )
}
