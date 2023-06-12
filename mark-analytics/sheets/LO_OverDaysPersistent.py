from ast import If
import sys, json, csv
from datetime import datetime
import utility.timestamp_utility as stamp

class LO_OverDaysPersistent:

    outputFilename: str = None
    students_data: list = None

    def __init__(self, filename, students_data):
        self.outputFilename = filename
        self.students_data = students_data
        self.run()

    def run(self):
        # Generate the dates from the first and last evaluation.
        dates = self.generateDates()
        # Write data on file check if there are errors.
        if self.generateTSVFile(dates):
            sys.stdout.write("\nAll done, data stored in " + self.outputFilename + "\n")
        else:
            sys.stdout.write("\nError\n")

    def generateDates(self):

        data = {}

        tempContainer = {}

        # Iterate on every unique student.
        for studentData in self.students_data:

            # This is the array of all assessments done by single student
            data = json.loads(studentData['fields']['data'])


            for LO in data:
                #we take the day of every evaluation in order to find the day of the first and last evaluation
                for evaluation in LO['eval_date']:
                    if evaluation not in tempContainer.keys():
                        tempContainer[evaluation] = 0
                    tempContainer[evaluation] += 1

        for key in sorted(tempContainer.keys()):
            dt_object = datetime.fromtimestamp(key)
            # We check if there are some problem in the time structure ( some students may have different time zone )
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
            firstRow = ["ID","Strand","goal","Short Goal","objectives","Core","Code + Level","Level","App Developer","App Designer","Game Creator"]
            rubrics = ["appDeveloper","appDesigner","gameCreator"]
            experienceLevels = ["No Exposure","Beginning","Progressing","Proficient","Exemplary"]
            
            for date in dates :
                dt_object = datetime.fromtimestamp(date)
                firstRow.append(f"{dt_object.strftime('%Y-%b-%d').upper()}")
                
            allRows.append(firstRow)

            LOs = readLearningObjectiveCSV(self) # The learning objectives that we have to analize 
            
            for idx, LO in enumerate(LOs): # We rotate for every learning objective that we have 
                evaluations = {} # a dictionary of day-dayEvaluation for have a history of the learning objective status per day
                evaluation = {1:0,2:0,3:0,4:0,5:0} # is intended as evaluation for that day, it will not be reformatted every time a day change but every time we change the learning objective in otder to have the persistency
                lastSelected = {}
                for date in dates: # For each day between the first and last evaluation
                    for studentData in self.students_data: # for each student that have created an evaluation
                        # lastSelected = -1 # we define with -1 that we was not selecting a learning objective before this one and we update it every time we change the student for keep remembering what was his last change
                        evaluatedLOs = json.loads(studentData['fields']['data']) # This is the array of LO that the student have evaluated
                        for evaluatedLO in evaluatedLOs: # we check every learning objective that has been evaluated by that student
                            if evaluatedLO['ID'] == LO['ID']: # If we find the learning objective that we're searching now inside the evaluated ones
                                if date in evaluatedLO['eval_date']: # we check if it was evaluated in the day we're looking at 
                                    for i in range(len(evaluatedLO['eval_date'])): # we check every evaluation day by index since we have a direct correlation of index between evaluatedLO['eval_date'] and evaluatedLO['eval_score']
                                        if date == evaluatedLO['eval_date'][i]: # if we're looking at the right date we
                                            evaluation[evaluatedLO['eval_score'][i]] += 1 # update the value of evaluation
                                            if studentData['fields']['ID'] in lastSelected.keys(): # if we don't have something else evaluated before we just continue
                                                evaluation[lastSelected[studentData['fields']['ID']]] -= 1 # else we notify that it was changed
                                            lastSelected[studentData['fields']['ID']] = evaluatedLO['eval_score'][i] # assign the new lastSelected value
                                            
                    evaluations[date] = evaluation.copy()

                #TODO: create the row for each expertise of this LO
                noExposure = [LO['ID'],LO['strand'],LO['goal'],LO['short'],LO['objectives'], "CORE" if LO['core'] else "ELECTIVE",LO['ID'] + " - " + "No Exposure", "No Exposure"]
                beginning = [LO['ID'],LO['strand'],LO['goal'],LO['short'],LO['objectives'], "CORE" if LO['core'] else "ELECTIVE",LO['ID'] + " - " + "Beginning", "Beginning"]
                progressing = [LO['ID'],LO['strand'],LO['goal'],LO['short'],LO['objectives'], "CORE" if LO['core'] else "ELECTIVE",LO['ID'] + " - " + "Progressing", "Progressing"]
                proficient = [LO['ID'],LO['strand'],LO['goal'],LO['short'],LO['objectives'], "CORE" if LO['core'] else "ELECTIVE",LO['ID'] + " - " + "Proficient", "Proficient"]
                exemplary = [LO['ID'],LO['strand'],LO['goal'],LO['short'],LO['objectives'], "CORE" if LO['core'] else "ELECTIVE",LO['ID'] + " - " + "Exemplary", "Exemplary"]

                # Add to the correct row
                # PS: apparently python don't have switch case, f**k you python cuz you'll have a lot of if-ifel-else now
                #["No Exposure","Beginning","Progressing","Proficient","Exemplary"] 
                for rubric in rubrics: 
                    if LO[rubric] in experienceLevels: 

                        noExposure.append("1" if LO[rubric] == "No Exposure" else "0")
                        beginning.append("1" if LO[rubric] == "Beginning" else "0")
                        progressing.append("1" if LO[rubric] == "Progressing" else "0")
                        proficient.append("1" if LO[rubric] == "Proficient" else "0")
                        exemplary.append("1" if LO[rubric] == "Exemplary" else "0")

                    else:
                        noExposure.append("0")
                        beginning.append("0")
                        progressing.append("0")
                        proficient.append("0")
                        exemplary.append("0")

                sys.stdout.write(f"{idx}/{len(LOs)}\n")
                for date in dates:
                    noExposure.append(evaluations[date][1])
                    beginning.append(evaluations[date][2])
                    progressing.append(evaluations[date][3])
                    proficient.append(evaluations[date][4])
                    exemplary.append(evaluations[date][5])

                #TODO: add the completed rows for to the rows array
                
                allRows.append(noExposure)
                allRows.append(beginning)
                allRows.append(progressing)
                allRows.append(proficient)
                allRows.append(exemplary)

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


# Read the LO csv file inside input folder. Uses ";" as separator.
def readLearningObjectiveCSV(self) -> list:
    LOdata = []
    LOfile = open("input/LearningObjectives.csv", 'r')
    lines = LOfile.readlines()

    for i in range(len(lines)):
        if (i == 0): continue # skip heading line
        
        values = lines[i].split(";")

        LO = {}
        LO["ID"] = values[0]
        LO["strand"] = values[1]
        LO["goal"] = values[2]
        LO["short"] = values[3]
        LO["objectives"] = values[4]
        LO["core"] = values[7] == "Core"


        LO["appDeveloper"] = values[9]
        LO["appDesigner"] = values[10]
        LO["gameCreator"] = values[11]
        

        LOdata.append(LO)

    LOfile.close()
    return LOdata