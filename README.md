# eye.math backend monorepository
## This is backend monorepo of eye.math project. 
EyeMath is a mobile app that helps users solve math equations. Instead of entering all the text manually to solve an equation, users can point their smartphone's camera at an example and EyeMath will recognize it automatically. After recontition, application make gRPC request to the backend External Api Gateway for getting answer of equation from SERVICE_MATH_SOLVE.

EyeMath backend use:
* Python 3.13.2 with UV (package manager), Ruff (lint and format tool) and TY (static typing tool)
* Golang 1.24.2
* PosgreSQL
* Redis
* PgAdmin
* Docker
* gRPC

## How to run the backend?

First, clone repo and cd into it

```bash
git clone https://github.com/dagahan/EyeMath_backend_monorepository
cd EyeMath_backend_monorepository
```

Then, install docker uv to your system

```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt install docker-ce
sudo systemctl status docker
```

You also need to create .env or pass env variables directly.
Please, see .env.example file!

```bash
cp .env.example .env
```

Finally, run the docker compose.

```bash
sudo docker-compose --env-file .env  up --build
```

Now your backend is online!

## Development stage.
Now let's talk about developing your own fork-project.

## How to develop and testing backend correctly?
There are a few rules:
1. Use exactly the same versions of software to interact with code. Use Declared project Python, Golang versions.
2. Use declared utils for Python: UV, Ruff and TY. Only with that utils project can started correct.
3. Before commiting changes, please, use Ruff and TY features:
```bash
uvx ty check src --ignore unresolved-attribute
```
```bash
ruff check .
```
it will help to lint, format and types your code by following rules at pyproject.toml

## Find a bug? 

If you found an issue or would like to submit an improvement to this project, please submit an issue using the issues tab above. If you would like to submit a PR with fix, reference the issue you created!