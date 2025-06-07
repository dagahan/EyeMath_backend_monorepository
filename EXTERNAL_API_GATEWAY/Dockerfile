FROM golang:1.24.2-alpine




# Установка зависимостей
RUN apk add --no-cache git protobuf protobuf-dev protoc ca-certificates

# Создание пользователя и группы (один раз)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Настройка рабочей директории
WORKDIR /workspace

# Установка инструментов
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1 \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0

# Добавление GOPATH/bin в PATH
ENV PATH="$PATH:$(go env GOPATH)/bin"

# Клонирование .proto файлов
RUN git clone --depth=1 https://github.com/dagahan/EyeMath_protos.git /protos

# Генерация Go-кода
RUN mkdir -p gen && \
    protoc \
        -I /protos \
        --go_out=gen --go_opt=paths=source_relative \
        --go_opt=Mservice_math_solve.proto=mathsolve/v1 \
        --go_opt=Mexternal_api_gateway.proto=exapigate/v1 \
        --go-grpc_out=gen --go-grpc_opt=paths=source_relative \
        --go-grpc_opt=Mservice_math_solve.proto=mathsolve/v1 \
        --go-grpc_opt=Mexternal_api_gateway.proto=exapigate/v1 \
        /protos/external_api_gateway.proto \
        /protos/service_math_solve.proto

# Организация сгенерированного кода
RUN mkdir -p gen/mathsolve gen/exapigate \
    && mv gen/service_math_solve*.pb.go gen/mathsolve/ \
    && mv gen/external_api_gateway*.pb.go gen/exapigate/

# Копирование исходного кода и установка зависимостей
COPY go.mod go.sum ./
RUN go mod tidy

COPY . .

# Сборка приложения
RUN go build -o ./bin/app ./

# Настройка прав доступа
RUN chown -R appuser:appgroup /workspace

# Экспорт порта и запуск
EXPOSE ${PORT}
USER appuser
CMD ["./bin/app"]