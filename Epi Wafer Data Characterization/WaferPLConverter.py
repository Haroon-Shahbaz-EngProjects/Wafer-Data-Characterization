from msilib.schema import Binary
from cv2 import invert
import pandas as pd
import numpy as np
import re
import os
import csv
import sys
import math

from sympy import Line, false, true


#find path of python file
path = os.path.dirname(sys.argv[0])
print ("Le path : ",path)

#assigning all paths needed

HeatmapPath = (os.path.join(path,"OutputHeatmap"))
pathSave= (os.path.join(path,"OutputCSV")) #directory to wherever you wish to save csvs
directory = (os.path.join(path,"InputCSV")) #directory to where input csv are located
tempPath = (os.path.join(path,"temp_docs")) #directory to where input csv are located
googlepath = r"G:\Shared drives\Test_Measurements\1. Test & Measurement Data\1. Reference High EQE\20220420_RGB_CAT2815_ML_Analysis\PL data\PL_CSVS"
#Assigning text strings to be read from Input.txt (User inputs)
rows=16 
col=13
BatchID = "Orignal14"

ReadRows = '# of rows:' ###MAKE INTO THE LIST THING###
ReadCols = '# of columns:'
ReadBatchID = '*optional* BatchID:'
ReadxSpacing = 'x spacing:'
ReadxIncrement = 'x increment:'
ReadxLeftVal = 'x left value:'
ReadxRightVal = 'x right value:'
ReadySpacing = 'y spacing:'
ReadyIncrement = 'y increment:'
ReadyBottomVal = 'y bottomvalue:'
ReadyTopVal = 'y topvalue:'
CartridgestoRemove = 'Cartridges to remove:'

proof = false #booleans for user input
grouped = false
headers = true

SavingtoCloud = false
exit = false

while proof == false: #user input to ask whether the csv will be grouped or not
    option = input("would you like to group csv's? (y/n): ")
    if option == 'y':
        print ("\ngrouping into one csv\n")
        proof = true
        grouped = true
    elif option == 'n':
        print ("\nSeperate CSV's will be made\n")
        proof = true
        grouped = false
    else:
        print ("\nerror: please input 'y' or 'n'\n")

while exit == false: #user input to ask whether the csv will be grouped or not
    option = input("would you like to save csv's to the google cloud (y/n): ")
    if option == 'y':
        print ("\nSaving to Google Cloud\n")
        SavingtoCloud = true
        exit = true
    elif option == 'n':
        print ("\n CSV's will be saved locally \n")
        SavingtoCloud = false
        exit = true
    else:
        print ("\nerror: please input 'y' or 'n'\n")

for filename in os.listdir(directory): #sacn through all csvs in input forlder
    infile = os.path.join(directory, filename)
    Justname = filename.split(".")[0] 
    name = filename

    xspacing=0.7085 #preset values in the case a user input is not located on txt file
    xinc=7.2
    xleft=-51.051
    xright=51.051

    yspacing=-0.76
    yinc=-5.4
    ybot=-48.9
    ytop=48.9

    xpos=xleft
    ypos=ytop
    name = filename
    # Select file 
    allLines = ''
    Prelim_file = open(os.path.join(tempPath,"Input.txt"),'r') #open txt file
    Lines = Prelim_file.readlines()
    for i in Lines: #assign txt file to string
        allLines = allLines + i

    # print (allLines)
    data = Prelim_file.read()
    if CartridgestoRemove in allLines: #find the cartrisdges to remove and place them in seperate txt file
        print ("yes")
        delete = allLines.split(CartridgestoRemove, 1)[1]
        text_file = open(os.path.join(tempPath,"cartIDS.txt"), "w")
        text_file.write(delete)
        text_file.close()
        # print("this is delete",delete)


