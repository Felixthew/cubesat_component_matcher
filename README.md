# Explaining how to use upload_table.py
## Requirements

1. You must have python installed
2. You need to clone the this repository. How to do this varies by what your using, so if you don't know how, google it.
3. You must install the required libraries for this script. You can do that by using one of the following commands:
### Mac (Terminal)
```
python3 -m pip install pandas openpyxl sqlalchemy psycopg2-binary
```
### Windows (Command Prompt/PowerShell)
```
py -m pip install pandas openpyxl sqlalchemy psycopg2-binary
```
## Running the program

Open the **upload_table.py** file in your chosen ide (notepad works too) and add/edit what method calls you want at the end of the file, all that matters is its on indentation level 0.
Then run the file and all should work. If no errors are thrown then it has most likely worked, but the only way to know for sure is to check the database.

### **Common Errors**
A bit about how file/directory paths work. if the file/directory is in the same folder as the script you can omit the root and just pass in the name i.e. "spreadsheet.xlsx",
but if it's outside the folder that the script is in, then you need to specify that. When in doubt just use the absolute path i.e. "C:\Users\felix\PyCharmMiscProject\data\otherTestSQL.xlsx".
You can normally find the absolute path in finder or file explorer.

If your pip install completed with no errors yet the script can't find the libraries. I run into this problemall thetime and it comes down to the fact that the pip is installing to a different
location the where the script is checking for libraries. One easy fix is if you use pycharm to pip install from the ide window with your project.

## Excel Formatting
* All tables should start at A1
* Row 1 is for headers
* Only one table per sheet
* Do not use (put values) in any cells not being used for the table.
* The sheet name will be used as the table name
  * except if there is only one sheet, then the file name will be the table name.
 
To avoid running into any unforeseen errors stick to xlsx files only. This should not be a problem unless you are doing weird things with Excel.
