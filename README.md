# eye.math
eye.math is a cutting-edge platform that allows users to solve handwritten mathematical problems at lightning speed.
using advanced computer vision and machine learning algorithms, the platform analyzes images and converts them into mathematical equations, which are then solved in a step-by-step process.


# Definition of problem
The modern scientific and technological landscape is rapidly evolving, and at its heart are complex mathematical problems that form the foundation of engineering and computational sciences. Today, the need for fast and accurate solutions to nonlinear equations is becoming a fundamental requirement for students, educators, and engineers alike.

Today's services either accurately recognize printed text or simply provide the result without explaining the steps leading to the answer. Most platforms focus on printed formulas and have low recognition accuracy for handwritten input, ranging from 65% to 85%. There is no comprehensive solution cycle available, from recognition to step-by-step problem-solving and LaTeX visualization.


# Project goals
The goal of the project is to create a highly efficient distributed platform that automates the process of recognizing handwritten mathematical problems and produces a ready-to-use visualization of the step-by-step solution in LaTeX format.
This system addresses the main aspects of working with mathematical expressions, including: recognition of handwritten formulas using convolutional neural networks (CV models), algorithmic solution of equations step by step (using algorithms written in Python), and visualization in LaTeX.


<p>
    <img src="./.github/assets/eye_math.png" alt="Eye Math Logo" width="250"/>
</p>

## Showcase

![eyemath (2)](https://github.com/user-attachments/assets/d1f8fabb-d71f-4393-8bd9-560e79f3aea4)


## Architecture
<p>
    <img src="./.github/assets/architecture.png" alt="Architecture Diagram" width="900"/>
</p>

## Tech Stack
<p>
    <img src="./.github/assets/tech_stack.png" alt="Tech Stack" width="600"/>
</p>

* Python 3.13.x with UV, Ruff, and TY for high-performance execution;
* PyTorch with CUDA acceleration for computer vision models;
* OpenCV for advanced image preprocessing pipelines;
* Nginx as reverse proxy;
* Docker for containerization;
* Kubernetes for production orchestration;
* gRPC for lightning speed of microservices communication;
* GraphQL with FastAPI as client-api;
* PostgreSQL;
* Prometheus and Grafana for observability monitoring.

## How to run the backend on signle node?

First, clone repo and cd into it.

```bash
git clone https://github.com/dagahan/EyeMath_backend_monorepository
cd EyeMath_backend_monorepository
```

Then, install docker and docker-compose (or minikube) to your system.

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

You also need to create .env or pass env variables directly.

```bash
cp .env.example .env
```

Edit your environment variables with nano.

```bash
nano .env
```

Finally, run the docker compose.

```bash
sudo docker-compose --env-file .env  up --build
```

Or run minikube.

```bash
kubectl run engine=docker
kubectl apply -f ./minikube
```

Now your backend is online!

## Find a bug? 

If you found an issue or would like to submit an improvement to this project, please submit it using the issues tab above.