###CONVERT THIS FOR LOOP TO A LIST###
    for line in Lines: # check for each user input on txt fileand assign them to variable
        if ReadRows in line:
            rows = int(line.split(': ')[1].split('n')[0])
            # print ("rows=: ",rows)
        if ReadCols in line:
            col = int(line.split(': ')[1].split('n')[0]) 
            # print ("col=: ",col)
        if ReadBatchID in line:
            BatchID = line.split(': ')[1].split('\n')[0] 
            # print ("BatchID=: ",BatchID)
        if ReadxSpacing in line:
            xspacing = float(line.split(': ')[1].split('n')[0]) 
            # print ("xspacing=: ",xspacing)
        if ReadxIncrement in line:
            xinc = float(line.split(': ')[1].split('n')[0]) 
            # print ("xinc=: ",xinc)
        if ReadxLeftVal in line:
            xleft = float(line.split(': ')[1].split('n')[0]) 
            # print ("xleft=: ",xleft)
        if ReadxRightVal in line:
            xright = float(line.split(': ')[1].split('n')[0]) 
            # print ("xright=: ",xright)
        if ReadySpacing in line:
            yspacing = float(line.split(': ')[1].split('n')[0]) 
            # print ("yspacing=: ",yspacing)
        if ReadyIncrement in line:
            yinc = float(line.split(': ')[1].split('n')[0]) 
            # print ("yincrement=: ",yinc)
        if ReadyBottomVal in line:
            ybot = float(line.split(': ')[1].split('n')[0]) 
            # print ("ybot=: ",ybot)
        if ReadyTopVal in line:
            ytop = float(line.split(': ')[1].split('n')[0]) 
            # print ("ytop=: ",ytop)

    DelRows = [] #arrays to hold cartridges IDS to delete
    DelCols = []
    DelRows.clear()
    DelCols.clear()

    Le_Discard = open(os.path.join(tempPath,"cartIDS.txt"), "r") #read text file with cartridge IDS to remove
    Le_Data = Le_Discard.readlines()[1:]

    for line in Le_Data: # Append Cartridge IDS tp 2D array to be deleted later
        temp=int((re.sub("[^0-9]", "", line)))
        DelRows.append(temp)
        delcol = ''.join([i for i in line if not i.isdigit()])
        delcol = delcol.split('\n')[0]
        DelCols.append(delcol)
    

    ext = os.path.splitext(os.path.join(directory,name))[-1].lower() #Get extension of file

    if ext == ".dat": #check if file is a .dat file, convert .dat file to an equivalent format to other csvs
        with open(os.path.join(directory,name)) as dat_file, open(os.path.join(tempPath,'tempdata.csv'), 'w') as csv_file: #writing to temporary document
            csv_writer = csv.writer(csv_file)

            for line in dat_file:
                row = [field.strip("") for field in line.split(',')] #Since they are DAT files, you remove the space and seperate by a comma to make it a csv format
                if len(row) == 6 and row[3] and row[4]:
                    csv_writer.writerow(row)
        df = pd.read_csv(os.path.join(tempPath,'tempdata.csv')) #assign csv to dataframe
        df.to_csv(os.path.join(tempPath,'tempdata2.csv'), encoding='utf-8', index=False,) #save dataframe to other csv with no indexes and a utf-8 encoding
        df2 = pd.read_csv(os.path.join(tempPath,'tempdata2.csv'), skiprows=1)
        df2.columns = ['X(mm)','Y(mm)','WLD(nm)','Peak INT','INT Signal','FWHM'] #asignning columns to format of Prolux
        df2x = df2['X(mm)'] #Grabbiong x, y, and wavelength columns
        df2y = df2['Y(mm)']
        df2wave = df2['WLD(nm)']
        df3 = df2.astype(float)
        df3[['X(mm)','Y(mm)','WLD(nm)']].to_csv(os.path.join(directory,Justname+'.csv')) #saving them to csv
        
        
        print ('converted dat to csv')

    if ext == ".dat": # for the red wafers in Shin-Etsu
        infile = os.path.join(directory,Justname+'.csv')
        data = pd.read_csv(infile, encoding='latin-1')
    else:
        data = pd.read_csv(infile, skiprows = 10, encoding='latin-1', usecols = ['X(mm)','Y(mm)','WLD(nm)'])


    datafr = pd.DataFrame(data)#place data from csv into dataframe
    print (datafr)
    # datafr.to_csv('name.csv', index=False)

    # print (data)



    cartridge = [] #arrays to hold the column values
    wafer = []
    mins = []
    maxs = []
    ranges = []
    stds = []



    i=0
    j=0

    def round_to_multiple(number,multiple): #function to take variable and round to nearest multiple of 2
        return multiple * round (number / multiple)

    num = rows
    # print (col)
    while i < num:

        while xpos < xright or j<col:
    #         print(xpos)
    #         print(ypos)
            for index, rows in datafr.iterrows():
                roundedx = round_to_multiple(xpos,2)#get rounded versions of x position and y position
                roundedy = round_to_multiple(ypos,2)
    #            print (roundedrow)
                if (rows['X(mm)'] >= xpos and rows['X(mm)'] <= round_to_multiple((xpos+xinc),2)): #append every data piece within the x range and y range
    #                print ('here')
                    if (rows['Y(mm)'] <= ypos and rows['Y(mm)'] >= round_to_multiple((ypos+yinc),2)):
    #                     print ('grabbing val: ',row['X(mm)'], row['Y(mm)'])
                        cartridge.append(rows['WLD(nm)'])
    #         print (cartridge)
            if not cartridge: #create the empty cartridges
    #             print("cartridge is empty")
                wafer.append(0)
                mins.append(0)
                maxs.append(0)
                ranges.append(0)
                stds.append(0)
            else:
    #             print ("average wavelength of cartridge is: ", np.mean(cartridge))
                wafer.append(np.mean(cartridge)) #send average value of array to Array for storage
                mins.append(np.min(cartridge)) #send minumum value of array to Array for storage
                maxs.append(np.max(cartridge)) #send maximum value of array to Array for storage
                ranges.append(np.max(cartridge)- np.min(cartridge)) #send range value of array to Array for storage
                stds.append(np.std(cartridge))
            cartridge.clear() #clear cartridge array
            xpos = xpos + xinc + xspacing #move on to next cartridge
            j=j+1
    #    print(i)
        j=0
        xpos = xleft #reset x val
        ypos = ypos + yinc+ yspacing #increment y value
        i=i+1
    # print ("done")

    # print(wafer)


    # LeWAFER = LeWAFER[LeWAFER !=0] #remove all 0 cartridges
    delete = ''


    #assign row and column values
 


    file = open(os.path.join(tempPath,"Input.txt"),'r') #open temporary doc
    Lines= file.readlines()

    for line in Lines: # check for each user input on txt fileand assign them to variable
        if ReadRows in line:
            rows = int(line.split(': ')[1].split('n')[0])

    # print ("this is delete",delete)
    # print (DelRows)
    # print (DelCols)

    csvName=name.split(".")[0]

    LeCols = [] #assign arrays to be used later
    LeRows = []
    LeIndex = []
    DelIndexes = []

    AltLeWave = [] #arrays to move data
    AltLeCols = []
    AltLeRows = []
    AltCartridgeID=[]
    AltLeIndex = []
    AltLemins = []
    AltLemaxs = []
    AltLeranges = []
    AltLestds = []

    alpha = rows
    tick=1
    while tick <= rows * col: #assign indexes to each cartridge
        LeIndex.append(int(tick))
        tick = tick +1

    import csv

    a=16
    b=1
    count=0
    while a > 0:
        while b <= col: # Assign the letter values to the columns ###MAKE LIST DICTIONARY FOR EACH LETTER, START AT 3 A==3###
        # print ("column=,",column)
            if (b==1): 
                LeCols.append('ZZZ') #assign the edges as ZZZ to be removed later
    #         print (a)
    #         print (b)          
            elif (b==2):
                #print("Setting 2 to A")
                LeCols.append('A')
            elif (b==3):
                #print("Setting 3 to B")
                LeCols.append('B')
            elif (b==4):
                #print("Setting 4 to c")
                LeCols.append('C')
            elif (b==5):
                #print("Setting 5 to d")
                LeCols.append('D')
            elif (b==6):
                #print("Setting 6 to e")
                LeCols.append('E')
            elif (b==7):
                #print("Setting 7 to f")
                LeCols.append('F')
            elif (b==8):
                #print("Setting 8 to g")
                LeCols.append('G')
            elif (b==9):
                #print("Setting 9 to h")
                LeCols.append('H')
            elif (b==10):
                #print("Setting 10 to i")
                LeCols.append('I')
            elif (b==11):
                #print("Setting 11 to j")
                LeCols.append('J')
            elif (b==12):
                #print("Setting 12 to k")
                LeCols.append('K')
            elif (b==13):
                #print("Setting 13 to l")
                LeCols.append('L')
            if (b==col):
                #print("Setting edge to delete")
                LeCols[-1]=('ZZZ')
            LeRows.append(int(a))
            b=b+1
            count=count+1
        a=a-1
        b=1
    c=0
    d=0
    e=0

    for line in Lines: # check for each user input on txt fileand assign them to variable
        if ReadRows in line:
            rows = int(line.split(': ')[1].split('n')[0])

    while c < len(wafer):   #assign a 0 value to all cartridgeIDS specified on discard.txt file as well as edges of wafer
        while d < len(DelRows):
            
    #         print (DeleteRows[d], " : ", LeRows[c])
    #         print (DeleteCols[d], " : ", LeCols[c])

            if (LeRows[c]==1 or LeRows[c]==rows):
                LeRows[c]=0
                LeCols[c]=0
            if (LeCols[c]=='ZZZ'):
                LeRows[c]=0
                LeCols[c]=0
            if (DelRows[d]==LeRows[c]-1 and DelCols[d] == LeCols[c]):
    #               print ("Deleting row: ", LeRows[c])
    #               print ("Column: ", LeCols[c])
                LeRows[c]=0
                LeCols[c]=0
            d = d+1  
        c = c+1
        d=0

    CartID = []
    y=0
    while y < len(LeRows): #assign Cartridge IDS
        if LeRows[y]!=0:
            temp=LeRows[y]-1
            CartID.append((str(LeCols[y])+str(temp)))
        y=y+1
        
    f=0 
    while f < len(LeIndex): #Append every cartridge not cropped
        if LeRows[f]!=0:
            AltLeWave.append((wafer[f]))
            AltLeRows.append(int(LeRows[f])-1)
            AltLeCols.append((LeCols[f]))
            AltLemins.append(mins[f])
            AltLemaxs.append(maxs[f])
            AltLeranges.append(ranges[f])
            AltLestds.append(stds[f])
        f=f+1

    # print ("lengths")
    # print (len(AltLeWave))
    # print (len(CartID))
    v=0
    JustID = []
    while v < len(AltLeCols): #Append WaferID
        JustID.append(Justname)
        v=v+1

    ArrMin = []
    ArrMax = []

