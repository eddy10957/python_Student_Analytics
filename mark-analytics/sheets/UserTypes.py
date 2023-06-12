from ast import If
import sys, json, csv
from datetime import datetime
import utility.timestamp_utility as stamp
import utility.airtable_manager as manager

class UserTypes:

    outputFilename: str = None
    students_data: list = None

    def __init__(self, filename, students_data):
        self.outputFilename = filename
        self.students_data = students_data
        self.run()

    def run(self):
        # Generate dates taking the start from the first ever evaluation done by students.
        dates = self.generateDates()
        # Write the actual file and check if there are errors.
        if self.generateTSVFile(dates):
            sys.stdout.write("\nAll done, data stored in " + self.outputFilename + "\n")
        else:
            sys.stdout.write("\nError\n")

    # Generate dates taking the start from the first ever evaluation done by students.
    def generateDates(self):

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
        for studentData in self.students_data:

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

        return dates # We return the array of days between the first and last evaluation

    def generateTSVFile(self,dates) -> bool:
        try:
            firstRow  = ["User Types"]
            for date in dates :
                dt_object = datetime.fromtimestamp(date)
                firstRow.append(f"{dt_object.strftime('%Y-%b-%d').upper()}")

            allRows = [] # This is an array of rows that will be created
            allRows.append(firstRow)
            
            userRow = ["Users"]
            checkpointTickerRow = ["Users - CheckpointTicker"]
            autonomousRow = ["Users - Autonomous"]
            enthusiastRow = ["Users - Enthusiast"]
            excludedUsersRow = ["ExcludedUsers"]
            outdatedRow = ["ExcludedUsers - Outdated"]
            nonUsersRow = ["ExcludedUsers - Non-User"]

            
             
                # For every dates from the start of the academy to now check how many evaluation per day done by single student
            for date in dates:
                users, checkPointTickersLearners, autonomousUsersLearners, enthusiastUsersLearners, excludedUsers, outdatedExcludedUsers, nonUsersExcludedUsers , _ , _ = manager.createAllSubsamples(self.students_data,date)
                userRow.append(len(users))
                checkpointTickerRow.append(len(checkPointTickersLearners))
                autonomousRow.append(len(autonomousUsersLearners))
                enthusiastRow.append(len(enthusiastUsersLearners))
                excludedUsersRow.append(len(excludedUsers))
                outdatedRow.append(len(outdatedExcludedUsers))
                nonUsersRow.append(len(nonUsersExcludedUsers))

                   
            allRows.append(userRow)
            allRows.append(checkpointTickerRow)
            allRows.append(autonomousRow)
            allRows.append(enthusiastRow)
            allRows.append(excludedUsersRow)
            allRows.append(outdatedRow)
            allRows.append(nonUsersRow)

            # write on the file
            with open(self.outputFilename, 'w') as out_file:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                for singleRow in allRows:
                    tsv_writer.writerow(singleRow)
                
                out_file.close()
            
            return True

        except Exception as e:
            sys.stdout.write("\n" + str(e) + "\n")
            return False
