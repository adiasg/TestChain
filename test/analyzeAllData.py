import os
import pandas

#print(os.listdir('data/'))

analyticsDF = pandas.DataFrame()

for working_dir in os.listdir('data/'):
    working_dir = 'data/'+working_dir+'/'
    try:
        testParametersDF = pandas.read_csv(working_dir+'testParametersDF.csv', index_col=0)
        testResultsDF = pandas.read_csv(working_dir+'testResultsDF.csv', index_col=0)
        testParametersDF['working_dir'] = working_dir
        analyticsDF = analyticsDF.append(pandas.concat([testResultsDF,testParametersDF], axis=1), ignore_index=True)
    except OSError:
        print("OSError for directory:", working_dir)

print(analyticsDF.columns)
analyticsDF = analyticsDF.sort_values(by=['simulation_time', 'number_of_peers', 'lambda_generate', 'lambda_sync'])
print(analyticsDF[['number_of_peers','lambda_generate','lambda_sync','longest_100%_agreed_chain']])
print("---------------------------------------------------------------------")
