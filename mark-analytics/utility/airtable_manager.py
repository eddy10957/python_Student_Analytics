import sys, json, csv
import requests, json
from datetime import datetime, timedelta

TOKEN = ''

def _getData(offset : str):

    url = ""

    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Type': 'application/json'
    }

    params = {}

    if offset != "" :
        params = {'offset': offset}

    response = requests.request("GET", url,params=params, headers=headers)

    return response.json()

def _deleteReplicatedStudents(students: []):
    addedStudents = []

    # From students passed to this function we create a dicortionary with his data
    # then copy value in a temporary array
    for index in range(len(students)):
        tempDictionary = {}
        tempDictionary["index"] = students[index]
        tempDictionary["createdTime"] = students[index]["date"]
        tempDictionary["studentID"] = students[index]["fields"]["ID"]
        addedStudents.append(tempDictionary)

    tempArray = addedStudents.copy()
    indexOfBiggest = {}
    dateOfBiggest = {}
    for student in addedStudents:
        for student2 in addedStudents:
            # If two studentsID match
            if student["studentID"] == student2["studentID"]:
                # IF the studentID is in indexOfBiggest (means not the first time finding this ID)
                if student["studentID"] in indexOfBiggest.keys():
                    # If the found record of the same student has a created time bigger then the previous date found from the same student ID
                    if student2["createdTime"] > dateOfBiggest[student2["studentID"]]:
                        # New indexOfBiggest based on the new occurency found
                        indexOfBiggest[student2["studentID"]] = student2["index"]
                        # New dateOfBiggest based on the new occurency found
                        dateOfBiggest[student["studentID"]] = student2["createdTime"]
                # If student is not inside indexOfBiggest (means first time finding this ID)
                # And student2 it's the last created        
                elif student["createdTime"] < student2["createdTime"]:
                    # New indexOfBiggest based on the new occurency found
                    indexOfBiggest[student["studentID"]] = student2["index"]
                    # New dateOfBiggest based on the new occurency found
                    dateOfBiggest[student["studentID"]] = student2["createdTime"]

                # If student is not inside indexOfBiggest (means first time finding this ID)
                # And student1 it's the last created 
                else:
                    # New indexOfBiggest based on the new occurency found
                    indexOfBiggest[student["studentID"]] = student["index"]
                    # New dateOfBiggest based on the new occurency found
                    dateOfBiggest[student["studentID"]] = student["createdTime"]

    returnArray = []
    for key in indexOfBiggest.keys():
        returnArray.append(indexOfBiggest[key])

    #Returns the last data sent from every student deleting duplicates
    return returnArray
    

def getStudentsContent():
    dataArray = []
    allStudents = []
    rawDataArray = []

    # Raw Data from airtable with all fields
    studentsData = _getData("")

    # Only data from "records" field. (So we exclude "offset" field)
    # "offset" field cointains a code to retrive the other data.
    # Unfortunately Airtable has a limit on records you can retrive in one call,
    # They use offset to give you some sort of link to the next 100 data.
    allStudents += studentsData["records"]

    while "offset" in studentsData.keys():
        # Taking the rest of the data until there's no more offset.
        studentsData = _getData(studentsData["offset"])
        allStudents += studentsData["records"]

    for student in allStudents:
        # Make date clear
        strtime = student["createdTime"][:-5].replace("T", " ")
        # From string to date time object
        date_time_obj = datetime.strptime(strtime, '%Y-%m-%d %H:%M:%S')
        # Creating the date fiels and appending it to every data retrived from airtable ( only record field)
        student["date"] = date_time_obj

    # Removes duplicates
    filteredStudents = _deleteReplicatedStudents(allStudents)

    for student in filteredStudents:
        # Crates and array with only unique students taking only "fields" and "data" fields
        rawDataArray.append(student["fields"]["data"])

    for rawData in rawDataArray:
        # Kinda useless this but previous team loves to insert "peppe" variable everywhere
        # Who am I to remove their beloved peppe?
        # Each RawData is a student, Each student is a Peppe
        peppe = rawData
        # Transforms data/peppe in a json object
        json_object = json.loads(peppe)
        # Array of json objects, adds in this array every assessment one by one, no students identification
        dataArray+=json_object
        
    #sys.stdout.write(dataArray)
    #sys.stdout.write(f"@@@@@@ {filteredStudents[0]['fields']}" )

    return dataArray, filteredStudents;

