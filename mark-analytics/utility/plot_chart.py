# import matplotlib.pyplot as plt
# import math

# VIEW_TYPE = 'MONTH' #'DAY' 'MONTH' 'YEAR'
# PLOT_COLORS =  { 'Technical' : 'blue', 
#             'Design' : 'green', 
#             'Process' : 'red', 
#             'App Business and Marketing' : 'purple', 
#             'Professional Skills' : 'yellow' }

# def plot(data: string):

#     data = json.loads(data)
#     for strand in data:
        
#         x = []
#         y = []
        
#         # getting data
#         for lo in data[strand]:
#             for date in data[strand][lo]['eval_date']:
#                 x += date
#             for score in data[strand][lo]['eval_score']:
#                 y += score

#         # calculating average for same time
#         dictionary = {}
#         for i in range(len(x)):
#             time = timestampToPeriod(truncate(x[i]))
#             if time in dictionary.keys():
#                 old = dictionary[time]
#                 dictionary[time] = (old + y[i]) / 2
#             else:
#                 dictionary[time] = y[i]

#         # returning to array
#         y = dictionary.values()
#         x = dictionary.keys()

#         # sorting by time
#         zipped_lists = zip(x, y)
#         sorted_pairs = sorted(zipped_lists)

#         tuples = zip(*sorted_pairs)
#         x, y = [ list(tuple) for tuple in  tuples]

#         # converting timestamps to date
#         x_dates = []
#         for time in x:
#             x_date = datetime.fromtimestamp(time).strftime('%d-%m-%y')
#             x_dates.append(x_date)

#         # plotting the points
#         plt.plot(x_dates, y, label = strand, color = PLOT_COLORS[strand])
    
#     # naming
#     plt.xlabel('Time')
#     plt.ylabel('Evaluation')
#     plt.title('Strands progression')
#     plt.get_current_fig_manager().canvas.set_window_title('LJM Data')
    
#     plt.legend()
#     plt.show()
    
