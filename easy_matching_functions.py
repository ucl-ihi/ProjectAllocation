import pandas as pd
import numpy as np

# Define student and project classes
class Student:
    def __init__(self, id, preferences):
        self.id = id
        self.preferences = preferences
        self.matched_project = None
        self.rank_choice = 1 # 1 indexed for readability

class Project:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.matched_students = []
        self.applicant_students = []

# Define functions to help algorithm
def assign_student_to_project(student, project):
    project.matched_students.append(student)
    student.matched_project = project

def remove_student_from_project(student, project):
    project.matched_students.remove(student)
    student.matched_project = None

# Function to check validity of matching
def check_matching(students, projects):
    # check no student is matched to more than one project
    for s in students:
        if s.matched_project is not None:
            for p in projects:
                if p.id != s.matched_project.id and p == s.matched_project:
                    print(f"Major Warning - Student {s.id} is matched to multiple projects")
                    return False
            
    # check no project is matched to more than its capacity
    for p in projects:
        if len(p.matched_students) > p.capacity:
            print(f"Major Warning - Project {p.id} is matched to more students than its capacity")
            return False
        
    # warning - check if projects were preferred by students
    for s in students:
        if s.matched_project is not None and s.matched_project.id not in s.preferences:
            print(f"Minor Warning - Student {s.id} is matched to a project they did not prefer")
    
    # warning - check any unassigned students
    if any(s.matched_project is None for s in students):
        print(f"Minor Warning - Some students are not matched to any project")
        
    # valid
    print("Matching is valid")
    return True

# Function to shuffle students
def shuffle_students(students):
    np.random.shuffle(students)

# rate matching
def rate_matching(students):
    score = 0
    for s in students:
        if s.matched_project is not None:
            score += 10 * s.rank_choice **-2
    return score


# Gale-Shapley Algorithm implementation
def gale_shapley(students, projects, n_prefs=None):
    # By default, use all preferences
    if n_prefs is None:
        n_prefs = len(students[0].preferences)

    # Initialize all students and projects as unmatched
    for student in students:
        student.matched_project = None
    for project in projects:
        project.matched_students = []

    # Create a dictionary to easily access projects by their id
    project_dict = {p.id: p for p in projects}

    # Continue until all students have proposed to all their preferences
    unconsidered_students = students.copy()
    round_count = 0

    while unconsidered_students and round_count < (len(students) * len(projects)):
        round_count += 1
        
        for student in unconsidered_students.copy():
            if student.rank_choice <= min(n_prefs, len(student.preferences)):
                # Student proposes to their preference
                project_id = student.preferences[student.rank_choice - 1]
                project = project_dict[project_id]
                
                if project.capacity == 0:
                    # Project is removed, move to next preference
                    student.rank_choice += 1
                elif len(project.matched_students) < project.capacity:
                    # Project has capacity, accept the student
                    assign_student_to_project(student, project)
                    unconsidered_students.remove(student)
                else:
                    # Project is at capacity, compare with current matches
                    # The student with the lowest rank choice (highest preference) is the preferred student
                    # e.g. studentA.rank_choice = 1, studentB.rank_choice = 2, studentA is preferred
                    worst_match = max(project.matched_students, key=lambda s: s.rank_choice)
                    if student.rank_choice < worst_match.rank_choice:
                        # New student is preferred, swap
                        remove_student_from_project(worst_match, project)
                        assign_student_to_project(student, project)
                        unconsidered_students.remove(student)
                        unconsidered_students.append(worst_match)
                    else:
                        # Student is rejected, move to next preference
                        student.rank_choice += 1
            else:
                # Student has proposed to all preferences, remove from unconsidered_students
                student.rank_choice = 0
                unconsidered_students.remove(student)

    return students, projects


def find_best_seed_matching(student_preferences, project_capacities, seed_range, results = None, N_PREFERENCES_TO_CONSIDER = None):
    # run to get best matching
    best_n_student_without_matching = 1000
    best_seed = 0
    best_matching_rating = 0

    # By default, we will consider all given preferences
    if N_PREFERENCES_TO_CONSIDER is None:
        N_PREFERENCES_TO_CONSIDER = student_preferences.shape[1] - 1

    for s in seed_range:
        students = []
        projects = []

        for index, row in student_preferences.iterrows():
            students.append(Student(row["student"], row[1:].tolist()))
            
        for index, row in project_capacities.iterrows():
            projects.append(Project(row["project"], row["capacity"]))


        seed_i = s
        np.random.seed(seed_i)

        # run matching
        shuffle_students(students)
        gale_shapley(students, projects, n_prefs=N_PREFERENCES_TO_CONSIDER)


        # save as pandas
        matching_student_df = pd.DataFrame(columns=["student", "project", "rank_choice", "preference"])
        for i in range(len(students)):
            student = students[i]
            if student.matched_project is not None:
                matching_student_df.loc[i] = [student.id, student.matched_project.id, student.rank_choice, student.preferences]
            else: 
                matching_student_df.loc[i] = [student.id, None, 0, student.preferences]

        matching_project_df = pd.DataFrame(columns=["project", "students", "capacity"])
        for i in range(len(projects)):
            project = projects[i]
            matching_project_df.loc[i] = [project.id, [s.id for s in project.matched_students], project.capacity]

        # compare
        n_student_without_matching = len(matching_student_df[matching_student_df["project"].isnull()])
        
        if n_student_without_matching <= best_n_student_without_matching:
            if rate_matching(students) > best_matching_rating:
                best_n_student_without_matching = n_student_without_matching
                best_seed = seed_i
                best_matching_rating = rate_matching(students)
                print(f'New best seed: {best_seed} with {best_n_student_without_matching} students without matching, '+
                    f'Unmatched projects: {len(matching_project_df[(matching_project_df["students"].apply(len) == 0) & (matching_project_df["capacity"]>0)])} ' +
                    f'Score: {best_matching_rating}')
    print("======")
    if results is not None:
        results.append([best_seed, best_n_student_without_matching, best_matching_rating])
    return best_seed, best_n_student_without_matching, best_matching_rating
