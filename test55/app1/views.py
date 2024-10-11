from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth import models
from django.contrib.auth.models import User
from .models import *
from django.urls import reverse
import datetime, random
from django.contrib.auth import hashers
from django.db.models import Q
from .funcs import *
from icecream import ic
from django.contrib.auth import update_session_auth_hash, login


def dashboard(request): #login redirects here, which then redirects users to their designated homepage
    if request.user.is_authenticated:
        currentUser = User.objects.get(username = request.user.username) #retrieves the record of the user entity for the user currently logged in
        
        if currentUser.is_staff:
            return redirect("/staff")
        else:
            
            return redirect("/student")
    else:
        return redirect("accounts/login")

#home pages
def student(request): #student home page
    if request.user.is_authenticated:
        template = loader.get_template("dashboard.html")
        currentUser = User.objects.get(username = request.user.username) #retrieves the record of the user entity for the user currently logged in
        me = Student.objects.get(username_id = request.user.username) #retrieves the record of the student entity for the user currently logged in
        myClass = Class.objects.filter(name = me.className).values_list('id').first() #retrieves the class id corresponding to the class that corresponds to the student record retrieved by the previous query
        uncompleteAssignments = StudentAssignment.objects.filter(completed = False, studentID_id = me.pk, isQuiz = False).values_list('assignmentID_id', flat=True).all() #retrieves the assignment ids for all uncomplete assignments set for the student currently logged in
        overdueAssignments = Assignment.objects.filter(className_id = myClass, dueDate__lte = datetime.datetime.now().date(), id__in = uncompleteAssignments).order_by("dueDate").all().values().count() #retrieves the assignment objects corresponding to the ids retrieved by the previous query, where the due date is before the current date (i.e. retrieves all overdue assignment records for the student)
        if overdueAssignments > 0 :
            overdueAssignments = str(overdueAssignments)
            msg = str("You have " + overdueAssignments + "  overdue assignments")
        else:
            msg = False

        howMany = uncompleteAssignments.count()
        worstCategories = StudentCategory.objects.filter(studentID_id = me.pk).values().order_by("average", "total").exclude(total=0) #returns all the StudentCategory records as a list of dictionaries for the current student ordered by the success rate of the student in questions of the categories, excluding those where the student has never answered a question on.
        for category in worstCategories:
            category["name"] = QuestionCategory.objects.get(id = category["categoryID_id"]).name #returns the category name for each cateogry in the previous query and adds this to the dictionary for each one
            if category["average"] < me.targetGrade.percentage:  #if a student's question success rate for a category is less than the required percentage for their target grade, then the fail attribute is set to true and these categories will be highlighted in red on the students home page.
                category["fail"] = True
            else:
                category["fail"] = False
        
        assignments = Assignment.objects.filter(className_id = myClass, dueDate__gte = datetime.datetime.now().date(), id__in = uncompleteAssignments).order_by("dueDate").all().values() # returns a list of dictionaries representing all assignment records whose ids are in the queryset returned by the query on line 37 where the due data is after the current date (i.e. retrieves all upcoming assignment records for the student)
        for assignment in assignments:
            assignment["questions"] = StudentQuestionAssignment.objects.filter(assignmentID_id = assignment["id"], studentID_id = me.pk).count() #returns the number of questions in each upcoming assignment and adds this to the dictionary for each one

        context ={ #data passed to the HTML page
            "currentUser": currentUser,
            "assignments" : assignments,
            "categories": worstCategories,
            "me" : me,
            "howMany" : howMany,
            "msg" : msg,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("accounts/login")
    
def staff(request):#teacher home page
    if request.user.is_staff:
        currentUser = User.objects.get(username = request.user.username)
        template = loader.get_template("staff.html")
        context = {
            "currentUser" : currentUser,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")


#change password pages 
    
#page for html form where a user can change their password 
def changePassword(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            staff = True
        else:
            staff = False
        #bad is passed in the url if the password does not meet the requirements. Issue is the text passed to the html template to be displayed to the user
        bad = request.GET.get("bad", "")
        if bad == "1":
            issue = "Passwords do not match"
        elif bad == "2":
            issue = "Password must contain at least 8 characters"
        elif bad == "3":
            issue = "Password must contain uppercase letters, lowercase letters and numbers"
        else:
            issue = None
        currentUser = User.objects.get(id = request.user.id)
        template = loader.get_template("changepassword.html")
        context = {#data to be passed to the html template
            "currentUser" : currentUser,
            "staff" : staff,
            "issue" : issue,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

#backend processing for the change password form
def changePasswordDo(request):
    if request.user.is_authenticated:
        try:
            #get post data from html form
            pw1 = request.POST["pw"]
            pw2 = request.POST["pw2"]
            if pw1 == pw2:#check if password matches the confirm password
                if len(pw1) > 7: #checks if password is 8 or more characters
                    if re.search("[a-z]", pw1) == None or re.search("[A-Z]", pw1) == None or re.search("[0-9]", pw1) == None:#pw must contain at least one of A-Z, a-z and 0-9
                        return redirect("/changepassword/?bad=3")
                       
                    else:
                        me = User.objects.get(id = request.user.id)
                        pword = hashers.make_password(pw1) #hash the password before storing in the database
                        me.password = pword
                        me.save()
                        #keep user logged in
                        update_session_auth_hash(request, request.user)
                        login(request, request.user)
                        return redirect("/")
                else:#password too small
                    return redirect("/changepassword/?bad=2")

            else:#passwords do not match
                return redirect("/changepassword/?bad=1")
        except:
            return redirect("/changepassword")
    else:
        return redirect("/")#redirect to home page if successful


#teacher pages

def studentList(request): #student list page to display all students
    if request.user.is_staff:
        #search bar passes search query in url. Users can search by student first and last name or class name.
        search = request.GET.get("search", None)
        if search is not None:
            students = Student.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(className = search)).values().order_by("className")#returns a list of dictionaries representing all student records whose first name, last name or class name contains the search query
            
        else:
            students = Student.objects.all().values().order_by("className", "last_name")#if no search query, return list of dictionaries representing all student records
        

        howMany = students.count()
        for student in students:
            warnings = getWarnings(student["id"]) #uses getWarnings function in funcs.py to determine if each student has failed or not completed any assignments. If they have, the warnings flag for that student will be set to True and the student will be highlighted in red in the list.
            if warnings == []:
                student["warnings"] = False
            else:
                student["warnings"] = True
            #get the total number of assignments set and completed and adds these to the dictionary for each student
            studentAssignmentsSet = StudentAssignment.objects.filter(studentID_id = student["id"]).count()
            student["set"] = studentAssignmentsSet
            studentAssignmentsDone = StudentAssignment.objects.filter(studentID_id = student["id"], completed = True).count()
            student["done"] = studentAssignmentsDone
            #get the target grade and add it to the dictionary for each student
            student["targetGrade"] = Grade.objects.get(id = student["targetGrade_id"]).grade

        currentUser = User.objects.get(username = request.user.username)
        template = loader.get_template("studentlist.html")

        context = {#data passed to HTMl template
            "allStudents" : students,
            "currentUser" : currentUser,
            "howMany" : howMany,
            "search" : search,

        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

def studentListSearch(request):#processing for the search query
    if request.user.is_staff:
        search = request.POST["search"]
        if search is not None:
            return redirect("/users/list/?search=" + search)
        else:
            return redirect("/users/list")
    else:
        return redirect("/")


def studentDetails(request, id):#page displaying details for an individual student. Student id is passed in the url
    if request.user.is_staff:
        currentUser = User.objects.get(id = request.user.id)
        template = loader.get_template("studentdetails.html")
        #get student and user records corresponding to the student
        myStudent = Student.objects.get(id = id)
        myUser = User.objects.get(username = myStudent.username)
        
        #get number of assignments set and complete 
        assignmentsComplete = StudentAssignment.objects.filter(studentID_id = myStudent.pk, completed = True).count()#gets the number of records in the StudentAssignment linking table where the assignment has been completed corresponding to the student
        assignmentsSet = StudentAssignment.objects.filter(studentID_id = myStudent.pk).count()#gets the total number of records in the StudentAssignment linking table corresponding to the student
        warningsList = getWarnings(id)
        
        bestCategory = StudentCategory.objects.filter(studentID_id = id).values().order_by("-average", "-total").exclude(total=0).first()#returns the category with the highest average score, excluding those where no questions have been answered
        if bestCategory is not None:
            bestCategory["name"] = QuestionCategory.objects.get(id = bestCategory["categoryID_id"]).name
        worstCategory = StudentCategory.objects.filter(studentID_id=id).values().order_by("average", "total").exclude(total=0).first()#returns the category with the lowest average score, excluding those where no questions have been answered
        if worstCategory is not None and worstCategory != bestCategory: #prevents the best category being the worst category if only one category exists where the student has answered questions.
            worstCategory["name"] = QuestionCategory.objects.get(id = worstCategory["categoryID_id"]).name
        context = { #data passed to HTML template
            "student" : myStudent,
            "user" : myUser,
            "currentUser" : currentUser,
            "assignmentsComplete" : assignmentsComplete,
            "assignmentsSet" : assignmentsSet,
            "warnings" : warningsList,
            "bestCategory" : bestCategory,
            "worstCategory" : worstCategory,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

def updateClassStudent(request, id): #HTML form to change a student's class
    if request.user.is_staff:
        template = loader.get_template("updateclassstudent.html")
        student = Student.objects.get(id = id)
        allClasses = Class.objects.all().values().order_by("name")#returns all class names. These are to be put as options in the <select> field in the form.
        context = { #data passed to HTML template
            "id" : id,
            "student" : student,
            "allClasses" : allClasses,
            "currentUser" : User.objects.get(username=request.user.username)
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

def updateClassStudentDo(request, id): #processing for HTML form to update a student's class
    if request.user.is_staff:
        #get student record from database and new class name from form
        student = Student.objects.get(id = id)
        classname = request.POST["cn"]

        #If the class doesnt exist, a new class is created
        if not Class.objects.filter(name = classname).exists():
            newClass = Class(name = classname)
            newClass.save()
        try:
            student = Student.objects.get(username_id = student.username)
            oldclass = Class.objects.get(name = student.className).pk
            
            student.className = Class.objects.get(name=classname)
            student.save()
            #add upcoming assignments set for new class
            classAssignments = Assignment.objects.filter(className_id = student.className.pk, dueDate__gte = datetime.datetime.now().date()).values_list('id', flat=True).all()#returns assignment ids for the new student's class, for assignments with a due date after the current date
            for assignment in classAssignments:
                
                try:
                    studentAssignment = StudentAssignment(studentID_id = student.pk, assignmentID_id = assignment) #creates new studentAssignment records in the linking table between Students and Assignments allowing the new student to access the assignments
                    studentAssignment.save()
                except:
                    pass

                questions = QuestionInAssignment.objects.filter(assignmentID_id = assignment).values_list('questionID_id', flat=True).all() #returns question ids for all the questions in all upcoming assignments for the new student's class
                for question in questions:
                    try:

                        StudentQuestionAssignment(studentID_id = student.pk, questionID_id = question, assignmentID_id = assignment).save() #creates new studentQuestionAssignment records in the linking table between Students, Assignments and Questions, allowing the new student to access the questions for each assignment
                    except:
                        pass
            
            #delete uncompleted assignments for past class
            oldAssignments = StudentAssignment.objects.filter(completed = False, studentID_id = student.pk, assignmentID_id__in = Assignment.objects.filter(className_id = oldclass).values_list("id"))
            for assignment in oldAssignments:
                assignment.delete()
                
            return HttpResponseRedirect(reverse("list"))
        except:
            return redirect("studentList")#exceptions will return the user to the student list page
    else:
        return redirect("/")
    
def updateTargetGrade(request, id):#HTML form to update the target grade of an existing student
    if request.user.is_staff:
        student = Student.objects.get(pk = id)
        url = request.GET.get("url", None)#Student details pages linking here pass the previous url path in the URL to redirect back to after the form has been submitted
        level = getGradeLevel(student)
        template = loader.get_template("updatetargetgrade.html")
        grades = Grade.objects.filter(level = level)
        context = { #data passed to HTML page
            "grades" : grades,
            "student" : student,
            "currentUser" : User.objects.get(username = request.user.username),
            "urlpath" : url,
        }
        return HttpResponse(template.render(context, request))

    else:
        return redirect("/")

def StudentTargetGradeDo(request, studentid): #backend processing for creating and updating target grades for students.
    next = request.POST.get("next", "/users/list")
    try:
        gradeid = request.POST["grade"]
        student = Student.objects.get(pk = studentid) #returns the Student record for the student whose target grade is being updated
        grade = Grade.objects.get(pk = gradeid) 
        student.targetGrade = grade
        student.save()
    except:
        return redirect("targetGrade")
    return redirect(next)

def resetStudentPassword(request, id):#page to do the processing for a teacher to reset a student's password. Student id is passed in the url
    if request.user.is_staff:
        try:
            default = "Password1"#hardcoded default password
             
            user = User.objects.get(username = Student.objects.get(id = id).username)#get user record corresponding to the student id passed in the url
            user.password = hashers.make_password(default)#hash the password before storing in database
            user.save()
        except:
            pass
        return redirect("/users/details/" + str(id))
    else:
        return redirect("/")


def add(request): #create new student HTML form page
    if request.user.is_staff:
        #Class pages linking here pass the class id in the URL. This obtains the corresponding class name and automatically fills in the relevant field in the form with the class name. If no class name is passed in the URL, the field is blank by defualt.
        myClass = request.GET.get("class", "") 
        allClasses = Class.objects.all().values().order_by("name")
        if myClass is not "":
            myClass = Class.objects.get(id=myClass) 
        context = { #data passed to the HTML page
            "myClass" : myClass,
            "allClasses" : allClasses,
            "currentUser" : User.objects.get(username = request.user.username)
        }
        template = loader.get_template("add.html")
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/") #student users attempting to access all teacher pages get automatically redirected to the student home page

def addrecord(request): #backend processing for the add new user form
    if request.user.is_staff:
        #retrieve data from form fields
        fname = request.POST["first"]
        lastname = request.POST["last"]
        emailAddress = request.POST["ea"]
        pword = request.POST["pw"]
        pword = hashers.make_password(pword)
        uname = request.POST["ea"]
        cname = request.POST["cn"]
        validEmail = re.search("@bostongrammarschool.co.uk", emailAddress) #only accepts school email addresses
        if validEmail is not None:
            
            try:
                #creates new user and student records for the new student
                user = User(username = uname, password = pword, email = emailAddress, first_name = fname, last_name = lastname)
                student = Student(first_name = fname, last_name = lastname, username_id = uname, className_id = cname)
                user.save()
                student.save()
                #creates assignment data for all upcoming assignments for the class the student is assigned to so the new student can access them.
                myClass = Class.objects.filter(name = cname).values_list('id').first()
                try:
                    classAssignments = Assignment.objects.filter(className_id = myClass, dueDate__gte = datetime.datetime.now().date()).values_list('id', flat=True).all()#returns assignment ids for the new student's class, for assignments with a due date after the current date
                    for assignment in classAssignments:
                        
                        try:
                            studentAssignment = StudentAssignment(studentID_id = student.pk, assignmentID_id = assignment) #creates new studentAssignment records in the linking table between Students and Assignments allowing the new student to access the assignments
                            studentAssignment.save()
                        except:
                            pass
                        questions = QuestionInAssignment.objects.filter(assignmentID_id = assignment).values_list('questionID_id', flat=True).all() #returns question ids for all the questions in all upcoming assignments for the new student's class
                        for question in questions:
                            try:

                                StudentQuestionAssignment(studentID_id = student.pk, questionID_id = question, assignmentID_id = assignment).save() #creates new studentQuestionAssignment records in the linking table between Students, Assignments and Questions, allowing the new student to access the questions for each assignment
                            except:
                                pass
                    
                    categories = QuestionCategory.objects.all().values_list('id', flat=True) #returns the ids for all categories
                    for category in categories:
                        newCategory = StudentCategory(studentID_id = student.pk, categoryID_id = category) #creates new records in the linking table between Students and Categories allowing data to be collected for each category for the new student.
                        newCategory.save()
                except:pass
                return redirect("/users/addtargetgrade/" + str(student.pk)) #redirects the user to the target grade page for the new student so the teacher can set a target grade for the new student
            except:
                return redirect("add")# any exceptions will redirect the user back to the HTML form
        else:
            return redirect("add")

    else:
        return redirect("/")

def studentTargetGrade(request, id): #page with HTML form to create a target grade for new students after creating them
    if request.user.is_staff:
        student = Student.objects.get(pk = id)
       
        level = getGradeLevel(student) #determine whether the student is GCSE or A Level to determine whether the options for target grade should be 9-1 or A*-E
        template = loader.get_template("addrecordtargetgrade.html")
        grades = Grade.objects.filter(level = level)#returns all target grades for the relevant level to be displayed as options on the HTML form
       
        context = { #data passed to the HTMl page
            "grades" : grades,
            "student" : student,
            "currentUser" : User.objects.get(username = request.user.username)
        }
        return HttpResponse(template.render(context, request))

    else:
        return redirect("/")

#delete a student record, and their corresponding user record from the database. ID is passed in the URL
def deleteStudentDo(request, id):
    if request.user.is_staff:
        student = Student.objects.get(id = id)
        uname = student.username
        try:
            
            student.delete()
            user = User.objects.get(username = uname)
            user.delete()
            return HttpResponseRedirect(reverse("list"))
        except:
            return redirect("studentList")
    else:
        return redirect("/")



#list of all classes
def classList(request):
    if request.user.is_staff:
        currentUser = User.objects.get(username = request.user.username)
        template = loader.get_template("classlist.html")

        classes = Class.objects.all().values().order_by("name")#get list of dictionaries representing all class records from the database

        #for each class, get the number of students and number of upcoming assignments and add these to the dictionary
        for eachClass in classes:
            students = Student.objects.filter(className = eachClass["name"]).count() #returns the number of students whose className attribute matches the name of the class
            upcomingAssignments = Assignment.objects.filter(className_id = eachClass["id"]).exclude(dueDate__lt = datetime.date.today()).count() #returns the number of assignments set for the class whose due date is after the current date (i.e. number of upcoming assignments)
            eachClass["students"] = students
            eachClass["assignments"] = upcomingAssignments
        context = { #data passed to HTML template
            "allClasses" : classes,
            "currentUser": currentUser
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

#page displaying details for an individual class, such as students in the class and assignments set for the class. The class id is passed in the url.
def classDetails(request, id):
    if request.user.is_staff:
        currentUser = User.objects.get(username = request.user.username)
        template = loader.get_template("classdetails.html")
        myClass = Class.objects.get(id = id) #returns class record corresponding to the class id
        students = Student.objects.filter(className = myClass.name).values() #gets all student records who are in the class, i.e the value of their className attribute matches the name of the class

        for student in students:
            #for each student, get the target grade, number of assignments set and number of assignments completed.
            student["targetGrade"] = str(Grade.objects.filter(id = student["targetGrade_id"]).values_list("grade", flat = True).first())
            studentAssignmentsSet = StudentAssignment.objects.filter(studentID_id = student["id"]).exclude(isQuiz = True).count() #since quizzes are stored in the same table as assignments, need to exclude quizzes from this query
            student["set"] = studentAssignmentsSet
            studentAssignmentsDone = StudentAssignment.objects.filter(studentID_id = student["id"], completed = True).count()
            student["done"] = studentAssignmentsDone

            #uses getWarnings function in funcs.py to determine if each student has failed or not completed any assignments. If they have, the warnings flag for that student will be set to True and the student will be highlighted in red.
            warnings = getWarnings(student["id"])
            if warnings != []:
                student["warnings"] = True
            else:
                student["warnings"] = False
        
        assignments = Assignment.objects.filter(className_id = id).values().order_by("dueDate").exclude(dueDate__lt = datetime.datetime.now().date())#returns all assignments set for the class, ordered by due date, excluding those with a due date before the current date
        #for each assignment, get the number of students who have been set the assignment and the number of students who have completed the assignment
        for assignment in assignments:
            #since quizzes are stored in the same table as assignments, need to exclude quizzes from these query
            assignment["set"] = str(StudentAssignment.objects.filter(assignmentID_id = assignment["id"]).exclude(isQuiz = True).count()) #returns the number of students who have been set the assignment
            assignment["done"] = str(StudentAssignment.objects.filter(assignmentID_id = assignment["id"], completed = True).exclude(isQuiz = True).count())#returns the number of students who have completed the assignment
        context = { #data passed to HTML temlate
            "class" : myClass,
            "students" : students,
            "assignments" : assignments,
            "currentUser" : currentUser,
        }
        
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")
    

def addclass(request): #HTMl form to create a new class
    if request.user.is_staff:
        template = loader.get_template("addclass.html")
        context = {
            "currentUser" : User.objects.get(username = request.user.username)
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")
    
def addrecordclass(request):#backend processing for the HTML form to create a new class
    if request.user.is_staff:
        classname = request.POST["cn"]
        #regex to check if class name matches the syntax for BGS class names
        if re.match("(10|11|12|13)[a-zA-Z0-9]*", classname) is not None:
            try:
                newClass = Class(name = classname)
                newClass.save()
                
                
                return HttpResponseRedirect(reverse("classList"))#redirects users back to the class list
            except:
                return redirect("addclass") #exceptions will redirect users back to the HTML form
        else:
            return redirect("addclass")
    else:
        return redirect("/")

#Delete a class record from the database. ID is passed in the url
def deleteClass(request, id):
    if request.user.is_staff:
        try:
            myClass = Class.objects.get(id=id)
            myClass.delete()
            
        except:pass
        return redirect("/class/list")
    else:
        return redirect("/")



#list of all assignments for all classes
def AssignmentList(request):
    if request.user.is_staff:
        template = loader.get_template("assignmentlist.html")
        currentUser = User.objects.get(username = request.user.username)
        today = datetime.date.today()
        assignments = Assignment.objects.filter(dueDate__gte = today).values().exclude(className_id = None).order_by("dueDate")#get list of dictionaries representing assignment records for assignments due in the future. Exclude where there is no className assigned in order to filter out quizzes from this query
        pastAssignments = Assignment.objects.filter(dueDate__lt = today).values().exclude(className_id = None).order_by("-dueDate")#get list of dictionaries representing assignment records for past assignments. Exclude where there is no className assigned in order to filter out quizzes from this query (all assignments have a className assigned)

        for assignment in assignments:
            
            #add extra data for each upcoming assignment to the dictionary
            assignment["daysLeft"] = ( assignment["dueDate"] - today).days #gets how many days between today and the due date
            assignment["className_id"] = Class.objects.get(id = assignment["className_id"]) #returns the class object corresponding to the class id the assignment is set for
            assignment["noCompleted"] = StudentAssignment.objects.filter(assignmentID_id = assignment["id"], completed = True).count() #returns the number of StudentAssignment records corresponding to the assignment where completed = True to get the number of students who have completed the assignment
            assignment["total"] = StudentAssignment.objects.filter(assignmentID_id = assignment["id"]).count() #gets the total number of students who have been set the assignment
            assignment["questions"] = QuestionInAssignment.objects.filter(assignmentID_id = assignment["id"]).count() #returns the number of QuestionInAssignment records corresponding to the assignment to get the number of questions in the assignment
       

        for assignment in pastAssignments:
            #add extra data for each past assignment to the dictionary, same as with upcoming assignments minus the days left.
            assignment["className_id"] = Class.objects.get(id = assignment["className_id"])
            assignment["noCompleted"] = StudentAssignment.objects.filter(assignmentID_id = assignment["id"], completed = True).count()
            assignment["total"] = StudentAssignment.objects.filter(assignmentID_id = assignment["id"]).count()
            assignment["questions"] = QuestionInAssignment.objects.filter(assignmentID_id = assignment["id"]).count()


        
        context = { #data passed to HTML template
            "allAssignments" : assignments,
            "pastAssignments" : pastAssignments,
            "currentUser" : currentUser
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

#page displaying details for an individual assignment. The id is passed in the url
def AssignmentDetails(request, id):
    if request.user.is_staff:
        template = loader.get_template("assignmentdetails.html")
        myAssignment = Assignment.objects.get(id = id)
        currentUser = User.objects.get(username = request.user.username)
        
        questions = QuestionInAssignment.objects.filter(assignmentID_id = id).values() #returns a list of dictionaries representing all records from the QuestionInAssignment linking table correpsonding to the assignment
        for y in questions:
            y["questionText"] = Question.objects.get(pk = y["questionID_id"]).questionText#adds the question text for each question to the dictionary
            
        studentResults = StudentAssignment.objects.filter(assignmentID_id = id).values()#returns a list of dictionaries representing all records from the StudentAssignment linking table correpsonding to the assignment

        for student in studentResults:
            #get the student record for each StudentAssignment and add to the dictionary
            z = Student.objects.get(id = student["studentID_id"])
            student["student"] = z
            #calculate student grade for the assignment
            student["grade"] = Grade.objects.filter(percentage__lte = student["score"], level = getGradeLevel(z)).values_list("grade", flat=True).order_by("-percentage").first()
            #determine if the student passed or failed the assignment based on their target grade
            if student["score"] >= z.targetGrade.percentage:
                student["pass"] = True
            else:
                student["pass"] = False

        #get due date into the format DD-MM-YYYY for the HTML form datefield
        if len(str(myAssignment.dueDate.month)) == 1: #type:ignore
            month = "0" + str(myAssignment.dueDate.month)#type:ignore
        else:
            month = str(myAssignment.dueDate.month)#type:ignore
        
        if len(str(myAssignment.dueDate.day)) == 1:#type:ignore
            day = "0" + str(myAssignment.dueDate.day)#type:ignore
        else:
            day = str(myAssignment.dueDate.day)#type:ignore
        d = str(str(myAssignment.dueDate.year) + "-" + month + "-" + day)#type:ignore
    
        if myAssignment.dueDate < datetime.datetime.now().date(): #type: ignore
            past = True
        else:
            past = False
        context = { #data passed to html template
            "assignment" : myAssignment,
            "questions" : questions,
            "currentUser" : currentUser,
            "studentResults" : studentResults,
            "past" : past,
            "date" : d,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

#backend processing to update an assignment's due date. Assignment id is passed in the url
def updateDueDate(request, id):
    if request.user.is_staff:
        try:
            assignment = Assignment.objects.get(id=id) #get assignment record corresponding to the assignment id passed in the url
            dueDate = request.POST["dd"]#get post data from date field on assignment details page
            assignment.dueDate = dueDate
            assignment.save()
        except:
            pass
        return redirect("/assignments/details/" + str(id))
    else:
        return redirect("/")

#page to see which questions each student answered correctly on an assignment
def assignmentScores(request, studentid, assignmentid):
    if request.user.is_staff:
        #get all StudentQuestionAssignment records to get question answer data for the student and the assignment
        studentAssignments = StudentQuestionAssignment.objects.filter(studentID_id = studentid, assignmentID_id = assignmentid).values()
        
        #get question text for each question
        for question in studentAssignments:
            question["questionText"] = Question.objects.get(id = question["questionID_id"]).questionText
        template = loader.get_template("assignmentscores.html")
        
        context = {#data passed to html template
            "questions" : studentAssignments,
            "currentUser" : User.objects.get(username = request.user.username),
            "student" : Student.objects.get(id=studentid)
        }
        return HttpResponse(template.render(context, request))

    else:
        return redirect("/")


def AssignmentCreate(request):#HTML form to create a new assignment
    if request.user.is_staff:
        template = loader.get_template("assignmentcreate.html")
        myClass = request.GET.get("class", "") #class details page linking here will pass a class ID in the url, to be autofilled in the form.
        if myClass is not "":
            myClass = Class.objects.get(id=myClass)#returns the class record corresponding to the class id passed in the url, if present
        issue = request.GET.get("past", None)
        if issue is not None:
            warning = True
        else:
            warning = False
        allClasses = Class.objects.all().values().order_by("name")#returns all class records
        context = { #data passed to HTMl template
            "myClass" : myClass,
            "allClasses" : allClasses,
            "currentUser" : User.objects.get(username = request.user.username),
            "warning": warning,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

def AssignmentCreateDo(request):#backend processing for form creating a new assignment
    if request.user.is_staff:
        #get POST data from HTML form
        name = request.POST["name"]
        className = request.POST["cn"]
        dueDate = request.POST["dueDate"]
        #create new assignment
        if datetime.datetime.strptime(dueDate, "%Y-%m-%d").date() >= datetime.date.today():
            try:
                #get class id corresponding to the class name given in the form
                myClass = Class.objects.get(name = className)
                className = myClass.pk
                try:
                    #create new assignment using the data from the form
                    newAssignment = Assignment(name = name, className = myClass, dueDate = dueDate)
                    newAssignment.save()
                    myData = Assignment.objects.filter(name = name, className = myClass, dueDate = dueDate).values_list("id", flat = True)
                    
                    students = Student.objects.filter(className = myClass.name).values_list("id", flat = True) #returns all student records in the class the assignment will be set for
                    #create new StudentAssignment record in the linking table for each student in the class
                    for student in students:
                        newRecord = StudentAssignment(studentID_id = student, assignmentID_id = newAssignment.pk)
                        newRecord.save()
                    return HttpResponseRedirect(reverse("updateAssignment", args = (myData[0],)))#if no exceptions occur, redirect to the page where questions can be added to the assignment
                except:
                    #redirect to the HTML form if any errors occur in processing the data
                    return redirect("/assignments/add")
            except:
                return redirect("/assignments/add")
        else:
            return redirect("/assignments/add/?past=true")
    else:
        return redirect("/")

def AddQuestions(request, id):#HTML form to add / update the questions in an assignment
    if request.user.is_staff:
        template = loader.get_template("assignmentaddquestions.html")

        thisAssignment = Assignment.objects.get(id = id)#returns assignment record corresponding to the assignment id passed in the url
        myClass = str(thisAssignment.className)
        try:
            level = request.GET.get("level", None)
            if level == None:
                level = request.POST["level"]
        except:
            #determine whether the class the assignment is assigned to is GCSE or A Level using regular expressions. GCSE classes are of the form 10__ or 11__ and A Level classes are of the form 12__ or 13__
            isALevel = re.search("12|13", myClass)
            if isALevel is not None:
                level =  "1"
            else:
                isGCSE = re.search("10|11", myClass)
                if isGCSE is not None:
                    level = "2"
                else:
                   level = "3"#class name not formatted correctly
            
        #return all categories that are of the level (GCSE or A Level) determined by the regular expression
        yesCategories = QuestionCategory.objects.filter(level = level).values_list("id", flat=True)
       #return all question records that are in one the categories returned by the previous query
        questions = Question.objects.filter(questionCategory_id__in = yesCategories).values().order_by("questionCategory")

        #Questions are ordered by category.
        #To organise the HTML page, display the category title when the cateogry changes, i.e when a question's category is different to the previous question's category, so that questions can be grouped by category
        prevQuestionCategory = ""
        for x in questions:
            if x["questionCategory_id"] != prevQuestionCategory:
                x["displayQuestionCategory"] = True
                prevQuestionCategory = x["questionCategory_id"]
                x["questionCategory"] = QuestionCategory.objects.get(id=x["questionCategory_id"])
            else:
                x["displayQuestionCategory"] = False
            #if the question is already in the assignment when changing the questions in an assignment, set checked flag to True so the checkbox corresponding to the question can be checked
            count = QuestionInAssignment.objects.filter(questionID_id = x["id"], assignmentID_id = id).count()
            if count == 0:
                x["checked"] = False
            else:
                x["checked"] = True
          
        context = { #data passed to HTML template
            "id" : id,
            "questions" : questions,
            "thisAssignment" : thisAssignment,
            "thisClass" : myClass,
            "currentUser" : User.objects.get(username=request.user.username),
            "level" : level,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

def AddQuestionsDo(request, id):#backend processing for add questions form
    if request.user.is_staff:
        #return all student records who are in the class the assignment is set for
        students = Student.objects.raw("SELECT app1_student.id FROM app1_student, app1_assignment, app1_class WHERE app1_student.className_id = app1_class.name AND app1_class.id = app1_assignment.className_id AND app1_assignment.id = %s", [id])
        questions = Question.objects.all().values_list("id")#returns a list of all question ids in the database
        
        #for each question, determine whether it was ticked in the form
        #if checked, create new QuestionInAssignment and StudentQuestionAssignment (linking tables) records for that question
        #if not checked, but a QuestionInAssignment or StudentQuestionAssignment record for that question exists, delete these records.
        for x in questions:
            try:
                #question is checked
                questionText = request.POST["question"+ str( x[0])]
                if questionText:
                    newQuestion = QuestionInAssignment(questionID_id = x[0], assignmentID_id = id)
                    try:
                        newQuestion.save()
                    except:
                        pass
                    
                    for y in students:
                        newStudentQuestionAssignment = StudentQuestionAssignment(studentID_id = y.id, questionID_id = x[0], assignmentID_id = id)
                        try:
                            newStudentQuestionAssignment.save()
                        except:
                            pass
            except:
                #question is not checked
                try:
                    myData = QuestionInAssignment.objects.get(questionID_id = x[0], assignmentID_id = id)
                    myData.delete()
                
                except:
                    pass
                try:
                    for z in students:
                        myData2 = StudentQuestionAssignment.objects.get(questionID_id = x[0], assignmentID_id = id, studentID_id = z.id)
                        myData2.delete() 
                except:
                    pass
                pass
            
           
        return redirect("/assignments/details/" + str(id))#redirect to assignment details page
    else:
        return redirect("/")


def AssignmentDelete(request, id):#delete assignment record and associated linking table records from the database.
    if request.user.is_staff:
        assignment = Assignment.objects.get(id = id)
        questions = QuestionInAssignment.objects.filter(assignmentID_id = id).values()
        try:
            assignment.delete()
            questions.delete()
            return HttpResponseRedirect(reverse("list"))
        except:
            return redirect("AssignmentList")
    else:
        return redirect("/")
    


def QuestionList(request):#page to display list of all questions
    if request.user.is_authenticated:
        if request.user.is_staff:
            template = loader.get_template("questionlist.html")
            currentUser = User.objects.get(username = request.user.username)

            #get all question records from the database
            questions = Question.objects.all().values().order_by("questionCategory_id")
            for question in questions:
                question["category"] = QuestionCategory.objects.filter(id = question["questionCategory_id"]).first()#get category name corresponding to id

            context = {
                "questions" : questions,
                "currentUser" : currentUser,
            }
            return HttpResponse(template.render(context, request))
        else:
            return redirect("/")
    else:
        return redirect("accounts/login")

#page to display details for each individual question. Question id is passed in url
def questionDetails(request, id):
    if request.user.is_staff:
        try:
            template = loader.get_template("questiondetails.html")
            currentUser = User.objects.get(username = request.user.username)
            #get question and linking table records correpsonding to the question id passed in url
            sqa = StudentQuestionAssignment.objects.filter(questionID_id = id).exclude(studentAnswer = None)
            q = Question.objects.get(id=id)
            #get percentage of people who chose each option
            total = sqa.count()
            numOpt1 = round(((sqa.filter(studentAnswer = str(q.opt1)).count() / total) * 100),2)
            numOpt2 = round(((sqa.filter(studentAnswer = str(q.opt2)).count() / total) * 100),2)
            numOpt3 = round(((sqa.filter(studentAnswer = str(q.opt3)).count() / total) * 100),2)
            numOpt4 = round(((sqa.filter(studentAnswer = str(q.opt4)).count() / total) * 100),2)
            
            context = { # data passed to html template
                "currentUser": currentUser,
                "sqa": sqa,
                "question": q,
                "total": total,
                "numOpt1": numOpt1,
                "numOpt2" : numOpt2,
                "numOpt3" : numOpt3,
                "numOpt4" : numOpt4,
            }
            return HttpResponse(template.render(context, request))
        except:
            return redirect("/questions/list")
    else:
        return redirect("/")

#page for HTML form to update a question details (question text, category, options and correct answer). QUestion id is passed in the url
def QuestionUpdate(request, id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            bad = request.GET.get("bad","")# bad is passed in the url if the correct answer doesnt match any of the options
            if bad == "true":
                issue = "Correct answer must exactly match one of the options"
            else:
                issue = None
            currentUser = User.objects.get(username = request.user.username)
            template = loader.get_template("questionupdate.html")
            #get question and category records corresponding to the id passed in the url
            question = Question.objects.get(id=id)
            myCategory = QuestionCategory.objects.raw("SELECT app1_questionCategory.id, app1_questionCategory.name FROM app1_questioncategory, app1_question WHERE app1_questioncategory.id = app1_question.questionCategory_id AND app1_question.id = %s", [id] )
            categories = QuestionCategory.objects.all()#returns all the category records in the database
            context = { #data passed to html template
                "question" : question,
                "categories" : categories,
                "myCategory" : myCategory[0],
                "currentUser" : currentUser,
                "issue" : issue,
            }
            return HttpResponse(template.render(context, request))
        else:
            return redirect("/")
    else:
        return redirect("accounts/login")

#backend processing for the HTML form to update question details
def QuestionUpdateDo(request, id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            try:
                #get post data from form
                questionText = request.POST["questionText"]
                opt1 = request.POST["opt1"]
                opt2 = request.POST["opt2"]
                opt3 = request.POST["opt3"]
                opt4 = request.POST["opt4"]
                answer = request.POST["answer"]
                category = request.POST["category"]

                #only update the question if the correct answer matches one of the options, otherwise redirect back to the form with the "bad" url
                if answer == opt1 or answer == opt2 or answer == opt3 or answer == opt4:
                    question = Question.objects.get(id=id)
                    
                    question.questionText = questionText
                    question.opt1 = opt1
                    question.opt2 = opt2
                    question.opt3 = opt3
                    question.opt4 = opt4
                    question.answer = answer
                    
                    
                    question.questionCategory = QuestionCategory.objects.get(id = category)
                    question.save()
                    return redirect("/questions/list")#redirect to question list page if successful
                else:
                    return HttpResponseRedirect(reverse("QuestionUpdate", args = (id,)))
            except:
                return HttpResponseRedirect(reverse("QuestionUpdate", args = (id,)))
        else:
            return redirect("/")

def QuestionCreate(request): #html form for creating a new question
    if request.user.is_authenticated:
        if request.user.is_staff:
            bad = request.GET.get("bad","") #'bad' is passed to the url if the correct answer submittec in the form does not match any of the options (i.e. if the question is impossible to answer correctly)
            if bad == "true":
                issue = "Correct answer must exactly match one of the options"
            else:
                issue = None
            template = loader.get_template("questioncreate.html")
            categories = QuestionCategory.objects.all()#gets all the categories from the database for options in the <select> statement for the user to choose which category the new question belongs to
            context = { #dta passed to html template
                "categories" : categories,
                "currentUser" : User.objects.get(username = request.user.username),
                "issue" : issue,
            }
            return HttpResponse(template.render(context, request))
        else:
            return redirect("/")
    else:
        return redirect("accounts/login")

#backend processing for creating a new question
def QuestionCreateDo(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            try:
                #get post data from html form
                questionText = request.POST["questionText"]
                opt1 = request.POST["opt1"]
                opt2 = request.POST["opt2"]
                opt3 = request.POST["opt3"]
                opt4 = request.POST["opt4"]
                answer = request.POST["answer"]
                category = request.POST["category"]

                if answer == opt1 or answer == opt2 or answer == opt3 or answer == opt4:#only create a new question record if the correct answer matches one of the options
                
                    newQuestion = Question(questionText = questionText, opt1 = opt1, opt2 = opt2, opt3 = opt3, opt4 = opt4, answer =answer, questionCategory_id = category)
                    newQuestion.save()
                    #return HttpResponseRedirect(reverse("QuestionList"))
                    return redirect("/questions/list")
                else:
                    return redirect("/questions/add/?bad=true")#redirect to 'bad' url if answer does not match an option
            except:
                return redirect("QuestionCreate")
        else:
            return redirect("/")
    else:
        return redirect("accounts/login")


#page to delete a question. Question id is passed in url
def QuestionDelete(request, id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            #get question correpsonding to id and delete from databse
            question = Question.objects.get(id = id)
            try:
                question.delete()
                return HttpResponseRedirect(reverse("QuestionList"))
            except:
                return redirect("QuestionList")
        else:
            return redirect("/")
    else:
        return redirect("accounts/login")



#html form to create a new category
def addCategory(request): 
    if request.user.is_staff:
        template = loader.get_template("categorycreate.html")
        context = {#data passed to html template
            "currentUser" : User.objects.get(username = request.user.username)
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")
    
#background processing for when create category form submitted
def addCategoryDo(request):
    if request.user.is_staff:
        #get post data from form
        categoryName = request.POST["name"]
        level = request.POST["level"]

        try:
            #create new cateogry record
            newCategory = QuestionCategory(name = categoryName, level = level)
            newCategory.save()
            #create new studentCategory linking table records for each student
            students = Student.objects.all().values_list("id", flat=True)
            for student in students:
                newStudentCategory = StudentCategory(studentID_id = student, categoryID_id = newCategory.pk)
                newStudentCategory.save()
        except:
            pass
        return redirect("/questions/list")
    else:
        return redirect("/")


#page for html form to delete a category
def categoryDelete(request):
    if request.user.is_staff:
        categories = QuestionCategory.objects.all().values() #returns all category records from the database
        template = loader.get_template("categorydelete.html")
        context = {
            "currentUser" : User.objects.get(username = request.user.username),
            "categories" : categories,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

#backend processing for category delete form submissions
def categoryDeleteDo(request):
    if request.user.is_staff:
        #get post data from form
        category = request.POST["category"]
        #delete record from database
        c = QuestionCategory.objects.get(id=category)
        c.delete()
        return redirect("/questions/list")
    else:
        return redirect("/")



#html form to add a new teacher
def addTeacher(request):
    template = loader.get_template("addteacher.html")
    context = { #data passed to the html template
        "currentUser" : User.objects.get(username=request.user.username)
    }
    return HttpResponse(template.render(context, request))

#backend processing for add teacher form submission
def addTeacherDo(request):
    if request.user.is_staff:
        #get post data from html form
        fname = request.POST["first"]
        lastname = request.POST["last"]
        emailAddress = request.POST["ea"]
        pword = request.POST["pw"]
        pword = hashers.make_password(pword) #hash password before adding to database
        uname = request.POST["ea"]
        try:
            #create new user record and corresponding teacher record for the new teacher
            user = User(username = uname, password = pword, email = emailAddress, first_name = fname, last_name = lastname, is_staff = True)
            teacher = Teacher(first_name = fname, last_name = lastname, username = uname)
            user.save()
            teacher.save()
            return redirect("/")
        except:
            return redirect("addTeacher")
    else:
        return redirect("/")


#student pages



#student page to display all assignments they have been set    
def studentAssignmentList(request):
    if request.user.is_authenticated:
        me = Student.objects.get(username_id=request.user.username)
        uncompleteAssignments = StudentAssignment.objects.filter(completed = False, studentID_id = me.pk, isQuiz = False).values_list('assignmentID_id', flat=True).all()#returns a list of all IDs of assignments the student has not yet completed
        
        CompletedAssignments = StudentAssignment.objects.filter(completed = True, studentID_id = me.pk).values().all().order_by("-dateCompleted")#returns all StudentAssignment linking table records for all assignments completed, ordered by due date with most recent first
        #get how many completed and uncompleted assignments there are
        howMany = uncompleteAssignments.count()
        howMany2 = CompletedAssignments.count()
        #get assignment records for all assignments whose ids were returned in the uncompleteAssignments query
        assignments = Assignment.objects.filter(className_id = Class.objects.filter(name = me.className).values_list('id').first(), id__in = uncompleteAssignments).order_by("dueDate").all().values()
        #add data to all completed assignments
        for assignment in CompletedAssignments:
            assignment["title"] = Assignment.objects.filter(id = assignment["assignmentID_id"]).values_list('name', flat=True).first()
            assignment["grade"] = Grade.objects.filter(percentage__lte = assignment["score"], level = getGradeLevel(me)).values_list("grade", flat=True).order_by("-percentage").first()
            if assignment["score"] >= me.targetGrade.percentage:
                assignment["pass"] = True
            else:
                assignment["pass"] = False
        #add data to uncomplete assignments
        for assignment in assignments:
            assignment["questions"] = StudentQuestionAssignment.objects.filter(assignmentID_id = assignment["id"], studentID_id = me.pk).count()
            if assignment["dueDate"] <= datetime.date.today():
                assignment["overdue"] = True

        
        template = loader.get_template("studentassignmentlist.html")
        context = { #data passed to html template
            "currentUser" : User.objects.get(username=request.user.username),
            "assignments" : assignments,
            
            "completedAssignments" : CompletedAssignments,
            "me" : me,
            "howMany" : howMany,
            "howMany2" : howMany2,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")

#student page displaying assignment information. Assignment id is passed in url
def StudentAssignment2(request, id):
    if request.user.is_authenticated:
        yesCategories = None
        #get user and student objects correpsonding to the current user
        currentUser = User.objects.get(username = request.user.username)
        me = Student.objects.get(username_id = currentUser.username)

        #get studentAssignment object corresponding to the assignment id from the url and the current user's student id
        assignment = StudentAssignment.objects.filter(studentID_id = me.pk, assignmentID_id = id).values().first()

        #if assignment completed, display score, grade and list of questions showing which were answered correctly
        if assignment["completed"]:#type: ignore
            assignment["grade"] = Grade.objects.filter(percentage__lte = assignment["score"], level = getGradeLevel(me)).values_list("grade", flat=True).order_by("-percentage").first()#type: ignore
            questions = StudentQuestionAssignment.objects.filter(studentID_id=me.pk, assignmentID_id = id).values()#type: ignore
            for question in questions:
                
                question["questionText"] = Question.objects.filter(id=question["questionID_id"]).values_list("questionText", flat=True).first()
                #question["correct"] = StudentQuestionAssignment.objects.filter(studentID_id=me.pk, assignmentID_id=id, questionID_id = 
            if assignment["score"] >= me.targetGrade.percentage:#type: ignore
                assignment["pass"] = True#type: ignore
            else:
                assignment["pass"] = False#type: ignore
        else:
            #if assignment not completed, display the categories that are within the assignment
            questions = None
            questions = StudentQuestionAssignment.objects.filter(studentID_id=me.pk, assignmentID_id = id).values()#type: ignore
            categories = []

            for question in questions:
                x = Question.objects.filter(id=question["questionID_id"]).values_list("questionCategory_id", flat=True).first()
                if x not in categories:
                    categories.append(x)
            
            
            yesCategories = QuestionCategory.objects.filter(id__in = categories).values() #returns the category records associated with the categories in the assignment
            
        template = loader.get_template("studentassignment.html")
        myAssignment = Assignment.objects.get(id = id)#returns the assignment record correpsonding to the id in the url
        noOfQuestions = QuestionInAssignment.objects.filter(assignmentID_id = id).count() #get number of questions in the assignment
        context = { #data passed to HTML template
            "assignment" : myAssignment,
            "thismany" : noOfQuestions,
            "currentUser" : currentUser,
            "studentAssignment" : assignment,
            "questions" : questions,
            "categories" : yesCategories,

        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("accounts/login")


#student page to display a question in the assignment. Assignment id is passed in the url
def StudentAssignmentQuestion(request, id):
    if request.user.is_authenticated:
        template = loader.get_template("studentassignmentquestion.html")
        me = Student.objects.filter(username = request.user.username).values_list("id").first()#returns the student id of the current student
        
        myAssignment = Assignment.objects.get(id = id)#returns the assignment record corresponding to the id in the url
        howMany = StudentQuestionAssignment.objects.filter(assignmentID_id = id, studentID_id = me, studentAnswer__isnull = True).count() #returns the number of questions still to be answered in the assignment

        #No questions left to be answered
        if howMany == 0:
            #if the 'assignment' is just a quiz, redirect to quiz complete page. (quizzes and assignments stored in the same entity)
            if str(myAssignment.name) == "Quiz":
                    return redirect("/quiz/complete/" + str(id))
            else:
                #get the number of questions answered correctly by the student in the assignment
                noOfCorrectAnswers = StudentAssignment.objects.filter(studentID_id = me, assignmentID_id = id).values_list("noCorrectAnswers", flat = True)[0]

                #get the total number of questions in the assignment
                totalQuestions = QuestionInAssignment.objects.filter(assignmentID_id = id).count()
                #update the StudentAssignment record for the student and the assignment to include the score and date completed, and to mark the assignment as completed
                score = (noOfCorrectAnswers / totalQuestions) * 100
                sa = StudentAssignment.objects.get(assignmentID_id = id, studentID_id = me)
                sa.completed = True
                sa.dateCompleted = datetime.datetime.now().date()
                sa.score = score
                sa.save()
                
                #update the Student record to update their average, total questions answered and number of correct answers
                student = Student.objects.get(username_id = request.user.username)
                student.noOfCorrectAnswers += noOfCorrectAnswers
                student.totalQuestionsAnswered += totalQuestions
                student.average = round(((student.noOfCorrectAnswers / student.totalQuestionsAnswered) * 100), 2)
                student.save()

                return redirect("/student/assignments/" + str(id))#redirect the student to the student's assignment info page for the assignment 
        else:
            #Questions left to be answered
            try:
                #gets the question id for the next question
                myQuestion = StudentQuestionAssignment.objects.filter(studentAnswer__isnull = True, assignmentID_id = id, studentID_id = me ).values_list("questionID_id", flat=True).first()
                #gets a list of question ids for all the questions in the assignment, and uses linear search to find the question number of the next question.
                questions = StudentQuestionAssignment.objects.filter( assignmentID_id = id, studentID_id = me ).values_list("questionID_id", flat=True).order_by("id")
                questionNo = None
                for x in range(len(questions)):
                    if questions[x] == myQuestion:
                        questionNo = x+1
                   
                #get the question record corresponding to the next question
                myData = Question.objects.get(pk = myQuestion)

                context = { #data passed to HTMl template
                    "assignment" : myAssignment,
                    "question" : myData,
                    "questionNo" : questionNo,
                    "currentUser" : User.objects.get(username=request.user.username),
                }

                return HttpResponse(template.render(context, request))
            except:
                #(RDC?)If assignment is a quiz, redirect to quiz complete page
                if str(myAssignment.name) == "Quiz":
                    return redirect("/quiz/complete/" + str(id))
                else:#no questions left so redirect to the results page
                    return redirect("/student/assignments/" + str(id))
                
    else:
        return redirect("accounts/login")

#backend processing for the studnet's answer to a question. Assignment id and studnet's answer are passed in the url
def StudentAnswerProcessing(request, assignmentid, answer):
    if request.user.is_authenticated:
        
        me = Student.objects.filter(username = request.user.username).values_list("id").first()
        try:
            #gets the question id for the question
            myQuestion = StudentQuestionAssignment.objects.filter(assignmentID_id = assignmentid, studentID_id = me, studentAnswer__isnull = True).values_list("questionID_id", flat=True).first()
            #get the Question and StudentQuestionAssignment records corresponding to the question id returned in the previous query
            myData = Question.objects.get(pk = myQuestion)
            studentQAssignment = StudentQuestionAssignment.objects.get(assignmentID_id = assignmentid, studentID_id = me, questionID_id = myQuestion)
            #get the studentAssignment record correpsonding to the current student and assignment
            studentInAssignment = StudentAssignment.objects.get(assignmentID_id = assignmentid, studentID_id = me)
            #get the StudentCategory record correposnding to the category of the question and the current student
            myCategory = StudentCategory.objects.get(categoryID_id = myData.questionCategory.pk, studentID_id = me)
            myCategory.total += 1
            #save answer data to database
            if myData.answer == answer:#question answered correctly
                myCategory.correct +=1
                studentQAssignment.studentAnswer = answer
                studentQAssignment.correct = True
                studentQAssignment.save()
                studentInAssignment.noCorrectAnswers = studentInAssignment.noCorrectAnswers + 1
                studentInAssignment.save()
                myCategory.average = round(((myCategory.correct / myCategory.total)*100), 2)
                myCategory.save()
                return redirect("/student/assignments/" + str(assignmentid) + "/question/correct")
            else: #question not answered correctly
                studentQAssignment.studentAnswer = answer
                studentQAssignment.save()
                myCategory.average = round(((myCategory.correct / myCategory.total)*100), 2)
                myCategory.save()
                return redirect("/student/assignments/" + str(assignmentid) + "/question/incorrect")

            
        except:
            pass
    else:
        return redirect("accounts/login")

def questionCorrect(request, id):#page to display correct screen to inform the user they have answred correctly
    if request.user.is_authenticated:
        template = loader.get_template("correct.html")
        context = {
            "currentUser": User.objects.get(username=request.user.username),
            "id" : id,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/accounts/login")

def questionIncorrect(request, id):#page to display incorrect screen to inform the user they have answred incorrectly
    if request.user.is_authenticated:
        template = loader.get_template("incorrect.html")
        context = {
            "currentUser": User.objects.get(username=request.user.username),
            "id" : id,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/accounts/login")


#student page to start a quiz
def QuizStart(request):
    if request.user.is_authenticated: #non authernticated users get redirected to the login page
        me = Student.objects.filter(username = request.user.username).values_list("id", flat=True).first() #get student id for current user
        categories = QuestionCategory.objects.all().values()#returns all category records from database
        try:#delete any previous quizzes from the database... these get stored in the assignments table while in progress then deleted afterwards
            prevQuiz = StudentAssignment.objects.filter(studentID_id = me, isQuiz = True).values_list("assignmentID_id").first()[0] #type: ignore
            
            quiz = Assignment.objects.get(id = prevQuiz)
            
            quiz.delete()
        except:pass
        template = loader.get_template("quizstart.html")
        context = { #data passed to HTML template
            "categories" : categories,
            "currentUser" : User.objects.get(username = request.user.username),
        }
        return HttpResponse(template.render(context, request))
        
    else:
        return redirect("accounts/login")

#backgorund processing for once the start quiz button has been pressed
def QuizStartDo(request):
    if request.user.is_authenticated:
        categories = QuestionCategory.objects.all().values_list("id", flat=True)#get all category ids
        yesCategories = []
        for category in categories:#get which categories the user selected to be a part of the quiz and append the ids to a list
            
            try:
                isCategorySelected = request.POST["category" + str(category)]
                if isCategorySelected: 
                    yesCategories.append(category)
            except:
                pass
        
        if len(yesCategories) == 0:
            return redirect("/quiz/start")#if no categories selected redirect to the start page
        else:
            myStudent = Student.objects.filter(username = request.user.username).values_list("id", flat=True).first()
            newAssignment = Assignment.objects.create(name = "Quiz")#create temporary assignment record for the quiz and add to database
            newAssignment.save()
            newStudentAssignment = StudentAssignment.objects.create(assignmentID_id = newAssignment.pk, studentID_id = myStudent, isQuiz = True)
            newStudentAssignment.save()
            #create list of question ids and add all question ids for questions in the categories selected by the user to this list
            validQuestions = []
            for category in yesCategories:
                myQuestions = Question.objects.filter(questionCategory_id = category).values_list("id", flat=True)
                for question in myQuestions:
                    validQuestions.append(question)
            
            numberOfQuestions = request.POST["questions"]#get the number of questions the user selected to be in the quiz
            yesQuestions = []
            #get a random question id from the list of question ids in the categories selected by the user and create the corresponding lionking table records. Repeat for the number of questions the user chose to be in the quiz
            for i in range(int(numberOfQuestions)):
                if len(validQuestions) != 0:
                    listIndex = random.randint(0, len(validQuestions) - 1)
                    newQuestionInAssignment = QuestionInAssignment.objects.create(questionID_id = validQuestions[listIndex], assignmentID_id = newAssignment.pk)
                    newQuestionInAssignment.save()
                    newStudentQuestionAssignment = StudentQuestionAssignment.objects.create(questionID_id = validQuestions[listIndex], studentID_id = myStudent, assignmentID_id = newAssignment.pk)
                    newStudentQuestionAssignment.save()
                    yesQuestions.append(validQuestions[listIndex])
                    del validQuestions[listIndex]#remove id from the list once the question has been added to the quiz
            
            return redirect("/student/assignments/" + str(newAssignment.pk) + "/question")#redirect to the question page

    else:
        return redirect("accounts/login")

#page to display the quiz completion screen. ID of assignment record for quiz is passed in url
def QuizComplete(request, id):
    assignmentid = id
    template = loader.get_template("quizcomplete.html")

    if request.user.is_authenticated:
        me = Student.objects.filter(username = request.user.username).values_list("id").first()#get student id for current user
        try:
            
            myAssignment = Assignment.objects.get(id = assignmentid) #get assignment record correpsonding to assignment id passed in url
            noOfCorrectAnswers = StudentAssignment.objects.filter(studentID_id = me, assignmentID_id = assignmentid).values_list("noCorrectAnswers", flat = True)[0]#get number of questions the student answered correctly in the quiz
            totalQuestions = QuestionInAssignment.objects.filter(assignmentID_id = assignmentid).count()#get the total number of QuestionInAssignment records for the quiz to find out how many questions were in the quiz.
            score = round(((noOfCorrectAnswers / totalQuestions) * 100), 2)#get the percentage the student got in the quiz

            #update student record to add the data from the quiz
            me = Student.objects.get(username_id = request.user.username)
            me.quizCorrectAnswers += noOfCorrectAnswers
            me.quizQuestionsAnswered += totalQuestions
            me.quizAverage = round(((me.quizCorrectAnswers / me.quizQuestionsAnswered) * 100), 2)
            me.noOfQuizzesCompleted += 1

            #get question text and correct answer for each question to be passed to HTML page
            questions = StudentQuestionAssignment.objects.filter(studentID_id = me, assignmentID_id = assignmentid).values()
            for question in questions:
                question["correctAnswer"] = Question.objects.filter(id = question["questionID_id"]).values_list("answer", flat = True)[0]
                question["questionText"] = Question.objects.filter(id = question["questionID_id"]).values_list("questionText", flat = True)[0]

            try:
                me.save()
            except:
                pass
            myAssignment.delete()#delete the temporary assignment record for thr quiz
            
            context = { #data to be passed to HTML template
                "assignment" : myAssignment,
                "score" : score,
                "currentUser" : User.objects.get(username = request.user.username),
                "questions" : questions,
            }
            return HttpResponse(template.render(context, request))
        except:
            return redirect("/")
    else:
        return redirect("accounts/login")


#page to display the student leaderboard
def leaderboard(request):
    if request.user.is_authenticated:
        template = loader.get_template("leaderboard.html")
        mode = request.POST.get("mode", "noc") #leaderboard has different sorting modes. noc = number of correct answers, avg = average, tqa = total questions answered
        myClass = str(request.POST.get("class", "all"))
        if myClass == "all": #get all student records if no class is specified
            students = Student.objects.all().values()
        else:#get student records for the class specified in the leaderboard page
            students = Student.objects.filter(className = myClass).values()

        #assign the relevant data determined by the sorting mode to the "data" flag for each student, so they can be sorted by this data flag
        if mode == "avg":
            
            for student in students:
                student["data"] = student["average"]
        elif mode == "tqa":
           
            for student in students:
                student["data"] = student["totalQuestionsAnswered"] + student["quizQuestionsAnswered"]
        else:
            
            for student in students:
                student["data"] = student["noOfCorrectAnswers"] + student["quizCorrectAnswers"]
        i = 1
        j = 1
        #bubble sort to get the student records in the leaderboard in the correct order
        students = list(students)
        for a in range(len(students) - 1):
            for b in range(len(students) - 1):
                if students[b]["data"] < students[b+1]["data"]:
                    tmp = students[b]
                    students[b] = students[b+1]
                    students[b+1] = tmp

       
        try:
            #get the index for each student in the leaderboard (so multiple students of the same rank are given the same index in the leaderboard)
            prevstudent = students[0]
            for student in students:
                if student["data"] == prevstudent["data"] and i != 1:
                    i = i - 1
                student["row"] = j
                student["index"] = i
                i+=1
                j+=1
                prevstudent = student

        except:
            pass

        classes = Class.objects.all().values() #get all class records to be passed to the html form as options in the select class box
        context = { #data passed to html form
            "currentUser" : User.objects.get(username=request.user.username),
            "students" : students,
            "mode" : mode,
            "classes" : classes,
            "myClass" : myClass,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect("/")



