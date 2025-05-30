package handler

import (
	"context"
	exapigate "main/gen"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type ServerAPI struct {
	exapigate.UnimplementedExternalApiGatewayServer
}

func SendRequestMathSolver(expression string) (*exapigate.MathSolverResponse, error) {
	conn, err := grpc.Dial("localhost:8001", grpc.WithInsecure())
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	client := exapigate.NewExternalApiGatewayClient(conn)
	res, err := client.MathSolver(
		context.Background(),
		//&exapigate.MathSolverRequest{Expression: expression},
		//&gRPC_math_solve.SolveRequest{Expression: expression},
	)

	if err != nil {
		// Преобразуем gRPC ошибку в статус
		if st, ok := status.FromError(err); ok {
			return &exapigate.MathSolverResponse{
				Status: exapigate.MathSolverResponse_ERROR,
				Result: st.Message(),
			}, nil
		}
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
