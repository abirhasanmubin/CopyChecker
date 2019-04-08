# CopyChecker

CopyChecker checks the authenticity of an assignment between two assignments offered to the teacher with just a couple of clicks. This assignment plagiarism checker web application works with common text submission.

#### Prerequisites
Python and MySQL must be installed in machine to run this application.

### Installing

For running CopyChecker:

* First install virtual environment package
```
pip install virtualenv
```
* Make a directory and change to new directory
```
mkdir virt
cd virt
```
* Create a virtual environment
```
virtualenv -p python3 vir_env
```
* If you are a linux user then activate virtual enviroment through
```
source vir_env/bin/activate
```
* If you are a windows user then activate virtual enviroment through
```
vir_env\Scripts\activate
```
* Then git clone project or download
```
git clone https://github.com/abirhasanmubin/CCheck.git
```
* Extract it and go to extracted location
```
cd CCheck
```
* Then install required packages from
```
pip install -r requirements.txt
```
* Finally runserver through
```
python manage.py runserver
```
## Built With

* [Django](https://docs.djangoproject.com/en/2.2//) - The web framework used
* [MySQL](https://www.mysql.com/) - Database

## Algorithm
* [Diff] (https://neil.fraser.name/writing/diff/) - The diff strategy by Neil Fraser.

## Authors

* [Abir Hasan Mubin](https://github.com/abirhasanmubin)
* [Al Imran Rony](https://github.com/Al-ImranRony)

## Manual
[CopyChecker Manual]()
