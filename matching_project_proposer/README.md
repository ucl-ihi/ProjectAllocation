# Allocation Algorithm (Project proposer implementation)
The same Gale-Shapley Algorithm is implemented. This implementation use projects are the "proposers" and the students are the "acceptors". Though often the allocations are mimially different when optimised, this setup may sometimes give more complete matching for the trade off of a lower overall matching score.

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
