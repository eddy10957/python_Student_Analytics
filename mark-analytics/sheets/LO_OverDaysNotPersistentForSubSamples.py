import sys, json, csv
from datetime import datetime
import utility.timestamp_utility as stamp
import sheets.LO_OverDaysPersistent as s3

class LO_OverDaysNotPersistentForSubSamples:

    outputFilename: str = None
    students_data: list = None

    def __init__(self, filename, students_data):
        rawDataArray = []
        dataArray = []
        self.outputFilename = filename

        for student in students_data:
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
        self.students_data = dataArray
        self.run()

    def run(self):
        # Generate the actual data to write on file
        data = self.generateData()
        # Write data on file check if there are errors.
        if self.generateTSVFile(data):
            sys.stdout.write("\nAll done, data stored in " + self.outputFilename + "\n")
        else:
            sys.stdout.write("\nError\n")

    def generateData(self) -> str:
        data = {}
        # Read Input file LO csv
        allLOs = s3.readLearningObjectiveCSV(self)
        
        # Iteration on the one by one LO assesments done by students.
        for learningObjectives in self.students_data:
            
            # getting data from each learning objectives
            ID = learningObjectives["ID"]
            strand = learningObjectives["strand"]
            short_goal = learningObjectives["goal_Short"]
            # This information is retrived from the csv file read before
            goal = next(LO for LO in allLOs if LO['ID'] == ID)['goal']
            # This information is retrived from the csv file read before
            objectives = next(LO for LO in allLOs if LO['ID'] == ID)['objectives']
            core = "CORE" if learningObjectives["isCore"] else "ELECTIVE"
            evalScore = learningObjectives["eval_score"]
            evalDate = learningObjectives["eval_date"]

            # creating entry in data if not already found.
            if ID not in data: 
                data[ID] = {}
                data[ID]["strand"] = strand
                data[ID]["goal"] = goal
                data[ID]["short_goal"] = short_goal
                data[ID]["objectives"] = objectives
                data[ID]["core"] = core
                data[ID]["level1"] = {}
                data[ID]["level2"] = {}
                data[ID]["level3"] = {}
                data[ID]["level4"] = {}
                data[ID]["level5"] = {}
            
            # filling data
            lastScore = 0
            lastDate = 0

            # Iteration based on how many scores found in the assesment evaluation score array. 
            # Example: A student could have evaluated him self two times on a particular LO,
            #          So we find two evaluation with different scores and different evaluation dates.
            #          evalScore = [1,2]
            for i in range(len(evalScore)):

                # getting score and date
                evalScoreValue = evalScore[i]
                evalDateValue = evalDate[i]

                # 0 score are not counted
                if evalScoreValue == 0: continue

                # transforming evaluation score from number to string
                evalScoreFullString = "level" + str(evalScoreValue)
                # Keeping track of the last score done on the LO, starting from 0 previously setted
                lastScoreFullString = "level" + str(lastScore)
                # Adjusting dates
                evalDateTimestamp = stamp.adjust(evalDateValue)
                # Keeping track of the last dates of evaluation of the LO
                lastDateTimestamp = stamp.adjust(lastDate)
                
                # subtracting if the score increased.
                #TODO: Why?
                if lastScore != 0:
                    data[ID][lastScoreFullString][lastDateTimestamp] -= 1
                
                # If the date of the evaluation is not already inside the dictionary of the level of that LO 
                if evalDateTimestamp not in data[ID][evalScoreFullString]: 
                    # Sets to zero the value in the dictionary of the level of the LO in that date.
                    # Just because we can now increment the value when we found one.
                    # Example: For BU-REV-002 there are 5 dictionaries: level1:{}, level2{} and so on
                    # this will set inside the correct dictionary the value zero to the date found
                    # level1 : {1667779261: 0}  first number is the date the second the value 0 we set
                    data[ID][evalScoreFullString][evalDateTimestamp] = 0

                # Increment the value of the LO assested of a specific level in a specific day.
                # Example: Continuing the example above this will become level1 : {1667779261: 1}
                data[ID][evalScoreFullString][evalDateTimestamp] += 1

                # Keeping track of the last evaluation score and the last date of evaluation throught the iteration
                lastScore = evalScoreValue
                lastDate = evalDateValue

                # Filling the other levels value with zeros  
                for j in range(1,6):
                    if j != evalScoreValue:
                        a = "level" + str(j)
                        if evalDateTimestamp not in data[ID][a]:
                            data[ID][a][evalDateTimestamp] = 0
         
        # Fill the the LOs not evaluated by anyone 
        for LO in allLOs:
            if LO['ID'] not in data.keys():
                data[LO['ID']] = {}
                data[LO['ID']]["strand"] = LO['strand']
                data[LO['ID']]["goal"] = LO['goal']
                data[LO['ID']]["short_goal"] = LO['short']
                data[LO['ID']]["objectives"] = LO['objectives']
                data[LO['ID']]["core"] = "CORE" if LO['core'] else "ELECTIVE"

                data[LO['ID']]["level1"] = {}
                data[LO['ID']]["level2"] = {}
                data[LO['ID']]["level3"] = {}
                data[LO['ID']]["level4"] = {}
                data[LO['ID']]["level5"] = {}

            """ data[LO['ID']]["backend"] = LO['backend']
            data[LO['ID']]["business"] = LO['business']
            data[LO['ID']]["design"] = LO['design']
            data[LO['ID']]["frontend"] = LO['frontend']
            data[LO['ID']]["gameDesign"] = LO['gameDesign']
            data[LO['ID']]["gameDeveloper"] = LO['gameDeveloper']
            data[LO['ID']]["projectManagement"] = LO['projectManagement'] """

            data[LO['ID']]["appDeveloper"] = LO['appDeveloper']
            data[LO['ID']]["appDesigner"] = LO['appDesigner']
            data[LO['ID']]["gameCreator"] = LO['gameCreator']
            

        data_string = json.dumps(self.addEmptyDate(data))
        # with open("output/test.json", 'w') as f:
        #     f.write(data_string)
        #     f.close()

        return data_string

    def addEmptyDate(self, data) -> str:

        # function to fill the timestamp with empty data if there aren't any evaluations.
        def fillEmptyData(data, timestamp):
            for ID in data:
                for i in range(1, 6):
                    value = stamp.adjust(timestamp)
                    if value not in data[ID]["level" + str(i)]:
                        data[ID]["level" + str(i)][value] = 0
            return data

        # calculate dates extremes
        minTimestamp = float("inf")
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        maxTimestamp = float(timestamp)
        # Find the earliest date (the smaller) from the assessments done by students
        for ID in data:
            for date in data[ID]["level1"].keys():
                if float(date) < minTimestamp:
                    minTimestamp = float(date)

        # saving 0 for each void timestamp. 
        timestamp = minTimestamp
        while timestamp < maxTimestamp:
            data = fillEmptyData(data, timestamp)
            
            # adding one day to the timestamp
            timestamp += 24*60*60

        data = fillEmptyData(data, maxTimestamp)

        return data

    def generateTSVFile(self, jsonData: str) -> bool:
        try:

            # returns JSON object as a dictionary
            data = json.loads(jsonData)

            # defining support arrays
            allRows = []
            experienceLevels = ["No Exposure","Beginning","Progressing","Proficient","Exemplary"]

            # the first row is a litte bit particular
            #New first Row after changes of the csv
            firstRow = ["ID","Strand","goal","Short Goal","objectives","Core","Code + Level","Level","App Developer","App Designer","Game Creator"]
            # Days from the start of evaluations to today. (TUTT 'O BLOCK, si poteva scrivere può semplice mi sa ma che ci vogliamo fa... Not my fault)
            level_Datas = [*data[list(data.keys())[0]]["level1"]]
            level_Datas.sort()

            # Creating column for every day!
            for level_Data in level_Datas:
                date_time = datetime.fromtimestamp(int(level_Data)).strftime('%Y-%b-%d').upper()
                firstRow.append(date_time)

            # appending the first row
            allRows.append(firstRow)

            # Creating a row for each learning objective that we have in the json
            #["ID","Strand","goal","Short Goal","objectives","Core","Level"]
            for key in data.keys():
                # fo this operation 5 time, each for an evaluation level
                for i in range(1,6):
                    # prepare the array
                    row = []
                    # insert the ID
                    row.append(key)
                    # input the strand
                    row.append(data[key]["strand"])
                    # input the goal
                    row.append(data[key]["goal"])
                    # insert the goal
                    row.append(data[key]["short_goal"])
                    # input the goal
                    row.append(data[key]["objectives"])
                    #insert the core
                    row.append(data[key]["core"])
                    # insert the code + level of expertice
                    row.append(key + " - " + experienceLevels[i-1])
                    # insert the level of expertice
                    row.append(experienceLevels[i-1])
                    
                    #rubrics = ["backend","business","design","frontend","gameDesign","gameDeveloper","projectManagement"]
                    #New rubrics after 2022/2023 changes
                    rubrics = ["appDeveloper","appDesigner","gameCreator"]                

                    # Appending the expected level of experience of that LO based on the rubrics expectation
                    for rubric in rubrics:
                        present = 0
                        if data[key][rubric] in experienceLevels:
                            present = experienceLevels.index(data[key][rubric])
                            row.append("1" if present == (i-1) else "0")
                        else:
                            row.append("0")

                    # check how many student evaluated that day and that level.
                    level_Datas = [*data[key]["level"+str(i)]]
                    level_Datas.sort()
                    for lvl in level_Datas:
                        row.append(data[key]["level"+str(i)][lvl])
                    
                    # add row to the array
                    allRows.append(row)

            # write on the file
            with open(self.outputFilename, 'w') as out_file:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                for singleRow in allRows:
                    tsv_writer.writerow(singleRow)
            
                out_file.close()
            print("@@@@@@@")
            return True

        except Exception as e: 
            sys.stdout.write("\n" + str(e) + "\n")
            return False
