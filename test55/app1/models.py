from django.db import models
from django.contrib.auth.models import User


def getDefaultGrade(): #function to return the default grade to use in the ForeignKey field in line 37 if no grade is selected 
        return Grade.objects.get(id=16).pk

class Grade(models.Model):
    grade = models.CharField(max_length=200)
    percentage = models.IntegerField(default=0)
    level = models.IntegerField(default = 1) # 1 for A level, 2 for gcse, 3 for ks3 (yes this is important)
    class Meta:
        unique_together = ('grade',)
    def __str__(self):
        return f"{self.grade}"
    
class Class(models.Model):
    name = models.CharField(max_length=200, unique=True)
    class Meta:
        verbose_name_plural ="Classes"
    def __str__(self):
        return self.name
    
class Student(models.Model):
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    noOfCorrectAnswers = models.IntegerField(default=0)
    totalQuestionsAnswered = models.IntegerField(default=0)
    quizQuestionsAnswered = models.IntegerField(default=0)
    quizCorrectAnswers = models.IntegerField(default=0)
    quizAverage = models.FloatField(default = 0)
    noOfQuizzesCompleted = models.IntegerField(default = 0)
    average = models.FloatField(default = 0)
    username = models.ForeignKey(User, to_field = "username", null = False, on_delete=models.CASCADE)
    className = models.ForeignKey(Class, to_field = "name", null =True, on_delete=models.SET_NULL)
    targetGrade = models.ForeignKey(Grade, default=getDefaultGrade, on_delete=models.CASCADE)
    
    def __str__(self):
       return f"{self.first_name} {self.last_name}"
    
class Teacher(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200)


    
class Assignment(models.Model):
    name = models.CharField(max_length=200)
    dueDate = models.DateField(null=True)
    className = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return f"{self.name} | {self.className}"

class QuestionCategory(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField(default = 1) # 1 for A level, 2 for gcse, 3 for ks3 (yes this is important)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name
    
class Question(models.Model):
    questionText = models.CharField(max_length=200)
    questionCategory = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, default = None) 
    opt1 = models.CharField(max_length=200)
    opt2 = models.CharField(max_length=200)
    opt3 = models.CharField(max_length=200)
    opt4 = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    def __str__(self):
        return self.questionText
    
class QuestionInAssignment(models.Model):
    questionID = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    assignmentID = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True)
    class Meta:
        unique_together = ('questionID', 'assignmentID')
    def __str__(self):
        return f"{self.questionID} | {self.assignmentID}"
    
class StudentAssignment(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    assignmentID = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)
    noCorrectAnswers = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    dateCompleted = models.DateField(null = True, default = None, auto_now=False, auto_now_add=False)
    isQuiz = models.BooleanField(default=False)
    class Meta:
        unique_together = ('studentID', 'assignmentID')
    def __str__(self):
        return f"{self.studentID} | {self.assignmentID} | {self.score}"

class StudentQuestionAssignment(models.Model):
    studentAnswer = models.CharField(max_length=200, null=True)
    correct = models.BooleanField(default=False)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    questionID = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    assignmentID = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True)#SET_NULL so that question data wont be deleted if assignment is deleted. This data used for calulating StudentCategory data.
    class Meta:
        unique_together = ('studentID', 'questionID', 'assignmentID')
    def __str__(self):
        return f"{self.studentID} | {self.questionID} | {self.assignmentID} | {self.studentAnswer}"

class StudentCategory(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    categoryID = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True)
    total = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    class Meta:
        unique_together = ('studentID', 'categoryID')

class TeacherInClass(models.Model):
    teacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classID = models.ForeignKey(Class, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('teacherID', 'classID')
                                  