# Dockerfile was generated from
# https://github.com/lodthe/dockerfiles/blob/main/go/Dockerfile
# Modified by Usov Nikita

FROM golang:1.24.2-alpine


# Setup base software for building an app.
RUN apk update && apk add ca-certificates git gcc g++ libc-dev binutils


WORKDIR /app


# Download dependencies.
RUN mkdir -p ./binary ./tmp
RUN go install github.com/air-verse/air@latest
COPY go.* ./
RUN go mod download


# Copy application source.
COPY . .


#Open port for service
EXPOSE ${PORT}


#Compile Run the application with toml configuration file.
CMD ["air", "-c", ".air.toml"]