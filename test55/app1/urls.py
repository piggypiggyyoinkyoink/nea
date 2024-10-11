from django.urls import path, include
from . import views


urlpatterns = [
    #login and homepages
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='home'),
    path("student", views.student, name='student'),
    path("staff", views.staff, name = "staff"),
    path("changepassword", views.changePassword, name = "changePassword"),
    path("changepassword/", views.changePassword, name = "changePassword"),
    path("changepassworddo", views.changePasswordDo, name = "changePasswordDo"),



    #teacher pages
    path("users/list", views.studentList, name = "studentList"),
    path("users/list/", views.studentList, name = "studentList"),
    path("users/list/search", views.studentListSearch, name = "studentListSearch"), 

    path("users/details/<int:id>", views.studentDetails, name = "studentDetails"),
    path("users/details/update/<int:id>", views.updateClassStudent, name = "update2"),
    path("users/details/update/updaterecord/<int:id>", views.updateClassStudentDo, name = "update3"),
    path("users/updatetargetgrade/<int:id>", views.updateTargetGrade , name = "updatetargetGrade"),
    path("users/updatetargetgrade/<int:id>/", views.updateTargetGrade , name = "updatetargetGrade"),
    path("users/pwreset/<int:id>", views.resetStudentPassword, name = "resetStudentPassword"),

    path("users/add", views.add, name = "add"),
    path("users/add/", views.add, name = "add"),
    path("users/addrecord", views.addrecord, name = "addrecord"),
    path("users/addtargetgrade/<int:id>", views.studentTargetGrade , name = "targetGrade"),
    path("users/addrecordtargetgrade/<int:studentid>", views.StudentTargetGradeDo, name = "targetGradeDo"),

    path("users/details/delete/<int:id>", views.deleteStudentDo, name = "deleteStudent"),
    

    path("users/addteacher", views.addTeacher, name = "addTeacher"),
    path("users/addteacherdo", views.addTeacherDo, name = "addTeacherDo"),



    path("class/list", views.classList, name = "classList"),
    path("class/details/<int:id>", views.classDetails, name = "classDetails"),

    path("class/add", views.addclass, name = "addclass"),
    path("class/addrecord", views.addrecordclass, name = "addrecordclass"),

    path("class/delete/<int:id>", views.deleteClass, name = "deleteclass"),
    
    

    path("assignments/list", views.AssignmentList, name = "AssignmentList"),
    path("assignments/details/<int:id>", views.AssignmentDetails, name = "AssignmentDetails"),
    path("assignments/details/duedate/<int:id>", views.updateDueDate, name = "updateDueDate"),
    path("assignments/details/update/<int:id>", views.AddQuestions, name = "updateAssignment"),
    path("assignments/details/update/<int:id>/", views.AddQuestions, name = "updateAssignment"),
    path("assignments/details/update/updaterecord/<int:id>", views.AddQuestionsDo, name = "updateAssignmentRecord"),
    path("assignments/details/scores/<int:assignmentid>/<int:studentid>", views.assignmentScores, name = "assignmentScores"),

    path("assignments/add", views.AssignmentCreate, name = "addAssignment"),
    path("assignments/add/", views.AssignmentCreate, name = "addAssignment"),
    path("assignments/addrecord", views.AssignmentCreateDo, name = "addAssignmentRecord"),
    
    path("assignments/delete/<int:id>", views.AssignmentDelete, name = "deleteAssignment"),


    
    path("questions/list", views.QuestionList, name = "QuestionList"),  

    path("questions/details/<int:id>", views.questionDetails, name = "questionDetails"),#type:ignore
    path("questions/update/<int:id>", views.QuestionUpdate, name = "QuestionUpdate"),
    path("questions/update/updaterecord/<int:id>", views.QuestionUpdateDo, name = "QuestionUpdateRecord"), #type: ignore

    path("questions/add", views.QuestionCreate, name = "QuestionCreate"),
    path("questions/add/", views.QuestionCreate, name = "QuestionCreate"),
    path("questions/addrecord", views.QuestionCreateDo, name = "QuestionCreateRecord"),

    path("questions/delete/<int:id>", views.QuestionDelete, name = "QuestionDelete"),


    path("categories/add", views.addCategory, name = "addCategory"),
    path("categories/addrecord", views.addCategoryDo, name = "addCategoryDo"),

    path("categories/delete", views.categoryDelete, name = "deleteCategory"),
    path("categories/deleterecord", views.categoryDeleteDo, name = "deleteCategory"),


    #student pages
    path("student/assignments/list", views.studentAssignmentList, name = "studentAssignmentList"),

    path("student/assignments/<int:id>", views.StudentAssignment2, name = "studentAssignment"),
    
    path("student/assignments/<int:id>/question", views.StudentAssignmentQuestion, name = "studentAssignmentQuestion"), 
    path("student/assignments/<int:assignmentid>/<str:answer>", views.StudentAnswerProcessing, name = "studentAnswerProcessing"),#type:ignore
    path("student/assignments/<int:id>/question/correct", views.questionCorrect, name = "correct"), 
    path("student/assignments/<int:id>/question/incorrect", views.questionIncorrect, name = "incorrect"), 

    
    path("quiz/start", views.QuizStart, name = "QuizStart"),
    path("quiz/startquiz", views.QuizStartDo, name = "QuizStartDo"), #type: ignore
    path("quiz/complete/<int:id>", views.QuizComplete, name = "QuizComplete"),
    
    
    
    path("leaderboard", views.leaderboard, name = "leaderboard"),
    
]