import sys, json, csv
import concurrent.futures as futures
from datetime import datetime
import utility.airtable_manager as airtable
import sheets.LO_OverChallengesWeeks as s1
import sheets.LO_OverDaysNotPersistent as s2
import sheets.LO_OverDaysPersistent as s3
import sheets.StudentEvaluations_OverDaysNotPersistent as s4
import sheets.UserTypes as s5
import sheets.LO_OverDaysNotPersistentForSubSamples as s6
import sheets.ExportLog as s7
import shutil




if __name__ == "__main__":

    sys.stdout.write("Getting data...\n")
    # Getting Data from Airtable, Function returns
    # Students_data = Every LO Assemssment one by one from each unique student.
    # Filtered Students = Unique students whole data
    
    students_data, uniqueStudents = airtable.getStudentsContent()
    users, checkPointTickersLearners, autonomousUsersLearners, enthusiastUsersLearners, excludedUsers, outdatedExcludedUsers, nonUsersExcludedUsers,averageNumberOfEvaluation,averageSessionByStudents = airtable.createAllSubsamples(uniqueStudents)
    
    #TODO: generate data for subsets. students_data is basically useless.

    
    OUTPUT_PATH = 'output/'
    
   
   #-----------------------OVER DAYS NOT PERSISTENT---------------
    SHEET1_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_AllUsers_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(uniqueStudents)}" + '.tsv'
    SHEET2_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_Users_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(users)}" + '.tsv'
    SHEET3_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_Users_CheckPointTicker_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(checkPointTickersLearners)}" + '.tsv'
    SHEET4_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_Users_Enthusiast_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(enthusiastUsersLearners)}" + '.tsv'
    SHEET5_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_Users_Autonomous_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(autonomousUsersLearners)}" + '.tsv'
    SHEET6_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_ExcludedUsers_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(excludedUsers)}" + '.tsv'
    SHEET7_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_ExcludedUsers_NonUsers_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(nonUsersExcludedUsers)}" + '.tsv'
    SHEET8_OUTPUT_FILE = 'LO_OverDaysNotPersistent/LO_OverDaysNotPersistent_ExcludedUsers_OutDated_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(outdatedExcludedUsers)}" + '.tsv'

    #----------------------OVER DAYS PERSISTENT------------------------
    SHEET9_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_AllUsers_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(uniqueStudents)}" + '.tsv'
    SHEET10_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_Users_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(users)}" + '.tsv'
    SHEET11_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_Users_CheckPointTicker_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(checkPointTickersLearners)}" + '.tsv'
    SHEET12_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_Users_Enthusiast_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(enthusiastUsersLearners)}" + '.tsv'
    SHEET13_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_Users_Autonomous_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(autonomousUsersLearners)}" + '.tsv'
    SHEET14_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_ExcludedUsers_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(excludedUsers)}" + '.tsv'
    SHEET15_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_ExcludedUsers_NonUsers_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(nonUsersExcludedUsers)}" + '.tsv'
    SHEET16_OUTPUT_FILE = 'LO_OverDaysPersistent/LO_OverDaysPersistent_ExcludedUsers_Outdated_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(outdatedExcludedUsers)}" + '.tsv'

    #----------------------STUDENT EVALUATION NOT PERSISTENT--------------------
    SHEET17_OUTPUT_FILE = 'StudentEvaluations_OverDaysNotPersistent_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(uniqueStudents)}" + '.tsv'
    SHEET18_OUTPUT_FILE = 'UserTypes_' + datetime.now().strftime("%Y|%m|%d_") + f"{len(uniqueStudents)}" + '.tsv'
   
    SHEET19_OUTPUT_FILE = 'ExportLog_'+ datetime.now().strftime("%Y|%m|%d_") + '.txt'
    
    overDaysNotPersistentDictionary = {
        SHEET2_OUTPUT_FILE:users,
        SHEET3_OUTPUT_FILE:checkPointTickersLearners,
        SHEET4_OUTPUT_FILE:enthusiastUsersLearners,
        SHEET5_OUTPUT_FILE:autonomousUsersLearners,
        SHEET6_OUTPUT_FILE:excludedUsers,
        SHEET7_OUTPUT_FILE:nonUsersExcludedUsers,
        SHEET8_OUTPUT_FILE:outdatedExcludedUsers
         }
    overDaysPersistentDictionary ={
        SHEET9_OUTPUT_FILE:uniqueStudents,
        SHEET10_OUTPUT_FILE:users,
        SHEET11_OUTPUT_FILE:checkPointTickersLearners,
        SHEET12_OUTPUT_FILE:enthusiastUsersLearners,
        SHEET13_OUTPUT_FILE:autonomousUsersLearners,
        SHEET14_OUTPUT_FILE:excludedUsers,
        SHEET15_OUTPUT_FILE:nonUsersExcludedUsers,
        SHEET16_OUTPUT_FILE:outdatedExcludedUsers
    }


 
    sys.stdout.write("\nGenerating LO_OverDaysNotPersistent sheet for all Learners ...")
    second_sheet = s2.LO_OverDaysNotPersistent(OUTPUT_PATH + SHEET1_OUTPUT_FILE, students_data.copy())




with futures.ThreadPoolExecutor(max_workers=22) as executor:
    for key in overDaysPersistentDictionary:
        sys.stdout.write(f"\nGenerating LO_OverDaysPersistent sheet  {key} ...")
        executor.submit(s3.LO_OverDaysPersistent,(OUTPUT_PATH + key),overDaysPersistentDictionary[key].copy())
    for key in overDaysNotPersistentDictionary:
        sys.stdout.write(f"\nGenerating LOs_OverDaysNotPersistent sheet {key} ...")
        executor.submit(s6.LO_OverDaysNotPersistentForSubSamples,(OUTPUT_PATH + key),overDaysNotPersistentDictionary[key].copy())

    sys.stdout.write("\nGenerating StudentEvaluations_OverDaysNotPersistent sheet for all Learners ...")
    executor.submit(s4.StudentEvaluations_OverDaysNotPersistent,(OUTPUT_PATH + SHEET17_OUTPUT_FILE),uniqueStudents.copy())

    sys.stdout.write("\nGenerating UserTypes sheet..")
    executor.submit(s5.UserTypes,(OUTPUT_PATH + SHEET18_OUTPUT_FILE),uniqueStudents.copy())

    sys.stdout.write("\nGeneratin Scope and Sequence ..")
    executor.submit(shutil.copy(r"input/Challenges.csv",OUTPUT_PATH+"ScopeAndSequence.csv"))

    sys.stdout.write("\nGeneratin Documentation ..")
    executor.submit(shutil.copy(r"input/Documentation.pdf",OUTPUT_PATH+"Documentation.pdf"))


sys.stdout.write("\nGenerating ExportLog sheet..")
s7.ExportLog(("output/" + SHEET19_OUTPUT_FILE),("output/"+ SHEET18_OUTPUT_FILE),len(uniqueStudents),averageNumberOfEvaluation,averageSessionByStudents)
