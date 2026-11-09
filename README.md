# Fitness Center Members

## Run locally

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set the database configuration in PowerShell (adjust the password as needed):

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your-mysql-password"
$env:DB_NAME = "fitness_center"
$env:FLASK_SECRET_KEY = "set-a-long-random-secret"
```

Start the app:

```powershell
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). MySQL must be running and
the `fitness_center` database and its tables must exist to display member data.
