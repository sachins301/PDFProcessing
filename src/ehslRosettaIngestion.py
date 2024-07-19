import re

from pandas import DataFrame

from common import commonUtil
from common import IngestionTemplate
import pandas as pd
import os
import requests
import json
import argparse


def getColValuesOnSha1(sha1: str, df: DataFrame, col: str):
    if col in df:
        value = df.loc[df['sha1'] == sha1, col]
        if not value.empty:
            return value.iloc[0]
        else:
            return ""
    else:
        return ""

'''
cleanColumns - clean the strings in transfer df, convert & to &amp; and remove non ascii characters
input - transferDf DataFrame
return - DataFrame
'''
def cleanStringColumns(transferDf: DataFrame) -> DataFrame:
    for cols in transferDf.columns:
        if transferDf[cols].dtype == object:
            transferDf[cols] = (transferDf[cols]
                                .str.replace('&', '&amp;')
                                .str.replace('>', '&gt;')
                                .str.replace('<', '&lt;')
                                .str.replace('\'', '&apos;')
                                .str.replace('"', '&quot;')
                                .str.replace(r'[^\x00-\x7F]+', '', regex=True)
                                )
    return transferDf

def main():

    """
    export.tsv
    Query.csv
        use left anti join to find element in export but not in query
        split the data to respective file types
        use the file id to download the files
        add the appropriate extensions
        create the sha and the trasfer.csv
        place the transfer file in some location
        run the python script - eg. ehslRosettaIngestion.py "NOVEL - NANOS Annual Meeting" --skip_download=True

    :return:
    """

    import argparse

    # Add an argument
    parser = argparse.ArgumentParser()
    parser.add_argument('collection', help='Collection Name to passed to isPartOf field')
    parser.add_argument('--skip_download', help='Set this to True to skip downloading of files, files expected to be present in resource/files/ folder', default=False)
    parser.add_argument('--username',
                        help='If the collection website is password protected, enter username',
                        default='')
    parser.add_argument('--password',
                        help='If the collection website is password protected, enter password',
                        default='')
    args = parser.parse_args()
    collection = args.collection
    skip_download = True if args.skip_download == "True" else False
    username = args.username
    password = args.password

    print("Skip Download: ",skip_download)


    input_path = '../resources/ehsl/input/'
    file_path = '../resources/ehsl/files/'
    output_path = '../resources/ehsl/output/'

    export_df = pd.read_csv(input_path+'export.tsv', sep='\t', header=0, encoding='latin-1')
    query_df = pd.read_csv(input_path+'Query.csv', header=0, low_memory=False)

    # Filter out rows not present in query.csv (rossetta) from the export.tsv (collections website)
    export_df = export_df[~export_df[['ark_t']].apply(tuple, 1).isin(query_df[['Identifier (DC)']].apply(tuple, 1))]

    fileTypes = export_df['format_t'].unique().tolist()
    print(fileTypes)

    #file type - extention mapping dictionary - NOT BEING USED ANYMORE ToDo - Remove this part later
    ft_ext_dict = {'video/mp4' : '.mp4',
                   'audio/mpeg': '.mp3',
                   'image/jpeg' : '.jpeg',
                   'application/pdf': '.pdf'}

    #remove null or empty values from fileType list (url resources may have fileformats empty)
    fileTypes = [x for x in fileTypes if pd.notna(x) and x.strip()]

    for fileType in fileTypes:
        export_ft_df = export_df[export_df['format_t'] == fileType]

        # Use the file_s column in export.tsv to get the file extension
        # reason: eg, image/jpeg can have jpg or jpeg extensions
        export_ft_df['filename'] = export_ft_df['id'].astype(str) + "." + export_ft_df['file_s'].str.extract(r'\.(\w+)$').squeeze()
        #file_extension_list = [re.findall(r'\.(\w+)$', _) for _ in export_ft_df['file_s']]

        file_extension_list = []
        id_list = []

        if skip_download == False:
            for index, row in export_ft_df.iterrows():

                file_name = row['file_s']

                # In some cases the file_s column is empty and the files needs to be downloaded with content disposition to get the proper file extension.
                # In such cases download the file separately and rename using the index and origin filname extension.
                if pd.isna(file_name):
                    url = "https://collections.lib.utah.edu/file?id=" + str(row['id'])
                    response = requests.get(url, auth=(username, password))
                    if response.status_code == 200:
                        # Try to extract filename from the Content-Disposition header if available
                        cd = response.headers.get('Content-Disposition')
                        if cd:
                            filename = re.findall(r'filename="([^"]*)"', cd)
                            if filename:
                                filename = filename[0]
                                filename = str(row['id'])+"."+filename.split('.')[-1]
                                full_path = os.path.join(file_path, filename)
                                with open(full_path, 'wb') as f:
                                    f.write(response.content)
                                print(f"File downloaded: {filename}")
                        else:
                            print(f"Failed to download file from URL: {url}")
                else:
                    match = re.findall(r'\.(\w+)$', file_name)
                    file_extension_list.append(match)
                    id_list.append("https://collections.lib.utah.edu/file?id=" + str(row['id']))

            print("id list = ", id_list)

            for url, file_extension in zip(id_list, file_extension_list):
                # Send a GET request to the URL
                response = requests.get(url, auth=(username, password))

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Extract filename from URL, get the id, and add the file extension
                    filename = url.split('=')[-1] + "." + file_extension[0]

                    # Write the content to a file
                    with open(file_path+filename, 'wb') as f:
                        f.write(response.content)
                    print(f"File downloaded: {filename}")
                else:
                    print(f"Failed to download file from URL: {url}")

        # if file type is pdf, wait for user to convert and replace them with 2ab format
        if fileType == 'application/pdf':
            export_ft_df['filename'] = export_ft_df['id'].astype(str) + '_2ab.pdf'
            print('PDF files awaiting conversion. Replace the pdf with 2ab pdf and press enter')
            input("Press Enter to continue...")

        #create the transfer.csv with the sha and filenames
        commonUtil.getShaTransfer(file_path, output_path)

        #populate the fields
        #read data dictionary
        with open('../datadictionary/ehsl.json') as json_file:
            data_dict = json.load(json_file)

        transfer_df = pd.read_csv(output_path+'transfer.csv')
        export_ft_df = export_ft_df.merge(transfer_df[['filename', 'sha1']], "left", "filename")

        for key, value in data_dict.items():
            if value:
                transfer_df[key] = transfer_df['sha1'].apply(lambda x: getColValuesOnSha1(x, export_ft_df, value))

        #first 6 charecters of sha1 to batch column
        transfer_df['batch'] = transfer_df['sha1'].apply(lambda x: str(x)[:8])

        # add isPartOf field
        transfer_df['ispartof'] = collection

        #clean string columns
        transfer_df = cleanStringColumns(transfer_df)

        transfer_df.to_csv(output_path+'transfer.csv', index=False)

        #create a new folder for each filetype within output folder
        output_filetype_path = output_path+"/"+fileType.replace('/', '_')
        os.makedirs(output_filetype_path, exist_ok=True)

        IngestionTemplate.createIngestionTemplate(fileType, output_path+'transfer.csv', file_path, output_filetype_path, True)

        # Iterate over each file in transfer_df['filename']
        for file in transfer_df['filename']:
            # Construct the full path to the file
            file_path_del = os.path.join(file_path, file)

            # Check if the path exists and is a file
            if os.path.exists(file_path_del) and os.path.isfile(file_path_del):
                # Remove the file
                os.remove(file_path_del)
            else:
                print(f"File {file} does not exist or is not a regular file.")


if __name__ == "__main__":
    main()