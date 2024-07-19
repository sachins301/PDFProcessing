import argparse
from sys import argv
import os
from os import listdir
from os.path import isfile, join

'''
UNFINISHED - TODO
To convert file@id=#id files to #id.fileFormat use > python renameFilesWithIndex.py <path> --indexFiles=True --fileFormat=jpg  
To convert <baseName>.<fileFormat><index> to <baseName>_<index>.<fileFormat> use > python renameFilesWithIndex.py <path> <baseName> (fileFormat is auto picked)
    eg: python .\\renameFilesWithIndex.py C:\\Users\\u1452118\Desktop\eccles\ Utah_Medical_Association_Bulletin
'''
def getDirList(path: str) -> list[str]:
    files = []
    for f in listdir(path):
        if isfile(join(path, f)):
            files += [f]
    return files

# 3 or more arguments - the python file, path to files, base file name, index file process selection
if len(argv) >= 3:
    print(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('--indexFiles', help='Files with file@id =', default=False)
    parser.add_argument('--fileFormat', help='File format =', default=None)
    args, argv = parser.parse_known_args()
    print(args, argv)
    indexFiles = args.indexFiles
    fileExtension = args.fileFormat
    try:
        filePath = argv[0]
        # if the user enters '\' at the end, remove them for uniformity
        filePath = filePath[:-1] if filePath.endswith("\\") else filePath
        fileList = getDirList(filePath)
        print(fileList)
    except:
        print('Could not read path provided')

    try:
        #common/base file name
        if(indexFiles):
            fileName = 'file@id='
        else:
            fileName = argv[1]
    except:
        print('Could not read the filename provided')

    # remove all characters except base filename
    fileList = [file for file in fileList if file.startswith(fileName)]

    for index, file in enumerate(fileList, start=1):
        # get the file extension from the provided list - add more extensions here
        fileExtension = fileExtension or next((f for f in file.split('.') if f in ['pdf', 'jpg', 'jpeg', 'mp4']), None)
        if indexFiles:
            newName = f"{file.split('=')[1]}.{fileExtension}"
        else:
            newName = f'{fileName}_{index}.{fileExtension}'
        os.rename(filePath+'\\'+file, filePath+'\\'+newName)

        print(f"Renamed: {file} to {newName}")

else:
    print('Pass a folder path and file name as argument')

