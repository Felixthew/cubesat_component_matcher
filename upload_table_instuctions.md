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

Note: these are also in the requirements.txt.

## Running the program

Open the **upload_table.py** file in your chosen ide (notepad works too), look through the pydoc,
and then add/edit what method calls you want at the end of the file, all that matters is it's on
indentation level 0.
Then run the file and all should work. If no errors are thrown then it has most likely worked, but
the only way to know for sure is to check the database (**Note**: the database UI only shows the "
public" schema).
The database connection string ("DB_URL") can be found in src\backend_solution\database.py. Edit the string there to
upload the database to your intended location.

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

At this point you would need to create your own posgresql database which you can easily do locally,
on your own computer, use a website (like railway which I used in the tutorial), or on a server,
like I later did with oracle cloud. However you make it though, [this tutorial](https://drive.google.com/file/d/14kWCtERpuQngLhAijG-0SPWGUsqPhfTT/view?usp=sharing)
will show you how to access that database through pycharm, all you need is the url.

**Note**: After uploading data, if you want to view your changes in an ide, make sure you refresh
the database in the ide.

## Excel Formatting

* All tables should start at A1
* Row 1 is for headers
* Only one table per sheet
* Do not use (put values) in any cells not being used for the table.
* The sheet name will be used as the table name
* For a comprehensive styleguide check [here.](https://docs.google.com/document/d/11T_ZlRI-ynXiog7w2_ZTOiBS0SRInuRN_kZEVmbFIS0/edit?tab=t.nuv6wc3ir3w8)

To avoid running into any unforeseen errors stick to xlsx files only. This should not be a problem
unless you are doing weird things with Excel.

### A note about the repository

Pycharm projects can be configured differently from computer to computer and this can cause
problems. For the most part, pycharm handles this quite well and when you pull this repo and run the
code it will automatically reconfigure the configuration files, so that it runs without problems.
However, because these files are tracked by git, you may get an error that you have local changes
that will be overwritten by a merge even if you didn't make changes. In this case, stash your
changes and then pull. If you do make intentional changes, push them to GitHub and don't wait.