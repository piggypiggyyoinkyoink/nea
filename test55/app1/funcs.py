import re, datetime
from .models import *
def getGradeLevel(student):
    #gcse classes start with 10 or 11 (for year 10 and 11), A Level classes start with 12 or 13 (for year 12 and 13)
    myClass =str(student.className)
    isALevel = re.match("(12|13)[a-zA-Z0-9]*", myClass)
    if isALevel is not None:
        return 1#1 = A Level
    else:
        isGCSE = re.match("(10|11)[a-zA-Z0-9]*", myClass)
        if isGCSE is not None:
            return 2 # 2 = GCSE
        else:
            return 3 #3 = potential extension to cover KS3 classes



def getWarnings(id):
    
    warnings = []
    student = Student.objects.get(id=id)
    studentAsList = Student.objects.filter(id=id).values()[0]#get dictionary of attributes for the student
    assignments = StudentAssignment.objects.filter(studentID_id=id).values().exclude(isQuiz = True).order_by("-assignmentID_id")#ordering by assignmentid orders by date set since id is autoincrement
    passmark = student.targetGrade.percentage
    noIncomplete = 0; noFails = 0
    if assignments.count() > 1:
        # 5 is a hardcoded value. If the student hasnt completed 5 assignments, then set to number of assignments they have completed.
        if assignments.count() > 5:
            last_n_assignments = 5
        else:
            last_n_assignments = assignments.count()
        x = 0
        lnaAvg = 0; lnaTotal = 0; lnaCompleted = 0; lnaFails = 0
        
        #calculate number of fails, number incomplete and average for last n assignments
        for assignment in assignments:
            if Assignment.objects.filter(id=assignment["assignmentID_id"]).values_list("dueDate", flat=True)[0] > datetime.datetime.now().date() and not assignment["completed"]:
                pass 
            else:
                if last_n_assignments != x:
                    x +=1
                    if assignment["completed"]:
                        lnaCompleted +=1
                        lnaTotal += assignment["score"]
                        if assignment["score"] < passmark:
                            lnaFails +=1
                    
                if last_n_assignments >= x and lnaAvg == 0 and lnaCompleted != 0:
                    lnaAvg = lnaTotal / lnaCompleted

                if not assignment["completed"]:
                    noIncomplete +=1
                elif assignment["score"] < passmark:
                    noFails +=1
        
        #get warnings
        if lnaFails >=2:
            warnings.append(str(studentAsList["first_name"]) + " " + str(studentAsList["last_name"]) + " has failed " + str(lnaFails) + " out of the last " + str(last_n_assignments) + " assignments.")
        elif lnaAvg < (0.7 * student.average):
            warnings.append(str(studentAsList["first_name"]) + " " + str(studentAsList["last_name"]) + " has not been performing as well as expected in the last " + str(last_n_assignments) + " assignments.")
        if noIncomplete == 1:
            warnings.append(str(studentAsList["first_name"]) + " " + str(studentAsList["last_name"]) + " has not completed " + str(noIncomplete) + " assignment.")
        elif noIncomplete > 1:
            warnings.append(str(studentAsList["first_name"]) + " " + str(studentAsList["last_name"]) + " has not completed " + str(noIncomplete) + " assignments.")


    return warnings