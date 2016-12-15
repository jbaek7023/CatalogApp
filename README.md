rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

# How to Setup
1. install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads?replytocom=98578)

2. install the appropriate version of package by typing things below on your terminal
```
$ pip install werkzeug==0.8.3
$ pip install flask==0.9
$ pip install Flask-Login==0.1.3
```

## How to Run 
1. clone the whole file

2. navigate to the folder which contains the file

3. Open your terminal in the folder and type "vagrant up"

4. type "vagrant ssh"

5. type "cd /vagrant/project.py"

6. set up your database by typing "python db_setup.py"

7. run your localhost by typing "python project.py"

8. open your browser and go to "localhost/http://localhost:5000/"
