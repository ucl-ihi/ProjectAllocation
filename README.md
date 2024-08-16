# ProjectAllocation

## Getting started
Create 2 csv files or amend them with actual data
- `student_preferences.csv` with 1 + number of preferences columns: student, preference1, preference2, ..., preferenceN
- `project_capacities.csv` with 3 columns: project, capacity, supervisor

Run the allocation algorithm in `matching.ipynb` file.

The output are two csv files
- `matching_student.csv` for a student focused view with 4 columns: student, project allocated, preference rank of allocation, list of preferences
- `matching_project.csv` for a project focused view with 4 columns: project, list of student allocated, capacity, supervisor

### Random seed searching
Run the random seed searching to maximise student happiness (with parallel processing) using `python seed_search_par.py`

## Allocation Algorithm
The allocation is conducted using the Gale-Shapley Algorithm, where students are the "proposers" and the projects are the "acceptors". This setup will be student-optimal, meaning students will generally have their most preferred choice and no student allocated to a more desired project would have a lower preference than you.

For example project 1 with one capacity, it is student 1's 1st choice, student 2's 2nd choice, and student 11's 1st choice. Only students 1 or 11 will be allocated to project 1.

![gsalg](https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Gale-Shapley.gif/731px-Gale-Shapley.gif)

In order for all students to have equal opportunity to be allocated to their desired project and have enough time to speak with potential supervisors, students are uniformly randomly selected (i.e. the preferences of projects to select students are random). 

The quality of the matching is measured using the `rate_matching` function. This calculates a score per student and their preference, the overall score of the matching is 

$$ S = 10\sum_{i=1}^N r_i^{-2} $$

 where $r_i$ is rank preference of a student (e.g. 1 is top preference, 3 is third preference), N is the number of students, 10 is an arbitrary scaling factor for readability. We will run the algorithm multiple times to choose the best matching that maximises student happiness.

For a complete matching to be guaranteed, all students would have to provide preferences for all projects. However, this is impractical. Thus in particular circumstances, such as when too many students have the exact same preferences, it is possible that some students are not allocated to any of their preferences. In these cases, allocations will be manually conducted to the remaining projects.

## Example
Example student preferences and project capacities have been provided to demonstrate the allocation algorithm in action.

## FAQ

