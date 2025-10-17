-----------------------------------------

Project: Data Explorer

Team: Group 1

-----------------------------------------

Project Description: 



----------------------------------------


## User Creation

### For Linux/Mac (bash):
```bash
export FLASK_APP=Urbanmobility.Backend
flask create-admin
```

### For Windows (PowerShell):
```powershell
$env:FLASK_APP = "Urbanmobility.Backend"
flask create-admin
```

### For Windows (CMD):
```cmd
set FLASK_APP=Urbanmobility.Backend
flask create-admin
```


# Set Flask app
$env:FLASK_APP = "Urbanmobility.Backend"

# Create admin user (will prompt for password)
flask create-admin

# Or use python -m flask
python -m flask create-admin