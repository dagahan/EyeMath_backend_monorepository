package auth

import (
	"context"
	exapigate "main/gen"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type Auth interface {
	Login(
		ctx context.Context,
		email string,
		password string,
		appID int,
	) (token string, err error)
	RegisterNewUser(
		ctx context.Context,
		email string,
		password string,
	) (userID int64, err error)
	IsAdmin(ctx context.Context, userID int64) (bool, error)
}

const (
	emptyValue    = "0"
	emptyValueInt = 0
)

type serverAPI struct {
	exapigate.UnimplementedExternalApiGatewayServer
	auth Auth
}

func Register(gRPC *grpc.Server, auth Auth) {
	exapigate.RegisterExternalApiGatewayServer(gRPC, &serverAPI{auth: auth})
}

func (s *serverAPI) Register(
	ctx context.Context,
	req *exapigate.RegisterRequest,
) (*exapigate.RegisterResponse, error) {
	if err := validateRegister(req); err != nil {
		return nil, err
	}

	userID, err := s.auth.RegisterNewUser(ctx, req.GetEmail(), req.GetPassword())
	if err != nil {
		return nil, status.Error(codes.Internal, "internal error")
	}

	return &exapigate.RegisterResponse{
		UserId: userID,
	}, nil
}

func (s *serverAPI) Login(
	ctx context.Context,
	req *exapigate.LoginRequest,
) (*exapigate.LoginResponse, error) {
	if err := validateLogin(req); err != nil {
		return nil, err
	}

	token, err := s.auth.Login(ctx, req.GetEmail(), req.GetPassword(), int(req.GetAppId()))
	if err != nil {
		return nil, status.Error(codes.Internal, "internal error")
	}

	return &exapigate.LoginResponse{
		Token: token,
	}, nil
}

func (s *serverAPI) IsAdmin(
	ctx context.Context,
	req *exapigate.IsAdminRequest,
) (*exapigate.IsAdminResponse, error) {
	if err := validateIsAdmin(req); err != nil {
		return nil, err
	}

	isAdmin, err := s.auth.IsAdmin(ctx, req.GetUserId())
	if err != nil {
		return nil, status.Error(codes.Internal, "internal error")
	}

	return &exapigate.IsAdminResponse{
		IsAdmin: isAdmin,
	}, nil
}

func validateLogin(req *exapigate.LoginRequest) error {
	if req.GetEmail() == emptyValue {
		return status.Error(codes.InvalidArgument, "email is required")
	}

	if req.GetPassword() == emptyValue {
		return status.Error(codes.InvalidArgument, "password is required")
	}

	if req.GetAppId() == emptyValueInt {
		return status.Error(codes.InvalidArgument, "app_id is required")
	}

	return nil
}

func validateRegister(req *exapigate.RegisterRequest) error {
	if req.GetEmail() == emptyValue {
		return status.Error(codes.InvalidArgument, "email is required")
	}

	if req.GetPassword() == emptyValue {
		return status.Error(codes.InvalidArgument, "password is required")
	}

	return nil
}

func validateIsAdmin(req *exapigate.IsAdminRequest) error {
	if req.GetUserId() == emptyValueInt {
		return status.Error(codes.InvalidArgument, "user_id is required")
	}

	return nil
}
