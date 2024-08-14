# ProjectAllocation

## Getting started
Create 2 csv files or ammend them with actual data
- `student_preferences.csv` with 6 columns: Student, Preference1, Preference2, Preference3, Preference4, Preference5
- `project_capacities.csv` with 3 columns: Project, Capacity, Supervisor

Run the allocation algorithm in `.ipynb` file.

The output are two csv files
- `matching_student.csv` for a student focused view with 2 columns: Student, Project allocation
- `matching_project.csv` for a project focused view with 2 columns: Project, Student (list of student allocated)


## Allocation Algorithm
The allocation is conducted using the Gale-Shapley Algorithm, where projects are the "proposors" and the students are the "acceptors".

![gsalg](https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Gale-Shapley.gif/731px-Gale-Shapley.gif)

In order for all students to have equal opportunity to be allocated to their desired project, students are uniformly randomly selected (i.e. the preferences of projects to select students are random). 

The quality of the matching is measured using the `rate_matching` function. This calculates a score per student and their preference, the overall score of the matching is $\Sum_{i=1}^N s_i = 10 r_i^{-2}$ where $r_i$ is rank preference of a student (e.g. 1 is top preference, 3 is third preference). We will run the algorithm multiple times to choose the best matching that maximises student happiness.

For a complete matching to be guaranteed, all students would have to provide preferences for all projects. However, this is inpractical. Thus in particular circumstances, such as when too many students have the exact same preferences, it is possible that some students are not allocated to any of their preferences. In these cases, allocations will be manually conducted to the remaining projects.

## Example
Example student preferences and project capacities have been provided to demonstrate the allocation algorithm in action.

## FAQ

