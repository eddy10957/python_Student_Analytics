from ast import If
import sys, json, csv
from datetime import datetime
import utility.timestamp_utility as stamp

class StudentEvaluations_OverDaysNotPersistent:

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
            allRows = [] # This is an array of rows that will be created

            # Creation of the first row that will contain the content of the columns, in particular you can find the days here
            firstRow = ["ID"]
            for date in dates :
                dt_object = datetime.fromtimestamp(date)
                firstRow.append(f"{dt_object.strftime('%Y-%b-%d').upper()}")
                
            allRows.append(firstRow)
            
            for studentData in self.students_data:
                row = []
                # ID Studente
                row.append(studentData['fields']['ID'])

                # For every dates from the start of the academy to now checke how many evsluation per day done by single student
                for date in dates:
                    evaluationPerDay = 0
                    LOs = json.loads(studentData['fields']['data'])
                    # For every LO found in the evaluations done by the student check date and add +1 if evaluation was done in the day searched
                    for LO in LOs:
                        if date in LO['eval_date']:
                            evaluationPerDay += 1
                    
                    #Append the complete row for one student,  with evaluation number per day. 
                    row.append(evaluationPerDay)

                allRows.append(row)

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
