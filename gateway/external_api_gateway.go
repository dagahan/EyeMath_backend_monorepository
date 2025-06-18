package main

import (
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"

	"log/slog"

	handler "github.com/dagahan/EyeMath_backend_monorepository/gateway/grpc/handler"

	exapigate "github.com/dagahan/EyeMath_protos/go/exapigate"

	"github.com/BurntSushi/toml"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

type EnvConfig struct {
	HOST        string `toml:"HOST"`
	PORT        int    `toml:"PORT"`
	StoragePath string `toml:"storage_path"`
}

type RootConfig struct {
	Env EnvConfig `toml:"env"`
}

func readConfig(path string) (*EnvConfig, error) {
	var root RootConfig
	if _, err := toml.DecodeFile(path, &root); err != nil {
		return nil, fmt.Errorf("cannot load config %q: %w", path, err)
	}
	return &root.Env, nil
}

func setupLogger(env string) *slog.Logger {
	var log *slog.Logger

	switch env {
	case "DEBUG":
		log = slog.New(
			slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug}),
		)
	case "INFO":
		log = slog.New(
			slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}),
		)
	default:
		log = slog.New(
			slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}),
		)
	}

	//TODO: + добавить запись логов в json прямо как на python.
	return log
}

func runServer(log *slog.Logger, cfg *EnvConfig) (*grpc.Server, net.Listener, error) {
	addr := fmt.Sprintf("%s:%d", cfg.HOST, cfg.PORT)

	listener, err := net.Listen("tcp", addr)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to listen: %w", err)
	}

	server := grpc.NewServer()
	srv := &handler.ServerAPI{}

	// Register reflection service on gRPC server.
	reflection.Register(server)

	exapigate.RegisterExternalApiGatewayServer(server, srv)

	log.Info(fmt.Sprintf("your HOST:PORT is  |  %v", addr))

	return server, listener, nil

}

func main() {
	log := setupLogger("DEBUG")

	cfg, err := readConfig("external_api_config.toml")
	if err != nil {
		log.Error("Error loading config: %v", err)
	}

	server, listener, err := runServer(log, cfg)
	if err != nil {
		log.Error("Server initialization failed", "error", err)
		os.Exit(1)
	}

	// Канал для обработки ошибок запуска сервера
	serverErr := make(chan error, 1)

	// Запускаем сервер в отдельной горутине
	go func() {
		if err := server.Serve(listener); err != nil {
			serverErr <- err
		}
	}()

	log.Info("Server started successfully", "address", listener.Addr().String())

	// Ожидаем сигналов ОС или ошибки сервера
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	select {
	case err := <-serverErr:
		log.Error("Server runtime error", "error", err)
	case sig := <-sigChan:
		log.Info("Received shutdown signal", "signal", sig)
		log.Info("Gracefully stopping server...")
		server.GracefulStop()
		log.Info("Server stopped")
	}
}
