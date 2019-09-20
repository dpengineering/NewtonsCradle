# Newtons Cradle Docker Image
This project has been containerized and is available as a docker package

## Installing Docker
Install docker by running ```curl -fsSL https://get.docker.com -o get-docker.sh``` followed by ```sudo sh get-docker.sh``` and finally ```sudo usermod -aG docker pi```

## Docker Run
By default docker doesn't supply a window provider when running a container therefore some flags must be set when calling the run command.
Follow the instructions on Github to pull the docker image to your machine. Run the container by exectuing;
```docker run --privileged --volume="$HOME/.Xauthority:/root/.Xauthority:rw" -v /dev/shm:/devshm --env="DISPLAY" --net=host  newtons-cradle```

## Docker Build
This Docker container was built by taking all needed dependencies from the working image and placing them in a common directory. The Dockerfile was written
to install all necessary packages, pathed off the common directory. The docker container was then built by running the command (executed in the common directory)
```docker build --tag=newtons-cradle .```

### Note
The Docker container must be built on a Raspberry Pi or else it will not be compiled correctly due to CPU Architecutre differences.

Additionally, the build process is very time consuming as the Raspberry Pi does not have a fast CPU. Typical build times take around 30 minutes to complete.
