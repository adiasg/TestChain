import os
import pandas

print(os.listdir('data/'))

analyticsDF = pandas.DataFrame()

for working_dir in os.listdir('data/'):
    #working_dir = os.listdir('data/')[0]
    working_dir = 'data/'+working_dir+'/'
    #print(working_dir)
    testParametersDF = pandas.read_csv(working_dir+'testParametersDF.csv', index_col=0)
    #print(testParametersDF)
    #print("---------------------------------------------------------------------")
    testResultsDF = pandas.read_csv(working_dir+'testResultsDF.csv', index_col=0)
    #print(testResultsDF)
    #print("---------------------------------------------------------------------")

    #print(pandas.concat([testParametersDF,testResultsDF], axis=1))
    #print("---------------------------------------------------------------------")

    analyticsDF = analyticsDF.append(pandas.concat([testResultsDF,testParametersDF], axis=1), ignore_index=True)
    #print(analyticsDF)
    #print("---------------------------------------------------------------------")


analyticsDF = analyticsDF.sort_values(by=['number_of_peers'])
analyticsDF = analyticsDF.append(pandas.concat([testResultsDF,testParametersDF], axis=1), ignore_index=True)
print(analyticsDF)
print("---------------------------------------------------------------------")
