React-Prov web application
(@Author: Chris Ryan)

------------------------------------------------------------------------

.:: INTRODUCTION ::.

This web application . To run, all that is needed are
the following files, which are located in the /src/ directory:
  >index.html
  >bundle.min.js
  >styles.css

.:: BUILD DEPENDENCIES ::.

All build dependencies are listed in the ./package.json file. The files required
to build bundle.min.js and style.css are located within the /build/ directory.

To rebuild this application on Windows, install Node.js (with npm), launch PowerShell
within this file's directory. Run the command 'npm install' to install all the dependencies.
The commands 'npm run build' and 'npm run build-dev' will compile the css and js files.
However, bundle.min.js will by un-minified (for debugging). Run the command
'npm run build-pro' to compile AND minify the js files.

The npm config file also contains the following script commands to run the application
locally, with hot reloading, on webpack's dev server:
  >'npm run start-server' will start this application through webpack-dev-server
  >'npm run start' will start this application through webpack-dev-server AND launch
    http://localhost:8080 in the default browser.

.:: INITIAL SETUP replace all <*name> below ::.

***Install the necessary items (for linux and Python 2.7):
$ sudo apt-get install python-psycopg2
$ sudo pip install Flask
$ sudo pip install tornado

***Add symlink to the included scripts (to be cleaned up later):
$ sudo ln -s /home/<username>/Documents/react-prov/react-prov/scripts /usr/lib/python2.7/dist-packages/pg_prov

***Setup a launch script for development and production (in ~/bin/, requires ~/logs for production);
$ nano ~/bin/start-prov.sh
  Add the following (swap the last lines to run on 127.0.0.0 instead of listening on all ip's):
    export FLASK_APP=/home/<username>/Documents/react-prov/react-prov/app/run.py
    flask run --host=0.0.0.0
    #python -m flask
  CTRL+O -> ENTER -> CTRL+X
$ chmod u+x ~/bin/start-prov.sh
$ nano ~/bin/start-prov-tornado.sh
  Add the following:
    nohup python /home/<username>/Documents/react-prov/react-prov/app/run-tornado.py > ~/logs/react-prov-tornado.log 2>&1&
    echo $! > ~/logs/run-tornado-pid.txt
  CTRL+O -> ENTER -> CTRL+X
$ chmod u+x ~/bin/start-prov-tornado.sh
$ nano ~/bin/kill-prov-tornado.sh
  Add the following:
    kill `cat ~/logs/run-tornado-pid.txt`
    > ~/logs/run-tornado-pid.txt
$ chmod u+x ~/bin/kill-prov-tornado.sh

***Setup PostgreSQL database on server or at least accessible by the server:

***Create database, create limited user, grant permissions, and import the data:
$ psql -h <hostname> -p <port> -U postgres
=> CREATE DATABASE tiger_ri;
=> CREATE USER <limitedDatabaseUsername> WITH PASSWORD '<password>';
$ sudo psql -h <hostname> -p <port> -U postgres -d tiger_ri < tiger_ri_backup.sql
$ psql -h <hostname> -p <port> -U postgres -d tiger_ri
#The following revoke, grant, alter commands may not be necessary but also don't hurt... (to be tested further)
=> REVOKE CONNECT ON DATABASE tiger_ri FROM PUBLIC;
=> GRANT CONNECT
=> ON DATABASE tiger_ri
=> TO <limitedDatabaseUsername>;
=> ALTER DEFAULT PRIVILEGES
=>   FOR ROLE postgres
=>   IN SCHEMA public
=>   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO <limitedDatabaseUsername>;
#This final grant is definitely necessary however
=> GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <limitedDatabaseUsername>;
=> \q ENTER

Create .pgpass file (on Windows it is -> %appdata%\postgresql\pgpass.conf):
$ nano ~/.pgpass
  Add database connection details for the limited user like the following:
    #hostname:port:database:username:password	--- escape ':' and '\' characters with a '\'
  CTRL+O -> ENTER -> CTRL+X
$ chmod 600 ~/.pgpass
