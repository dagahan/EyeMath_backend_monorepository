package handler

import (
	"context"
	exapigate "main/gen"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"

	mathsolve "github.com/dagahan/EyeMath_protos/go/mathsolve"
)

type ServerAPI struct {
	exapigate.UnimplementedExternalApiGatewayServer
}

func SendRequestMathSolver(expression string) (*mathsolve.SolveResponse, error) {
	conn, err := grpc.Dial(
		"localhost:8001",
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
		grpc.WithTimeout(5*time.Second),
	)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	client := mathsolve.NewGRPC_math_solveClient(conn)

	req := &mathsolve.SolveRequest{
		Expression: expression,
	}

	res, err := client.Solve(context.Background(), req)
	if err != nil {
		return nil, err
	}

	return res, nil

}

// Register is a method that handles user registration.
func (s *ServerAPI) Register(ctx context.Context, req *exapigate.RegisterRequest) (resp *exapigate.RegisterResponse, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = status.Errorf(codes.Internal, "panic: %v", r)
		}
	}()

	return &exapigate.RegisterResponse{UserId: 0}, nil
}

func (s *ServerAPI) Login(ctx context.Context, req *exapigate.LoginRequest) (resp *exapigate.LoginResponse, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = status.Errorf(codes.Internal, "panic: %v", r)
		}
	}()

	return &exapigate.LoginResponse{
		Token: "0",
	}, nil
}

func (s *ServerAPI) IsAdmin(ctx context.Context, req *exapigate.IsAdminRequest) (resp *exapigate.IsAdminResponse, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = status.Errorf(codes.Internal, "panic: %v", r)
		}
	}()

	return &exapigate.IsAdminResponse{
		IsAdmin: true,
	}, nil
}

func (s *ServerAPI) MathSolver(ctx context.Context, req *exapigate.MathSolverRequest) (*exapigate.MathSolverResponse, error) {
	response, err := SendRequestMathSolver(req.Expression)

	if err != nil {
		// В случае ошибки возвращаем ответ с статусом ERROR
		return &exapigate.MathSolverResponse{
			Status: exapigate.MathSolverResponse_ERROR,
			Result: "Failed to contact math service: " + err.Error(),
		}, nil
	}

	return &exapigate.MathSolverResponse{
		Status: response.Status,
		Result: response.Result,
	}, nil
}
