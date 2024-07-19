import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import re
from datetime import datetime
from common import pdfParser
from common import imageParser
from common import commonUtil




prevYear = '1897'
def process_files(files_df):
    monthList = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER',
                 'NOVEMBER', 'DECEMBER']

    failCount = 0
    prevDate = ''

    #for index, row in files_df.iloc[::8].iterrows():
    for index, row in files_df.iloc[::8].iterrows():
        filename = row['filename']
        date_column = row['date']

        print(f'Processing {filename}')

        '''
        file_path = '../resources/digitalnewspapers/' + filename
        text = pdfParser.pdfToText(file_path)
        textHead = text[:5000]
        '''

        #PDF to JPG
        inputPath = '../resources/digitalnewspapers/'
        outputPath = '../resources/digitalnewspapers/croped/'

        pdfParser.pdfToJpeg(inputPath, outputPath, filename)


        #Image to text
        imgFilename = outputPath+os.path.splitext(filename)[0] + '.jpg'
        textHead = imageParser.imageToText(imgFilename)
        #print(textHead)

        try:

            # Modify the regex as required. For current newspaper, date is followed by "EVENING"
            # Create a regex pattern with the list of months, digits, and year
            pattern = re.compile(r"EVENING,* (" + '|'.join(monthList) + r") (\d+)")

            match = re.search(pattern, textHead.upper())
            year_matches = re.findall(r"1\d{3}", textHead)
            year = year_matches[0] if year_matches else prevYear
            prevYear = year
            if match:
                month = match.group(1)
                day = match.group(2)

                print(f"Match found in {filename}: {month} {day} {year}")
                date = month + " " + day + " " + year
                date_object = datetime.strptime(date, "%B %d %Y")

                # Format the datetime object as needed
                formatted_date = date_object.strftime("%m/%d/%Y")

                # ToDo - Remove this later - temperory logic to handle some of the files that had supplements of 4 pages extra
                if prevDate == formatted_date:
                    index += 4
                    row = files_df.iloc[index]
                else:
                    prevDate = formatted_date

                failCount = 0

            else:
                print(f"No match found in {filename}.")
                formatted_date = "No Match"
                failCount += 1
        except Exception as e:
            print(f"An exception occured while processing {filename}")
            formatted_date = "No Match"
            failCount += 1

            # Update the 'date' column in the DataFrame
        files_df.at[index, 'date'] = formatted_date

        #exit the code if not able to fetch dates from 4 consecutive docs
        if failCount >= 10:
            return files_df




    return files_df


def main():
    directory_path = '../resources/digitalnewspapers'
    files_df = pd.DataFrame({'filename': commonUtil.getDirList(directory_path), 'date': ""})
    files_df.index = range(1, len(files_df) + 1)

    print("Original DataFrame:")
    print(files_df)
    files_df.to_csv('files_df.csv', index=True)

    updated_files_df = process_files(files_df)

    print("\nUpdated DataFrame:")
    print(updated_files_df)

    updated_files_df.to_csv('updated_files.csv', index=True)

if __name__ == "__main__":
    main()