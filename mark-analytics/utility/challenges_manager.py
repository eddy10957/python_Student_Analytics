from datetime import date

def readChallengesCSV() -> list:
    '''
    Example of generated dict:
        [
            {
                "name" : "Spritz",
                "code" : "NC1",
                "start" : "4/10/21",
                "end" : "22/10/21",
                "num_weeks" : 3
            }
        ]
    '''

    challenge_data = []
    challenges_file = open("input/Challenges.csv", 'r')
    lines = challenges_file.readlines()

    for i in range(len(lines)):
        if (i == 0): continue # skip heading line
        
        values = lines[i].split(";")

        ch = {}
        ch["code"] = values[0]
        ch["name"] = values[1]
        ch["start"] = values[2]
        ch["end"] = values[3]

        # calculating num of weeks between start and end date
        start_date_components = list(map(int, values[2].split("/")))
        end_date_components = list(map(int, values[3].split("/")))

        start_date = date(start_date_components[2], start_date_components[1], start_date_components[0])
        end_date = date(end_date_components[2], end_date_components[1], end_date_components[0])
        ch["num_weeks"] = abs((start_date-end_date).days // 7)

        challenge_data.append(ch)

    challenges_file.close()
    return challenge_data
