# Explaining how to use upload_table.py

## Requirements

1. You must have python installed
2. You need to clone this repository. How to do this varies by what your using, so if you don't know
   how, google it.
3. You must install the required libraries for this script. You can do that by using one of the
   following commands:

### Mac (Terminal)

```
python3 -m pip install pandas openpyxl sqlalchemy psycopg2-binary
```

### Windows (Command Prompt/PowerShell)

```
py -m pip install pandas openpyxl sqlalchemy psycopg2-binary
```

## Running the program

Open the **upload_table.py** file in your chosen ide (notepad works too), look through the pydoc,
and then add/edit what method calls you want at the end of the file, all that matters is it's on
indentation level 0.
Then run the file and all should work. If no errors are thrown then it has most likely worked, but
the only way to know for sure is to check the database (**Note**: the database UI only shows the "
public" schema).

### **Common Errors**

A bit about how file/directory paths work. if the file/directory is in the same folder as the script
you can omit the root and just pass in the name i.e. "spreadsheet.xlsx",
but if it's outside the folder that the script is in, then you need to specify that. When in doubt
just use the absolute path i.e. "C:\Users\felix\PyCharmMiscProject\data\otherTestSQL.xlsx".
You can normally find the absolute path in finder or file explorer.

If your pip install completed with no errors yet the script can't find the libraries. I run into
this problem all the time, and it comes down to the fact that the pip is installing to a different
location the where the script is checking for libraries. One easy fix if you use pycharm is to pip
install from the ide window with your project.

## Accessing the database

Once you've uploaded your tables you wil probably want to view the database. The simplest way to do
this is through the [server's webpage](https://railway.com/invite/7vsOAcYhq20). Form the project
window, you can select "Main Postgres Database" and then the "data" tab. This will let you see all
the tables in the default "public" schema. As for viewing custom schema, I don't think the website
will let you. If you want to be able to see a more comprehensive view with the custom schema and be
able to write sql files,
follow [this tutorial](https://drive.google.com/file/d/14kWCtERpuQngLhAijG-0SPWGUsqPhfTT/view?usp=sharing)
which will show you how to connect a pycharm or datagrip project to the database.

**Note**: After uploading data, if you want to view your changes in an ide, make sure you refresh
the database in the ide. Also note that data will not be uploaded immediately if the server is
sleeping. Instead, the upload wil be queued until the server wakes up. You can see and or control
this from the [server's webpage](https://railway.com/invite/7vsOAcYhq20).

## Excel Formatting

* All tables should start at A1
* Row 1 is for headers
* Only one table per sheet
* Do not use (put values) in any cells not being used for the table.
* The sheet name will be used as the table name
    * except if there is only one sheet, then the file name will be the table name.
* This list may change (this is just a start, feel free to suggest additions/changes)

To avoid running into any unforeseen errors stick to xlsx files only. This should not be a problem
unless you are doing weird things with Excel.
