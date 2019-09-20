FROM python:3.6.9-slim-buster

# Set working directory
WORKDIR /app
COPY . /app

# Update and install pip
#RUN apt-get -y update && apt-get install -y python3-pip

# Install Kivy
#RUN sh ./kivy-install.sh
RUN apt-get -y update && apt-get install -y python3-pip && apt-get install -y python3-pip && sh ./kivy-install.sh && pip3 install RPi.GPIO spidev apscheduler smbus smbus2

# Install dependencies project is currently running on
RUN pip3 install RaspberryPiCommon/.
RUN pip3 install RaspberryPiCommon/pidev/Kivy/MixPanel/.
RUN pip3 install slushengine/.

# Run the Newtons Cradle
CMD ["python3", "-u", "NewtonsCradle/main.py"]
