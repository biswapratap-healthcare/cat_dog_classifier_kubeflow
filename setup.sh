sudo apt-get update
sudo apt-get install git -y
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add –
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce
sudo apt-get install ffmpeg libsm6 libxext6 -y
sudo apt-get install gcc
sudo apt-get install python3-dev -y
sudo apt-get install python3-venv -y
sudo apt-get install libpq-dev python-dev -y
