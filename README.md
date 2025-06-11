# Explaining how to use upload_table.py
## Requirements

You must have python installed
Additionally you must have certain libraries installed, you can install them by running the following command.
### Mac (Terminal)
```
python3 -m pip install pandas openpyxl sqlalchemy psycopg2-binary
```
### Windows (Command Prompt/PowerShell)
```
py -m pip install pandas openpyxl sqlalchemy psycopg2-binary
```
## Running the program

Then open the **upload_table.py** file in your chosen ide (notepad works too) and add/edit what method calls you want at the end of the file, all that matters is its on indentation level 0.
Then run the file and all should work. If no errors are thrown then it has most likely worked, but the only way to know for sure is to check the database.

### **Note:**
A bit about how file/directory paths work. if the file/directory is in the same folder as the script you can omit the root and just pass in the name i.e. "spreadsheet.xlsx",
but if it's outside the folder that the script is in, then you need to specify that. When in doubt just use the absolute path i.e. "C:\Users\felix\PyCharmMiscProject\data\otherTestSQL.xlsx".
You can normally find the absolute path in finder or file explorer.
