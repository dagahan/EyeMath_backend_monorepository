# Dockerfile was generated from
# https://github.com/lodthe/dockerfiles/blob/main/go/Dockerfile
# Modified by Usov Nikita

FROM golang:1.24.2-alpine


# Setup base software for building an app.
RUN apk update && apk add ca-certificates git gcc g++ libc-dev binutils


# Creating user "appuser" with home directory /home/appuser 
RUN addgroup -S appgroup \
 && adduser  -S appuser -G appgroup


WORKDIR /app


# Download dependencies.
RUN mkdir -p ./binary ./tmp \
    && go install github.com/air-verse/air@latest
COPY go.* ./
RUN go mod download

COPY . .

RUN chown -R appuser:appgroup /app /go/pkg
EXPOSE ${PORT}
USER appuser
CMD ["air", "-c", "external_api_config.toml"]