# Function takes the unique students data, a threshold in oder get different subsamples based on threshold.
# aboveAndBelow is a boolean used to apply the threshold either above and below the average
# dateToStop is used to subsampling date by date
def subSamplingUsers(studentsData, threshold, aboveAndBelow = False, dateToStop = -1):
    allStudentsSessionsContainer = []
    subSampleStudentArray = []
    if studentsData == []:
        return [] , 0
    
    def addEmptyDate(beginning):
        dates = []
        current = beginning
        now = datetime.now()
        timestamp = datetime.timestamp(now)

        while current < (timestamp):
            dates.append(current) 
            current += 24*60*60
            dt_object = datetime.fromtimestamp(current)
            if dt_object.hour == 1:
                current -= 1*60*60
            elif dt_object.hour == 23:
                current += 1*60*60

        return dates

    data = {}

    tempContainer = {}

    # Scrollig for every students data
    for studentData in studentsData:

        # This is the array of LOs evaluated by the student.
        data = json.loads(studentData['fields']['data'])

        for LO in data:
            #we take the day of every evaluation to find the day of the first and last evaluation
            for evaluation in LO['eval_date']:
                if evaluation not in tempContainer.keys():
                    tempContainer[evaluation] = 0
                tempContainer[evaluation] += 1

    for key in sorted(tempContainer.keys()):
        dt_object = datetime.fromtimestamp(key)
        # We check if tere are some problem in the time structure ( some students may have different time zone )
        if dt_object.hour != 0:
            newKey = key - (dt_object.hour) * 60 * 60
            tempContainer[newKey] = tempContainer[key]
            del tempContainer[key]

    beginning = min(tempContainer.keys()) # Timestamp of the first evaluation
    end = max(tempContainer.keys()) # Timestamp of the last evaluation

    dates = addEmptyDate(beginning) # We generate an array of datas from the date of the first evaluation to the day of the last evaluation considering the daylight savings time for avoid errors

    if  dateToStop == -1:
        for studentData in studentsData:
            studentSessionContainer = []
            # For every dates from the start of the academy to now check how many evaluations per day done by single student
            for date in dates:
                evaluationPerDay = 0
                LOs = json.loads(studentData['fields']['data'])
                # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                for LO in LOs:
                    if date in LO['eval_date']:
                        evaluationPerDay += 1
                        # If found at leaste one evaluation for that day I'm ok with it and skip to next day
                        break
                # Append the value for that day
                studentSessionContainer.append(evaluationPerDay)
            # Append the value of the sum all session(so 1 if performed at least one evaluation) done by one student in a conatiner
            allStudentsSessionsContainer.append(sum((studentSessionContainer)))
        # Calculate the average sessions done by students    
        averageSessionByStudents = sum(allStudentsSessionsContainer)/len(studentsData)
        # if we want above and below
        if aboveAndBelow:
            # the minimum value is calculated the average minus the threshold %
            minBoundsAverage = averageSessionByStudents - (averageSessionByStudents * threshold / 100)
            maxBoundAverage = averageSessionByStudents + (averageSessionByStudents * threshold / 100)
            for studentData in studentsData:
                studentSessionContainer = []
                # For every dates from the start of the academy to now check how many evaluations per day done by single student
                for date in dates:
                    evaluationPerDay = 0
                    LOs = json.loads(studentData['fields']['data'])
                    # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                    for LO in LOs:
                        if date in LO['eval_date']:
                            evaluationPerDay += 1
                            # If found at leaste one evaluation for that day I'm ok with it and skip to next day
                            break
                    studentSessionContainer.append(evaluationPerDay)
                
                if sum(studentSessionContainer) in range(round(minBoundsAverage),round(maxBoundAverage)):
                    print(f'il valore è passato con {sum(studentSessionContainer)}  min bound {round(minBoundsAverage)} e max bound di {round(maxBoundAverage)}')
                    subSampleStudentArray.append(studentData)

            return subSampleStudentArray,averageSessionByStudents
        else:
            maxBoundAverage = averageSessionByStudents + (averageSessionByStudents * threshold / 100)
            for studentData in studentsData:
                studentSessionContainer = []
                # For every dates from the start of the academy to now check how many evaluations per day done by single student
                for date in dates:
                    evaluationPerDay = 0
                    LOs = json.loads(studentData['fields']['data'])
                    # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                    for LO in LOs:
                        if date in LO['eval_date']:
                            evaluationPerDay += 1
                            # If found at least one evaluation for that day I'm ok with it and skip to next day
                            break
                    studentSessionContainer.append(evaluationPerDay)
                if sum(studentSessionContainer) > maxBoundAverage:
                    print(f'il valore è passato con {sum(studentSessionContainer)} su max bound di {round(maxBoundAverage)}')
                    subSampleStudentArray.append(studentData)

            return subSampleStudentArray,averageSessionByStudents
    else:
        for studentData in studentsData:
            studentSessionContainer = []
            # For every dates from the start of the academy to now check how many evaluations per day done by single student
            for date in dates:
                evaluationPerDay = 0
                LOs = json.loads(studentData['fields']['data'])
                # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                for LO in LOs:
                    if date in LO['eval_date']:
                        evaluationPerDay += 1
                        # If found at leaste one evaluation for that day I'm ok with it and skip to next day
                        break
                # Append the value for that day
                studentSessionContainer.append(evaluationPerDay)
                if date == dateToStop:
                    break
            # Append the value of the sum all session(so 1 if performed at least one evaluation) done by one student in a conatiner
            allStudentsSessionsContainer.append(sum((studentSessionContainer)))
        # Calculate the average sessions done by students    
        averageSessionByStudents = sum(allStudentsSessionsContainer)/len(studentsData)
        # if we want above and below
        if aboveAndBelow:
            # the minimum value is calculated the average minus the threshold %
            minBoundsAverage = averageSessionByStudents - (averageSessionByStudents * threshold / 100)
            maxBoundAverage = averageSessionByStudents + (averageSessionByStudents * threshold / 100)
            for studentData in studentsData:
                studentSessionContainer = []
                # For every dates from the start of the academy to now check how many evaluations per day done by single student
                for date in dates:
                    evaluationPerDay = 0
                    LOs = json.loads(studentData['fields']['data'])
                    # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                    for LO in LOs:
                        if date in LO['eval_date']:
                            evaluationPerDay += 1
                            # If found at leaste one evaluation for that day I'm ok with it and skip to next day
                            break
                    studentSessionContainer.append(evaluationPerDay)
                    if date == dateToStop:
                        break
                
                if sum(studentSessionContainer) in range(round(minBoundsAverage),round(maxBoundAverage)):
                    print(f'il valore è passato con {sum(studentSessionContainer)}  min bound {round(minBoundsAverage)} e max bound di {round(maxBoundAverage)}')
                    subSampleStudentArray.append(studentData)

            return subSampleStudentArray,averageSessionByStudents
        else:
            maxBoundAverage = averageSessionByStudents + (averageSessionByStudents * threshold / 100)
            for studentData in studentsData:
                studentSessionContainer = []
                # For every dates from the start of the academy to now check how many evaluations per day done by single student
                for date in dates:
                    evaluationPerDay = 0
                    LOs = json.loads(studentData['fields']['data'])
                    # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                    for LO in LOs:
                        if date in LO['eval_date']:
                            evaluationPerDay += 1
                            # If found at least one evaluation for that day I'm ok with it and skip to next day
                            break
                    studentSessionContainer.append(evaluationPerDay)
                    if date == dateToStop:
                        break
 
                if sum(studentSessionContainer) > maxBoundAverage:
                    print(f'il valore è passato con {sum(studentSessionContainer)} su max bound di {round(maxBoundAverage)}')
                    subSampleStudentArray.append(studentData)

            return subSampleStudentArray,averageSessionByStudents

