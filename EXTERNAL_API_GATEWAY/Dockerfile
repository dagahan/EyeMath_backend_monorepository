# Dockerfile для external_api_gateway
# ----------------------------
# 1. Builder stage
# ----------------------------
FROM golang:1.24.2-alpine AS builder

# Setup base software for building an app.
RUN apk add --no-cache git protobuf protobuf-dev protoc

# Устанавливаем air для hot-reload - ИСПРАВЛЕНО!
RUN go install github.com/air-verse/air@latest  # <--- Ключевое исправление

# Creating user "appuser" with home directory /home/appuser 
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /workspace

# Устанавливаем плагины для protoc
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1 \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0

# Добавляем GOPATH/bin в PATH
ENV PATH="$PATH:$(go env GOPATH)/bin"

# Клонируем репозиторий с .proto-файлами
RUN git clone --depth=1 https://github.com/dagahan/EyeMath_protos.git /protos

# Создаём директорию для сгенерированных Go-файлов
RUN mkdir -p /workspace/gen

# Генерируем Go-stubs
RUN protoc \
    -I /protos \
    --go_out=/workspace/gen --go_opt=paths=source_relative \
    --go-grpc_out=/workspace/gen --go-grpc_opt=paths=source_relative \
    /protos/external_api_gateway.proto \
    /protos/service_math_solve.proto

# Копируем исходный код
COPY go.mod go.sum /workspace/
COPY . /workspace

# Собираем бинарь
RUN go mod tidy \
    && go build -o /workspace/bin/app ./

# ----------------------------
# 2. Runtime stage
# ----------------------------
FROM alpine:latest

# Устанавливаем необходимые пакеты
RUN apk add --no-cache ca-certificates

WORKDIR /app

# Копируем собранный бинарь
COPY --from=builder /workspace/bin/app /app/app
COPY --from=builder /workspace/gen /app/gen

# Копируем air из builder - ПУТЬ ОСТАЁТСЯ ПРЕЖНИМ
COPY --from=builder /go/bin/air /usr/local/bin/air

# Копируем конфиг air
COPY --from=builder /workspace/external_api_config.toml /app/

# Создаём пользователя и группу
RUN addgroup -S appgroup && \
    adduser -S -G appgroup appuser && \
    chown -R appuser:appgroup /app

EXPOSE ${PORT}
USER appuser
CMD ["air", "-c", "external_api_config.toml"]