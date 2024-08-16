import pandas as pd
import numpy as np
import multiprocessing
import pandas as pd

# Define student and project classes
class Student:
    def __init__(self, id, preferences):
        self.id = id
        self.preferences = preferences
        self.offers = []
        self.matched_project = None
        self.rank_choice = 0

class Project:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.matched_students = []
        self.applicant_students = []
        self.rejected_students = []

# Define functions to help algorithm
def assign_project_to_student(student, project):
    project.matched_students.append(student)
    student.matched_project = project

def remove_student_from_project(student, project):
    project.matched_students.remove(student)
    student.matched_project = None

# Function to check validity of matching
def check_matching(students, projects):
    # check no student is matched to more than one project
    for s in students:
        if s.matched_project != None:
            for p in projects:
                if p.id != s.matched_project and p == s.matched_project:
                    print(f"Major Warning - Student {s.id} is matched to multiple projects")
                    return False
            
    # check no project is matched to more than its capacity
    for p in projects:
        if len(p.matched_students) > p.capacity:
            print(f"Major Warning - Project {p.id} is matched to more students than its capacity")
            return False
        
    # warning - check if projects were preferred by students
    for s in students:
        if s.matched_project != None and s.matched_project not in s.preferences:
            print(f"Minor Warning - Student {s.id} is matched to a project they did not prefer")
    
    # warning - check any unassigned students
    if any(s.matched_project == None for s in students):
        print(f"Minor Warning - Some students are not matched to any project")
        
    # valid
    print("Matching is valid")
    return True

# Function to shuffle students
def shuffle_students(students):
    # shuffle students
    np.random.shuffle(students)

# rate matching
def rate_matching(students):
    score = 0
    # rate matching
    for s in students:
        if s.matched_project != None:
            score += 10 * s.rank_choice **-2
    
    return score


# Gale-Shapley Algorithm implementation
def gale_shapley(students, projects, n_prefs=None):
    # By default, use all preferences
    if n_prefs == None:
        n_prefs = len(students[0].preferences)

    # Initialise all students and projects as unmatched
    # Initialise applicants for each project (assume project students ranked in order of preference for project)
    for student in students:
        student.matched_project = None
    for project in projects:
        project.matched_students = []
        project.applicant_students = [s for s in students if project.id in s.preferences[:n_prefs]]
    
    # stop while loop when every project either reaches capacity or has no more applicants
    continue_condition = True

    round_count = 0

    while continue_condition:
        round_count += 1
        # print(f"\nround {round_count} =====================")
        # projects propose to the top student who applied to them
        for p in projects:
            
            if (len(p.applicant_students) !=0 ) & (len(p.matched_students) < p.capacity):
                s = p.applicant_students.pop(0)
                s.offers.append(p.id)
                assign_project_to_student(s, p)

        
        # each student accepts best offer and rejects the rest
        for s in students:
            # print(f"Student {s.id} offers: {s.offers}")
            if s.offers:
                s.offers.sort(key=lambda x: s.preferences.index(x))
                best_offer = s.offers[0]
                for offer in s.offers:
                    if offer != best_offer:
                        project = next(p for p in projects if p.id == offer)
                        project.rejected_students.append(s)
                        remove_student_from_project(s, project)
                s.offers = [best_offer]

        # check if any projects have capacity and unseen applications
        any_unseen_applications = np.array([len(p.applicant_students) > 0 for p in projects])
        any_project_with_capacity = np.array([p.capacity > len(p.matched_students) for p in projects])
        continue_condition = any(any_unseen_applications & any_project_with_capacity)
        
        if round_count > (len(students) * len(projects)):
            break

        # clean up
        for student in students:
            if student.offers:
                student.matched_project = student.offers[0]
                student.rank_choice = 1 + student.preferences.index(student.matched_project)


def find_best_seed_matching(seed_range, results = None, N_PREFERENCES_TO_CONSIDER = None):
    # run to get best matching
    best_n_student_without_matching = 1000
    best_seed = 0
    best_matching_rating = 0

    # load data
    student_preferences = pd.read_csv("student_preferences.csv")
    project_capacities = pd.read_csv("project_capacities.csv")

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
        matching_student_df = pd.DataFrame(columns=["student", "project"])
        for i in range(len(students)):
            student = students[i]
            matching_student_df.loc[i] = [student.id, student.matched_project]

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



if __name__ == "__main__":

    with multiprocessing.Manager() as manager:
        results = manager.list()
        p1 = multiprocessing.Process(target=find_best_seed_matching, args=(range(0, 2000), results))
        p2 = multiprocessing.Process(target=find_best_seed_matching, args=(range(2000, 4000), results))
        p3 = multiprocessing.Process(target=find_best_seed_matching, args=(range(4000, 6000), results))
        p4 = multiprocessing.Process(target=find_best_seed_matching, args=(range(6000, 8000), results))
        p5 = multiprocessing.Process(target=find_best_seed_matching, args=(range(8000, 10000), results))
        p6 = multiprocessing.Process(target=find_best_seed_matching, args=(range(10000, 12000), results))
        p7 = multiprocessing.Process(target=find_best_seed_matching, args=(range(12000, 14000), results))
        p8 = multiprocessing.Process(target=find_best_seed_matching, args=(range(14000, 16000), results))

        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p5.start()
        p6.start()
        p7.start()
        p8.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()
        p6.join()
        p7.join()
        p8.join()

        best_seeds = list(results)

        df = pd.DataFrame(best_seeds, columns=["seed", "n_student_without_matching", "matching_rating"])
        df = df.sort_values(by=["n_student_without_matching", "matching_rating"], ascending=[True, False])
        print(df)