###FOR THE NEXT FEW IF STATEMENTS, KEEP THE IF STATEMENT BUT PASS IN MINARRVAL AND MAXARRVAL BININCREMENT AND NUMOFBINS CAN STAY INSIDE###

    if (AltLeWave[5]>510 and AltLeWave[5]<550):
        Green=true# set boolean to true
        Blue=false
        Red=false

        MinArrVal = 510#min and max of bins
        MaxArrVal = 550
        BinIncrement = 0.3
        NumofBins = ((MaxArrVal-MinArrVal)*BinIncrement)


        temp = MinArrVal
        counter = 0
        while (counter < NumofBins):#Append min and max bins
            ArrMin.append(float(temp))
            ArrMax.append(float(temp+BinIncrement))
            counter = counter + 1
            temp = temp + BinIncrement
        print(ArrMin)
        print(ArrMax)
        counter2 = 0
        counter3 = 0
        BinArr = []
        SubBinArr = []
        inBin = false
        while (counter2 < len(AltLeWave)):
            inBin=false
            while (counter3 < len(ArrMin)):
                if (float(AltLeWave[counter2]) > float(ArrMin[counter3]) and float(AltLeWave[counter2]) < float(ArrMax[counter3])):#Check which bin each wavelength belongs to and append value
                    BinArr.append(counter3+1)
                    Mid = ((ArrMin[counter3]+ArrMax[counter3])/2)
                    if (float(AltLeWave[counter2])>Mid): #Append sub bins
                        SubBinArr.append('B')
                    else:
                        SubBinArr.append('A')
                    inBin=true
                counter3=counter3+1
            if (inBin==false): #check case if a cartridge is at a value outside the bins range
                BinArr.append(0)
                SubBinArr.append('null') 
            counter3=0
            counter2 = counter2+1

    if (AltLeWave[5]>430 and AltLeWave[5]<460):
        Blue=true # set boolean to true
        Green=false
        Red=false

        MinArrVal = 430 #min and max of bins
        MaxArrVal = 460
        BinIncrement = 0.3
        NumofBins = ((MaxArrVal-MinArrVal)*BinIncrement)

        temp = MinArrVal
        counter = 0
        while (counter < NumofBins): #Append min and max bins
            ArrMin.append(temp)
            ArrMax.append(temp+BinIncrement)
            counter = counter + 1
            temp = temp + BinIncrement
        
        counter2 = 0
        counter3 = 0
        BinArr = []
        SubBinArr = []
        inBin = false
        while (counter2 < len(AltLeWave)): #Check which bin each wavelength belongs to and append value
            inBin=false
            while (counter3 < len(ArrMin)):
                if (AltLeWave[counter2] >= ArrMin[counter3] and AltLeWave[counter2] < ArrMax[counter3]):
                    BinArr.append(counter3+1)
                    Mid = ((ArrMin[counter3]+ArrMax[counter3])/2)
                    if (float(AltLeWave[counter2])>Mid): #Append sub bins
                        SubBinArr.append('B')
                    else:
                        SubBinArr.append('A')
                    inBin=true
                counter3=counter3+1
            if (inBin==false):
                BinArr.append(0)
                SubBinArr.append('null')    

                
            counter3=0
            counter2 = counter2+1

    if (AltLeWave[3]>600 and AltLeWave[3]<675):
       
        Red=true # set boolean to true
        Green=false
        Blue=false

        MinArrVal = 600 #min and max of bins
        MaxArrVal = 675
        BinIncrement = 0.3
        NumofBins = ((MaxArrVal-MinArrVal)*BinIncrement)
        temp = MinArrVal
        counter = 0
        while (counter < NumofBins): #Append min and max bins 
            ArrMin.append(temp)
            ArrMax.append(temp+BinIncrement)
            counter = counter + 1
            temp = temp + BinIncrement
        
        counter2 = 0
        counter3 = 0
        BinArr = []
        SubBinArr = []
        inBin = false
        while (counter2 < len(AltLeWave)): #Check which bin each wavelength belongs to and append value
            inBin=false
            while (counter3 < len(ArrMin)):
                if (AltLeWave[counter2] > ArrMin[counter3] and AltLeWave[counter2] < ArrMax[counter3]):#Append sub bins
                    BinArr.append(counter3+1)
                    Mid = ((ArrMin[counter3]+ArrMax[counter3])/2)
                    if (float(AltLeWave[counter2])>Mid):
                        SubBinArr.append('B')
                    else:
                        SubBinArr.append('A')
                    inBin=true
                counter3=counter3+1
            if (inBin==false):
                BinArr.append(0)
                SubBinArr.append('null')
                    
            counter3=0
            counter2 = counter2+1
    
    
    t=0
    StrArray = []
    while (t< len(AltLeWave)): #create column that says available
        StrArray.append("Available")
        t=t+1

    df = pd.DataFrame({ # Columns of csv
    #                    'Index': LeIndex, # Name of column : array of values
                    'WaferID': JustID,
                    'Rows': AltLeRows,
                    'Columns': AltLeCols,
                    'Wavelength (nm)': AltLeWave,
                    'Cartridge ID': CartID,
                    'Minumum value': AltLemins,
                    'Mamimum Value': AltLemaxs,
                    'Range (nm)': AltLeranges,
                    'Standard Deviation (nm)': AltLestds,
                    "Bin Number": BinArr, 
                    "Sub Bin": SubBinArr,
                    "Availability": StrArray
                                   })

    import os
    import matplotlib.pyplot as plt

    if (SavingtoCloud==true): #Create cloud save paths if saving to cloud (MUST have google file stream, also must be )
        cloudpath = os.path.join(googlepath, Justname)
        imgpath = os.path.join(cloudpath,Justname+".jpg")
        sample_file_name = "sample"
        if not os.path.isdir(cloudpath):
            os.makedirs(cloudpath)
    if (SavingtoCloud==false):
        imgpath=os.path.join(HeatmapPath,filename+".jpg")

    

    if (SavingtoCloud==true):     
        if grouped: #Save final dataframe to CSV
            if headers:
                df.to_csv(os.path.join(googlepath,BatchID+"PLGrouped.csv"), mode='a', index=False, header=True)
                headers = false
            else:
                df.to_csv(os.path.join(googlepath,BatchID+"PLGrouped.csv"), mode='a', index=False, header=False)
        else:    
            df.to_csv(os.path.join(googlepath,csvName+"PL.csv"),index=False)#where u save the csv file

    if (SavingtoCloud==false):     
        if grouped: #Save final dataframe to CSV
            if headers:
                df.to_csv(os.path.join(pathSave,BatchID+"PLGrouped.csv"), mode='a', index=False, header=True)
                headers = false
            else:
                df.to_csv(os.path.join(pathSave,BatchID+"PLGrouped.csv"), mode='a', index=False, header=False)
        else:    
            df.to_csv(os.path.join(pathSave,csvName+"PL.csv"),index=False)#where u save the csv file
    #df_wafer.to_csv(os.path.join(pathSave,csvName+"Regular"+".csv"),index=False)#If you want to print a csv with none of the cartridges removed 

    print (df)
    print ("Finished Wafer: ", Justname)
    if ext == ".dat": # for the red wafers in Shin-Etsu Delete temporarycsv made
        os.remove(os.path.join(directory,Justname+".csv"))
    
    import pandas as pd #HEATMAP
    import seaborn as sns
    import matplotlib.pyplot as plt

    LEGOATWAVE = np.round(AltLeWave, 2) #round all wavelengths to 2 deciamals

    data = pd.DataFrame(data={'Rows':AltLeRows, 'Columns':AltLeCols, 'Wavelength (nm)':LEGOATWAVE}) #take rows,cols, and wavelength for heat map
    data = data.pivot(index='Rows', columns='Columns', values='Wavelength (nm)', )
    print (LEGOATWAVE)

    plt.figure(figsize = (16,12))

    ax=sns.heatmap(data, annot=True, fmt='.2f',  linewidths=.5, cbar_kws={'label': 'Wavelength (nm)'}) #create heatmap
    ax.invert_yaxis()

    
    ax.legend(["Wavelength (nm)"])
    ax.set_title(f"Wavelength Wafer Map of {Justname}")
    # plt.show()

   

    plt.savefig(imgpath)

    print ("saving heatmap to ", HeatmapPath)

print ("\nprocess complete")
