package main

import (
	"fmt"
	"os"

	"log/slog"

	//exapigate "GoDocker/gen"

	"github.com/BurntSushi/toml"
)

type EnvConfig struct {
	HOST string `toml:"HOST"`
	PORT int    `toml:"PORT"`
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

	// + добавить запись логов в json прямо как на python.
	return log
}

func main() {
	log := setupLogger("DEBUG")

	log.Info(fmt.Sprintf("Hello!"))

	cfg, err := readConfig("external_api_config.toml")
	if err != nil {
		log.Error("Error loading config: %v", err)
	}

	addr := fmt.Sprintf("%s:%d", cfg.HOST, cfg.PORT)

	log.Info(fmt.Sprintf("Hello! your HOST:PORT is  |  %v", addr))
}