# This function return the Excluded Users defined as:
#   non-users (performed less than 5% assessment compared to the average of real users)
#   outdated users (performed last assessment more then 90 days before)
#   dateToStop is used to subsampling date by date
def createSubSamplingExcludedAndUsers(studentsData, threshold, days, dateToStop = -1):
    totalExcludedUsers = []
    nonUsersExludedUsers = []
    avoidDuplicatesNonUsersExludedUsers = []
    outdatedExcluedUsers = []

    notExcludedUsers = []
    def addEmptyDate(beginning):

        dates = []
        current = beginning
        now = datetime.now()
        timestamp = datetime.timestamp(now)

        while current < (timestamp):
            dates.append(current) 
            current += 24*60*60
            dt_object = datetime.fromtimestamp(current)
            if dt_object.hour == 1:
                current -= 1*60*60
            elif dt_object.hour == 23:
                current += 1*60*60

        return dates
    if dateToStop == -1:
        data = {}

        tempContainer = {}
        totalEvaluationsAllStudents = 0
        # Scrollig for every students data
        for studentData in studentsData:
            # This is the array of LOs evaluated by the student.
            data = json.loads(studentData['fields']['data'])

            for LO in data:
                #we take the day of every evaluation to find the day of the first and last evaluation
                for evaluation in LO['eval_date']:
                    if evaluation not in tempContainer.keys():
                        tempContainer[evaluation] = 0
                    tempContainer[evaluation] += 1
                    totalEvaluationsAllStudents += 1
        

        for key in sorted(tempContainer.keys()):
            dt_object = datetime.fromtimestamp(key)
            # We check if tere are some problem in the time structure ( some students may have different time zone )
            if dt_object.hour != 0:
                newKey = key - (dt_object.hour) * 60 * 60
                tempContainer[newKey] = tempContainer[key]
                del tempContainer[key]

        beginning = min(tempContainer.keys()) # Timestamp of the first evaluation
        end = max(tempContainer.keys()) # Timestamp of the last evaluation

        dates = addEmptyDate(beginning)
        
        averageNumberOfEvaluation = totalEvaluationsAllStudents/len(studentsData)

        for studentData in studentsData:
            lastEvaluationDate = 0
            totalEvaluationForStudent = 0
            # For every dates from the start of the academy to now checke how many evsluation per day done by single student
            for date in dates:
                evaluationPerDay = 0
                LOs = json.loads(studentData['fields']['data'])
                # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                for LO in LOs:
                    if date in LO['eval_date']:
                        evaluationPerDay += 1
                        totalEvaluationForStudent += 1
                        lastEvaluationDate = date
            if lastEvaluationDate < datetime.timestamp(datetime.today() - timedelta(days)):
                outdatedExcluedUsers.append(studentData)
                print(studentData['fields']['ID'])
                print(f'excluded for time constraint') 
                if totalEvaluationForStudent <  (averageNumberOfEvaluation * threshold / 100):
                    avoidDuplicatesNonUsersExludedUsers.append(studentData)
                    print(studentData['fields']['ID'])
                    print(f'excluded for assessment contraint done {totalEvaluationForStudent} on 5% of the average {(averageNumberOfEvaluation * threshold / 100)}')
            elif totalEvaluationForStudent <  (averageNumberOfEvaluation * threshold / 100):
                nonUsersExludedUsers.append(studentData)
                print(studentData['fields']['ID'])
                print(f'excluded for assessment contraint done {totalEvaluationForStudent} on 5% of the average {(averageNumberOfEvaluation * threshold / 100)}')
            else:
                notExcludedUsers.append(studentData)
        excludedUsers = outdatedExcluedUsers + nonUsersExludedUsers

        return excludedUsers, notExcludedUsers, outdatedExcluedUsers, (nonUsersExludedUsers + avoidDuplicatesNonUsersExludedUsers),averageNumberOfEvaluation
    else:

        data = {}

        tempContainer = {}
        totalEvaluationsAllStudents = 0
        # Scrollig for every students data
        for studentData in studentsData:
            # This is the array of LOs evaluated by the student.
            data = json.loads(studentData['fields']['data'])

            for LO in data:
                #we take the day of every evaluation to find the day of the first and last evaluation
                for evaluation in LO['eval_date']:
                    if evaluation not in tempContainer.keys():
                        tempContainer[evaluation] = 0
                    if evaluation <= dateToStop : 
                        tempContainer[evaluation] += 1
                        totalEvaluationsAllStudents += 1
        

        for key in sorted(tempContainer.keys()):
            dt_object = datetime.fromtimestamp(key)
            # We check if tere are some problem in the time structure ( some students may have different time zone )
            if dt_object.hour != 0:
                newKey = key - (dt_object.hour) * 60 * 60
                tempContainer[newKey] = tempContainer[key]
                del tempContainer[key]
        if bool(tempContainer.keys()):
            beginning = min(tempContainer.keys()) # Timestamp of the first evaluation
            end = max(tempContainer.keys()) # Timestamp of the last evaluation
        else:
             beginning = dateToStop

        dates = addEmptyDate(beginning)
        
        averageNumberOfEvaluation = totalEvaluationsAllStudents/len(studentsData)

        for studentData in studentsData:
            lastEvaluationDate = 0
            totalEvaluationForStudent = 0
            # For every dates from the start of the academy to now checke how many evsluation per day done by single student
            for date in dates:
                evaluationPerDay = 0
                LOs = json.loads(studentData['fields']['data'])
                # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                for LO in LOs:
                    if date > dateToStop:
                        continue
                    if date in LO['eval_date']:
                        evaluationPerDay += 1
                        totalEvaluationForStudent += 1
                        lastEvaluationDate = date
            if lastEvaluationDate < datetime.timestamp(datetime.today() - timedelta(days)):
                outdatedExcluedUsers.append(studentData)
                print(studentData['fields']['ID'])
                print(f'excluded for time constraint') 
                if totalEvaluationForStudent <  (averageNumberOfEvaluation * threshold / 100):
                    avoidDuplicatesNonUsersExludedUsers.append(studentData)
                    print(studentData['fields']['ID'])
                    print(f'excluded for assessment contraint done {totalEvaluationForStudent} on 5% of the average {(averageNumberOfEvaluation * threshold / 100)}')
            elif totalEvaluationForStudent <  (averageNumberOfEvaluation * threshold / 100):
                nonUsersExludedUsers.append(studentData)
                print(studentData['fields']['ID'])
                print(f'excluded for assessment contraint done {totalEvaluationForStudent} on 5% of the average {(averageNumberOfEvaluation * threshold / 100)}')
            else:
                notExcludedUsers.append(studentData)
        excludedUsers = outdatedExcluedUsers + nonUsersExludedUsers
        print('out of for of excuded')
        return excludedUsers, notExcludedUsers, outdatedExcluedUsers, (nonUsersExludedUsers + avoidDuplicatesNonUsersExludedUsers),averageNumberOfEvaluation
            


# Create all subsamples
# dateToStop is used to subsampling date by date

def createAllSubsamples(students: [], dateToStop = -1):
    print("\nGenerating Excluded - Users - Subsamples Excluded\n")
    excludedUsers , users, outdatedExcludedUsers, nonUsersExcludedUsers,averageNumberOfEvaluation = createSubSamplingExcludedAndUsers(students.copy(),5,90,dateToStop)
    print("Generating Check Point Tickers\n")
    checkPointTickersLearners,averageSessionByStudents = subSamplingUsers(users.copy(),25,True,dateToStop)
    print("Generating Autonomous Users\n")
    autonomousUsersLearners, _ = subSamplingUsers(users.copy(),25,False,dateToStop)
    print("Generating Enthusiast Users\n")
    enthusiastUsersLearners, _ = subSamplingUsers(users.copy(),50,False,dateToStop)
    return  users, checkPointTickersLearners, autonomousUsersLearners, enthusiastUsersLearners, excludedUsers, outdatedExcludedUsers, nonUsersExcludedUsers,averageNumberOfEvaluation,averageSessionByStudents
