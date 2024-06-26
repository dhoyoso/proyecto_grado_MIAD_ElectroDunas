# Define connection parameters
$EC2Address = "ec2-user@ec2-3-208-19-151.compute-1.amazonaws.com"  # Include username
$KeyPath = "C:\Users\dhoyoso\Documents\Maestria UNIANDES\Cursos\PROYECTO APLICADO\electrodunas-key-pair.pem"  # Path to your private key file

# Define repository and server details
$GitRepository = "https://github.com/dhoyoso/proyecto_grado_MIAD_ElectroDunas.git"
$ServerDirectory = "proyecto_grado_MIAD_ElectroDunas"  # Directory name after cloning
$PythonEnvironment = "venv"  # Python virtual environment directory
$GunicornPort = 8000  # Port for Uvicorn server

# Define SSH commands, replacing Windows-style line endings
$SSHCommand = @"
sudo yum install git -y  # Ensure git is installed

# Clone the repository
rm -rf proyecto_grado_MIAD_ElectroDunas

git clone $GitRepository

cd $ServerDirectory/dashboard  # Navigate to the repository directory

# Setup Python virtual environment
python3 -m venv $PythonEnvironment
source $PythonEnvironment/bin/activate
pip3 install -r requirements.txt

# Install gunicorn within virtual environment
pip3 install gunicorn

# Kill any processes using the Gunicorn port
sudo fuser -k $GunicornPort/tcp

# Start Uvicorn with nohup
nohup gunicorn --bind 0.0.0.0:$GunicornPort app:server &
"@ -replace "`r",""

# Use Start-Process for SSH connection
Start-Process ssh -ArgumentList "-i `"$KeyPath`" $EC2Address", $SSHCommand -NoNewWindow -Wait
