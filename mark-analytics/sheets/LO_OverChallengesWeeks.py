import sys, json, csv
from datetime import datetime, date, timedelta
import utility.timestamp_utility as stamp
import utility.challenges_manager as challenge


class FirstSheet:

    outputFilename: str = None
    challenges: list = None
    students_data: list = None

    def __init__(self, filename, students_data):
        self.outputFilename = filename
        self.challenges = challenge.readChallengesCSV()
        self.students_data = students_data

    def run(self):
        data = self.generateData()
        if self.generateTSVFile(data):
            sys.stdout.write("\nAll done, data stored in " + self.outputFilename + "\n")
        else:
            sys.stdout.write("\nError\n")

    def dateInWeek(self, a_date, challenge) -> int:
        
        ch_start = None
        ch_end = None

        for ch in self.challenges:
            if ch["code"] == challenge:
                ch_start = list(map(int, ch["start"].split("/")))
                ch_end = list(map(int, ch["end"].split("/")))
                break
        
        ch_start_date = date(ch_start[2], ch_start[1], ch_start[0])
        ch_end_date = date(ch_end[2], ch_end[1], ch_end[0])

        i = ch_start_date
        w = 1
        while i <= ch_end_date:
            
            i = i + timedelta(days=7)
            
            if a_date <= i:
                return w
            
            w = w + 1

        return 0

    def generateData(self) -> str:
        data = {}
        for learningObjectives in self.students_data:
            # getting data from each learning objectives
            ID = learningObjectives["ID"]
            strand = learningObjectives["strand"]
            short_goal = learningObjectives["goal_Short"]
            core = learningObjectives["isCore"]
            evalScore = learningObjectives["eval_score"]
            evalDate = learningObjectives["eval_date"]

            # creating empty data if nil
            if ID not in data:
                data[ID] = {}
                data[ID]["strand"] = strand
                data[ID]["short_goal"] = short_goal
                data[ID]["core"] = core
                data[ID]["challenges"] = {}
            
                for ch in self.challenges:
                    ch_code = ch["code"]
                    data[ID]["challenges"][ch_code] = {}

                    for week_num in range(1, ch["num_weeks"]):
                        week_string = "week" + str(week_num)
                        week_data = {"avg": 0, "avg_num": 0, "sum": 0, "sum_num": 0}
                        data[ID]["challenges"][ch_code][week_string] = week_data

            # filling data
            for i in range(len(evalScore)):
                
                # getting score
                evalScoreValue = evalScore[i]

                # 0 score are not counted
                if evalScoreValue == 0: continue

                # getting date
                evalDateValue = evalDate[i]
                evalDateTimestamp = stamp.adjust(evalDateValue)
                evalDateDateTime = datetime.fromtimestamp(evalDateTimestamp)
                
                corresponding_challenge = None
                corresponding_week = None

                for ch in self.challenges:
                    week = self.dateInWeek(evalDateDateTime.date(), ch["code"])
                    if week != 0:
                        corresponding_challenge = ch["code"]
                        corresponding_week = week
                
                
                old_data = data[ID]["challenges"][corresponding_challenge]["week" + str(corresponding_week)]
                new_data = {"avg": 0, "avg_num": 0, "sum": 0, "sum_num": 0}

                new_data["avg"] = (old_data["avg"] + evalScoreValue) / 2
                new_data["avg_num"] = old_data["avg_num"] + 1
                
                if corresponding_week == 1:
                    new_data["sum"] = new_data["avg"]
                    new_data["sum_num"] = new_data["avg_num"]
                else:
                    for old_week in range(1, corresponding_week):
                        old_week_avg = data[ID]["challenges"][corresponding_challenge]["week" + str(old_week)]["avg"]
                        old_week_avg_num = data[ID]["challenges"][corresponding_challenge]["week" + str(old_week)]["avg_num"]
                        new_data["sum"] = (new_data["avg"] + old_week_avg) / 2
                        new_data["sum_num"] = old_week_avg_num + new_data["sum_num"]
                
                data[ID]["challenges"][corresponding_challenge]["week" + str(corresponding_week)] = new_data
                
        data_string = json.dumps(data)
        # with open("output/test.json", 'w') as f:
        #     f.write(data_string)
        #     f.close()

        return data_string

    def generateTSVFile(self, jsonData: str) -> bool:
        try:
            
            # returns JSON object as
            # a dictionary
            data = json.loads(jsonData)
            
            # defining support arrays
            allRows = []

            # the first row is a litte bit particular
            firstRow = ["","","","",""]
            for challenge in data[list(data.keys())[0]]["challenges"].keys():
                for weeks in data[list(data.keys())[0]]["challenges"][challenge].keys():
                    if weeks == "week1":
                        toAppend = [challenge,"","",""]
                        firstRow += toAppend
                    else:
                        toAppend = ["","","",""]
                        firstRow += toAppend
            # appending the first row
            allRows.append(firstRow)

            # the second row is a litte bit particular
            firstRow = ["","","","",""]
            for challenge in data[list(data.keys())[0]]["challenges"].keys():
                for weeks in data[list(data.keys())[0]]["challenges"][challenge].keys():
                    toAppend = [weeks,"","",""]
                    firstRow += toAppend
            
            # appending the third row
            allRows.append(firstRow)

            # the third row is a litte bit particular
            firstRow = ["","Strand","Code","Type","Learn Goal"]
            for challenge in data[list(data.keys())[0]]["challenges"].keys():

                for weeks in data[list(data.keys())[0]]["challenges"][challenge].keys():
                    toAppend = ["AVG","#","SUM","#"]
                    firstRow += toAppend
            # appending the third row
            allRows.append(firstRow)

            # the forth row is a litte bit particular
            firstRow = ["Type : ","","","",""]
            for challenge in data[list(data.keys())[0]]["challenges"].keys():
                for weeks in data[list(data.keys())[0]]["challenges"][challenge].keys():
                    toAppend = ["","Somma : ","",""]
                    firstRow += toAppend
            
            # appending the forth row
            allRows.append(firstRow)

            filteredCore = [sub for sub in data.keys() if data[sub]["core"]]

            # the core row is a litte bit particular
            firstRow = ["CORE","","","",""]

            coreLearningObjective = {challenge : {week : {"sum":0} for week in data[filteredCore[0]]["challenges"][challenge].keys()} for challenge in data[filteredCore[0]]["challenges"].keys()}


            for ID in data.keys():
                for challenge in data[ID]["challenges"].keys():
                    for week in data[ID]["challenges"][challenge].keys():
                        coreLearningObjective[challenge][week]["sum"] += data[ID]["challenges"][challenge][week]["avg_num"]

            for challenge in coreLearningObjective.keys():
                for week in coreLearningObjective[challenge].keys():
                    toAppend = ["",coreLearningObjective[challenge][week]["sum"],"",""]
                    firstRow += toAppend
            
            # appending the core row
            allRows.append(firstRow)

            # the forth row is a litte bit particular
            firstRow = ["Strand: ","","","",""]
            for challenge in data[list(data.keys())[0]]["challenges"].keys():
                for weeks in data[list(data.keys())[0]]["challenges"][challenge].keys():
                    toAppend = ["","Somma : ","Media : ","Somma : "]
                    firstRow += toAppend
            
            # appending the forth row
            allRows.append(firstRow)

            strands = [data[sub]['strand'] for sub in data.keys()]

            forChallenges = {strand : {challenge : {week : {"sum":0, "med": 0, "medNum": 0, "allSum": 0, "allSumNum": 0} for week in data[filteredCore[0]]["challenges"][challenge].keys()} for challenge in data[filteredCore[0]]["challenges"].keys()} for strand in strands}

            # the forth row is a litte bit particular
            
            # strands
            for strand in dict.fromkeys(strands).keys():
                # all the Learning Objective
                for id in filteredCore:
                    #if the LO have the same strand of what we're selecting now
                    if data[id]["strand"] == strand:
                        for challenge in data[list(data.keys())[0]]["challenges"].keys():
                            for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                                forChallenges[strand][challenge][week]["sum"] += data[id]["challenges"][challenge][week]["avg_num"]
                                forChallenges[strand][challenge][week]["med"] += data[id]["challenges"][challenge][week]["sum"]
                                forChallenges[strand][challenge][week]["medNum"] += 1
                                forChallenges[strand][challenge][week]["allSum"] += data[id]["challenges"][challenge][week]["sum_num"]
                                forChallenges[strand][challenge][week]["allSumNum"] += 1
            
            for strand in dict.fromkeys(strands).keys():
                firstRow = [strand,"","","",""]
                for challenge in data[list(data.keys())[0]]["challenges"].keys():
                    for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                        numMed = forChallenges[strand][challenge][week]["medNum"]
                        allSumNum = forChallenges[strand][challenge][week]["allSumNum"]
                        if numMed == 0:
                            numMed = 1
                        if allSumNum == 0:
                            allSumNum = 1
                        toAppend = ["",forChallenges[strand][challenge][week]["sum"],int(forChallenges[strand][challenge][week]["med"]/numMed),int(forChallenges[strand][challenge][week]["allSum"]/allSumNum)]
                        firstRow += toAppend
                # appending the row
                allRows.append(firstRow)

                
                for id in filteredCore:
                    
                    #if the LO have the same strand of what we're selecting now
                    if data[id]["strand"] == strand:
                        firstRow = ["",strand,id,"CORE",data[id]["short_goal"]]
                        for challenge in data[list(data.keys())[0]]["challenges"].keys():
                            for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                                toAppend = [data[id]["challenges"][challenge][week]["avg"],data[id]["challenges"][challenge][week]["avg_num"],data[id]["challenges"][challenge][week]["sum"],data[id]["challenges"][challenge][week]["sum_num"]]
                                firstRow += toAppend
                        allRows.append(firstRow)
            
            filteredElective = [sub for sub in data.keys() if not data[sub]["core"]]

            # the core row is a litte bit particular
            firstRow = ["CORE","","","",""]

            coreLearningObjective = {challenge : {week : {"sum":0} for week in data[filteredElective[0]]["challenges"][challenge].keys()} for challenge in data[filteredElective[0]]["challenges"].keys()}
            
            for ID in data.keys():
                for challenge in data[ID]["challenges"].keys():
                    for week in data[ID]["challenges"][challenge].keys():
                        coreLearningObjective[challenge][week]["sum"] += data[ID]["challenges"][challenge][week]["avg_num"]

            for challenge in coreLearningObjective.keys():
                for week in coreLearningObjective[challenge].keys():
                    toAppend = ["",coreLearningObjective[challenge][week]["sum"],"",""]
                    firstRow += toAppend
            
            # appending the core row
            allRows.append(firstRow)
            
            # the forth row is a litte bit particular
            firstRow = ["Strand: ","","","",""]
            for challenge in data[list(data.keys())[0]]["challenges"].keys():
                for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                    toAppend = ["","Somma : ","Media : ","Somma : "]
                    firstRow += toAppend
            
            # appending the forth row
            allRows.append(firstRow)

            forChallenges = {strand : {challenge : {week : {"sum":0, "med": 0, "medNum": 0, "allSum": 0, "allSumNum": 0} for week in data[filteredElective[0]]["challenges"][challenge].keys()} for challenge in data[filteredElective[0]]["challenges"].keys()} for strand in strands}

            # the forth row is a litte bit particular
            
            # strands
            for strand in dict.fromkeys(strands).keys():
                # all the Learning Objective
                for id in filteredElective:
                    #if the LO have the same strand of what we're selecting now
                    if data[id]["strand"] == strand:
                        for challenge in data[list(data.keys())[0]]["challenges"].keys():
                            for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                                forChallenges[strand][challenge][week]["sum"] += data[id]["challenges"][challenge][week]["avg_num"]
                                forChallenges[strand][challenge][week]["med"] += data[id]["challenges"][challenge][week]["sum"]
                                forChallenges[strand][challenge][week]["medNum"] += 1
                                forChallenges[strand][challenge][week]["allSum"] += data[id]["challenges"][challenge][week]["sum_num"]
                                forChallenges[strand][challenge][week]["allSumNum"] += 1
            
            for strand in dict.fromkeys(strands).keys():
                firstRow = [strand,"","","",""]
                for challenge in data[list(data.keys())[0]]["challenges"].keys():
                    for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                        numMed = forChallenges[strand][challenge][week]["medNum"]
                        allSumNum = forChallenges[strand][challenge][week]["allSumNum"]
                        sum = forChallenges[strand][challenge][week]["sum"]
                        if numMed == 0:
                            numMed = 1
                        if allSumNum == 0:
                            allSumNum = 1
                        toAppend = ["",sum,int(forChallenges[strand][challenge][week]["med"]/numMed),int(forChallenges[strand][challenge][week]["allSum"]/allSumNum)]
                        firstRow += toAppend
                # appending the row
                allRows.append(firstRow)

                for id in filteredElective:
                    
                    #if the LO have the same strand of what we're selecting now
                    if data[id]["strand"] == strand:
                        firstRow = ["",strand,id,"ELECTIVE",data[id]["short_goal"]]
                        for challenge in data[list(data.keys())[0]]["challenges"].keys():
                            for week in data[list(data.keys())[0]]["challenges"][challenge].keys():
                                toAppend = [data[id]["challenges"][challenge][week]["avg"],data[id]["challenges"][challenge][week]["avg_num"],data[id]["challenges"][challenge][week]["sum"],data[id]["challenges"][challenge][week]["sum_num"]]
                                firstRow += toAppend
                        allRows.append(firstRow)

            # write on the file
            with open(self.outputFilename, 'wt') as out_file:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                for singleRow in allRows:
                    tsv_writer.writerow(singleRow)
                out_file.close()

            return True

        except Exception as e: 
            sys.stdout.write("\n" + str(e) + "\n")
            return False

  
      
        
