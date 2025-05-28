package app

import (
	"log/slog"

	grpcapp "main/app/grpc"
)

type App struct {
	GRPCSrv *grpcapp.App
}

func New(
	log *slog.Logger,
	grpcPort int,
	storagePath string,
	//tokenTTL time.Duration,
) *App {
	// TODO: инициализировать хранилище (storage)

	// TODO: init auth service (auth)

	grpcApp := grpcapp.New(log, grpcPort, nil)

	return &App{
		GRPCSrv: grpcApp,
	}
}
