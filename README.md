# eye.math backend monorepository
EyeMath is a web service that provides solving math equations from the image features. 
Instead of entering all the text manually to solve an equation, users can point their smartphone's camera at handsrited math expression and solve it!

EyeMath backend use:
* Python 3.13.x with UV, Ruff and TY.
* Nginx
* Docker
* Docker-Compose (or minikube)
* gRPC
* GraphQL with FastAPI
* PostgreSQL

## How to run the backend on signle node?

First, clone repo and cd into it

```bash
git clone https://github.com/dagahan/EyeMath_backend_monorepository
cd EyeMath_backend_monorepository
```

Then, install docker and docker-compose (or minikube) to your system.

```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt install docker-ce
sudo systemctl status docker
```

You also need to create .env or pass env variables directly.

```bash
cp .env.example .env
```

Finally, run the docker compose.

```bash
sudo docker-compose --env-file .env  up --build
```

Or run minikube

```bash
kubectl run engine=docker
kubectl apply -f ./minikube
```

Now your backend is online!

## Find a bug? 

If you found an issue or would like to submit an improvement to this project, please submit it using the issues tab above.