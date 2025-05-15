from PyPDF2 import PdfReader;
import pandas as pd;
import glob;
from datetime import datetime;

# This script extracts data from PDF files in the Downloads folder, 
# processes it, and saves it to a CSV file.

pattern = glob.glob("../../../Downloads/Rates*.pdf")

all_dfs = []

def wrangle(path):
    
    with open("desired.txt", "w") as file:
        pass

    
    f = open("test.txt","w")
    reader = PdfReader(f"{path}")
    page = reader.pages[0]
    f.writelines(page.extract_text())
    f.close()
    
    desired_currency_positions = [3,4,5,7]
    f = open("test.txt","r")
    lines = f.readlines()
    f.close()

    #print(lines, "From: ", path)
    
    if lines[1] == 'International Banking & Portfolio Management\n':
        date = lines[2].split("-")
        desired_currency_positions = [4,5,6,8]
    
    elif lines[1] == ' Inputter…………………..\n':
        date = lines[7].split("-")
        desired_currency_positions = [9,11,12,14]
    
    elif lines[1] == '      \n':
        date = lines[5].split("-")
        desired_currency_positions = [7,8,9,11]

    elif lines[1] == '  \n':
        date = lines[4].split("-")
        desired_currency_positions = [6,7,8,10]
        
           

    elif lines[1] == ' \n':
        final = len(lines) - 1
        
        if len(lines[final].split(",")) < 3:
            #print(lines, "From: ", path)
             
            if lines[final] == "Page 1":
                final = final - 1
                
                year_container =  lines[final].split(",")[1]
                day_and_month = lines[final].split(",")[0].split(".")
                day_and_month_length = len(day_and_month)
                final_separator = day_and_month[day_and_month_length-1].split(" ")
                day = final_separator[1]
                month = final_separator[0][5:]
                year = year_container.split("I")[0]
                date = [day, month, year]
                #print(year, "From: ", path)
            
            else:
                print("From: ", path)
                target = lines[final].split(",")[1].split(" ")
                date = [target[1],target[2],target[3]]
                desired_currency_positions = [5,7,8,10]
                #print(lines)

                if "INTERBANK MARKET RATE\n" in lines or "INTERBANK RATE\n" in lines:
                    desired_currency_positions = [6,8,9,11]
                    #print(lines, "From: ", path)

        else:  
            date = [lines[final].split(",")[1].split(" ")[2],lines[final].split(",")[1].split(" ")[1],
            lines[final].split(",")[2]]
            desired_currency_positions = [6,8,9,11] 
                
        if "   "  in date[2] or " "  in date[2]:
            #print(date[2], "From: ", path)
            date[2] = date[2].split(" ")[1]
            desired_currency_positions = [5,7,8,10]  
            #print(lines)
        
        #print(lines, "From: ", path)

    else:
        date = lines[1].split("-")

    #print(date, "From: ", path)
    
    if "20" not in date[2]:
        date[2] = "20" + date[2]

    if date[1] == "Jan":
        date[1] = date[1].replace("Jan","January")

    elif date[1] == "Feb":
        date[1] = date[1].replace("Feb","February")

    elif date[1] == "Mar":    
        date[1] = date[1].replace("Mar","March")

    elif date[1] == "Apr":  
        date[1] = date[1].replace("Apr","April")

    elif date[1] == "Jun":
        date[1] = date[1].replace("Jun","June")

    elif date[1] == "Jul":
        date[1] = date[1].replace("Jul","July")

    elif date[1] == "Aug":
        date[1] = date[1].replace("Aug","August")

    elif date[1] == "Sep":
        date[1] = date[1].replace("Sep","September")

    elif date[1] == "Oct":
        date[1] = date[1].replace("Oct","October")

    elif date[1] == "Nov":
        date[1] = date[1].replace("Nov","November")

    elif date[1] == "Dec":
        date[1] = date[1].replace("Dec","December")
        
    
    if len(date[0]) > 3:
        month = date[0]
        day = date[1]
        date[0] = day
        date[1] = month
        desired_currency_positions = [6,8,9,11]
        #print(lines)

    date = date[0] +" "+date[1] +" " + date[2].strip()

    if date == "26 February 2025c":
        date = "26 February 2025"
        #print(lines, "From: ", path)

    print(date, "From: ", path)
    date = datetime.strptime(date, '%d %B %Y').strftime('%Y-%m-%d')
    
    for i in desired_currency_positions:
        f = open("desired.txt","a")

        lines[i] =( date+" "+ lines[i].replace("*","").replace("  "," ").replace("\n"," ")
        .replace("           "," ").replace("         "," ").replace("        "," ").replace("       "," ").
        replace("      "," ").replace("  "," ").replace("  "," ") )

        #print(lines[i])
        f.writelines(lines[i]+ "\n")
        f.close()

    df= pd.read_csv("desired.txt", sep=" ", header=None,names=["Date","Currency", "Bid", "Ask",
                                                               "Average","edge_case1","edge_case2","edge_case3",
                                                               "edge_case4","edge_case5","edge_case6","edge_case7",
                                                               "edge_case8","edge_case9","edge_case10","edge_case11",
                                                               "edge_case12","edge_case13","edge_case14","edge_case15",
                                                               "edge_case16","edge_case17","edge_case18",
                                                               "edge_case19","edge_case20","edge_case21",
                                                                "edge_case22","edge_case23","edge_case24",
                                                                "edge_case25","edge_case26","edge_case27",
                                                                "edge_case28","edge_case29"])
    #print(df["edge_case3"], "From: ", path)

    if date >= datetime.strptime("08 April 2024", '%d %B %Y').strftime('%Y-%m-%d'):
        df["edge_case3"][0] = df["edge_case3"][0] * 2498.7242

    
    df["ZMK"] = df["Average"][3]
    df["ZAR"] = df["Average"][1]
    df["GBP"] = df["Average"][2]
    df["ZWL"] = df["edge_case3"][0]

    df.drop(columns=["edge_case1","edge_case2","edge_case3",
                    "edge_case4","edge_case5","edge_case6","edge_case7",
                    "edge_case8","edge_case9","edge_case10","edge_case11",
                    "edge_case12","edge_case13","edge_case14","edge_case15",
                    "edge_case16","edge_case17","edge_case18",
                    "edge_case19","edge_case20","edge_case21",
                    "edge_case22","edge_case23","edge_case24",
                    "edge_case25","edge_case26","edge_case27",
                    "edge_case28","edge_case29"], inplace=True)

    
    target_for_removal = ["Currency", "Bid", "Ask","Average"] 
    df.drop(columns=target_for_removal, inplace=True)

    return df

for i in pattern:
    df = wrangle(i)
    all_dfs.append(df)

final_df = pd.concat(all_dfs, ignore_index=True).set_index("Date").drop_duplicates().sort_index(ascending=False)
print(final_df.head())
print(final_df.tail())
print(final_df.shape)

#save
final_df.to_csv("final_rates.csv")

"""
df = wrangle("../../../Downloads/RATES_26_MARCH_2025.pdf")
print(df.head())
print(df.tail())"""