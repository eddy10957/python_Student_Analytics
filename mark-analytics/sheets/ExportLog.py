from ast import If
import sys, json, csv
from datetime import datetime
import pandas as pd
import utility.timestamp_utility as stamp
import utility.airtable_manager as manager



class ExportLog:

    outputFilename: str = None
    userTypesFileName: str = None
    averageNumberOfEvaluation = 0
    averageSessionByStudents = 0

    def __init__(self, filename, userTypesFileName,allUsersCount,averageNumberOfEvaluation,averageSessionByStudents):
        self.outputFilename = filename
        self.userTypesFileName = userTypesFileName
        self.allUsersCount = allUsersCount
        self.averageNumberOfEvaluation = averageNumberOfEvaluation
        self.averageSessionByStudents = averageSessionByStudents
        self.run()

    def run(self):
        
        # Write the actual file and check if there are errors.
        if self.generateTxtFile():
            sys.stdout.write("\nAll done, data stored in " + self.outputFilename + "\n")
        else:
            sys.stdout.write("\nError\n")

    
    def generateTxtFile(self) -> bool:
        try:
            allRows = []

            allRows.append(f'Data Export {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')
            
            # Generating the subsample row 
            data = pd.read_csv(self.userTypesFileName, delimiter='\t')
            last_col_name = data.columns[-1]
            samples_str = f"\nSubSamples to {last_col_name}\n"
            for i, row in data.iloc[0:].iterrows():
                col_1_row_2_str = row[0]
                last_col_val = row[-1]
                samples_str += f"    {col_1_row_2_str} {last_col_val} \n"
            allRows.append(samples_str)

            # Check if subsamples of Users - Enthusiast are more then Users - Autonomous which should not be possible
            # Check also if sum of Users and Excluded users is not equal of all users.
            rows_to_check = data.iloc[[0, 4], 1:]
            checkCounter = 0
            errorColumnsSubSamplesUsers = []
            errorColumnsAllUsers = []
            for col in data.columns[1:]:
                checkCounter += 1
                if data.loc[2,col] < data.loc[3,col]:
                    errorColumnsSubSamplesUsers.append(col)
                if rows_to_check[col].sum() != self.allUsersCount:
                    errorColumnsAllUsers.append(col)


            allRows.append(f'\nAverage number of evaluations done by learner {round(self.averageNumberOfEvaluation)}')
            allRows.append(f'\nAverage number of sessions done by learner {round(self.averageSessionByStudents)}\n')

            allRows.append(f'\nTest passed {checkCounter*2} \n')
            allRows.append(f'User sub samples test not passed {len(errorColumnsSubSamplesUsers)} at days {errorColumnsSubSamplesUsers} \n')
            allRows.append(f'Users + Excluded not equal All Users test not passed {len(errorColumnsAllUsers)} at days {errorColumnsAllUsers} \n ')
            

            # write on the file
            with open(self.outputFilename, 'w') as out_file:
                for singleRow in allRows:
                    out_file.write(singleRow)
                
                out_file.close()
            
            return True

        except Exception as e:
            sys.stdout.write("\n" + str(e) + "\n")
            return False
