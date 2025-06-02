# EyeMath backend monorepository


## This is backend monorepo of EyeMath project. 


EyeMath is a mobile app that helps users solve math equations. Instead of entering all the text manually to solve an equation, users can point their smartphone's camera at an example and EyeMath will recognize it automatically. After recontition, application make gRPC request to the backend External Api Gateway for getting answer of equation from SERVICE_MATH_SOLVE.




EyeMath backend use:
* Python 3.12
* Golang 1.24.2
* PosgreSQL
* Redis
* PgAdmin
* Docker
* gRPC




## ARCHETECTURE OF BACKEND

[Mobile app (frontend)] ↔ gRPC ↔ [API External gRPC Gateway (golang)] ↔ gRPC ↔ microservices([MATH_SOLVE] (py),
                                        ↑                                                    [MATH_RECOGNIZE] (py))
                                        ↑          
                                    microservice[Auth] (golang)  
                                        ↓
                                        ↓
                                    ([PostgreSQL], [Redis])





## Find a bug? 

If you found an issue or would like to submit an improvement to this project, please submit an issue using the issues tab above. If you would like to submit a PR with fix, reference the issue you created!