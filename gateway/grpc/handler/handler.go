package handler

import (
	"context"
	"os"

	exapigate "github.com/dagahan/EyeMath_protos/exapigate"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"

	mathrecognize "github.com/dagahan/EyeMath_protos/mathrecognize"
	mathsolve "github.com/dagahan/EyeMath_protos/mathsolve"
)

type ServerAPI struct {
	exapigate.UnimplementedExternalApiGatewayServer
}

func isRunningInDocker() bool {
	return os.Getenv("RUNNING_INSIDE_DOCKER") != "1"
}

func SendRequestMathSolver(expression string) (*mathsolve.SolveResponse, error) {
	var address string
	// TODO: данную проверку нужно проводить всего один раз, значение вынести в константу.
	if isRunningInDocker() {
		address = "service_math_solve:8001"
		// fmt.Println("Running inside Docker, using service address")
	} else {
		address = "localhost:8001"
		// fmt.Println("Running outside Docker, using localhost address")
	}

	conn, err := grpc.NewClient(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		// grpc.WithBlock(),
		// grpc.WithTimeout(5*time.Second),
	)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	client := mathsolve.NewGRPCMathSolveClient(conn)

	req := &mathsolve.SolveRequest{
		Expression: expression,
	}

	res, err := client.Solve(context.Background(), req)
	if err != nil {
		return nil, err
	}

	return res, nil

}

func SendRequestMathRecognizer(expression []byte) (*mathrecognize.RecognizeResponse, error) {
	var address string
	// TODO: данную проверку нужно проводить всего один раз, значение вынести в константу.
	if isRunningInDocker() {
		address = "service_math_recognize:8002"
		// fmt.Println("Running inside Docker, using service address")
	} else {
		address = "localhost:8002"
		// fmt.Println("Running outside Docker, using localhost address")
	}

	conn, err := grpc.NewClient(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		// grpc.WithBlock(),
		// grpc.WithTimeout(5*time.Second),
	)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	client := mathrecognize.NewGRPCMathRecognizeClient(conn)

	req := &mathrecognize.RecognizeRequest{
		Image: expression,
	}

	res, err := client.Recognize(context.Background(), req)
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

	if s == nil {
		return nil, status.Error(codes.Internal, "server instance is nil")
	}

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
			Result: "Failed to contact math service: " + err.Error(),
		}, nil
	}

	return &exapigate.MathSolverResponse{
		Result: response.Result,
	}, nil
}

func (s *ServerAPI) MathRecognizer(ctx context.Context, req *exapigate.MathRecognizerRequest) (*exapigate.MathRecognizerResponse, error) {
	response, err := SendRequestMathRecognizer(req.Image)

	if err != nil {
		// В случае ошибки возвращаем ответ с статусом ERROR
		return &exapigate.MathRecognizerResponse{
			Result: "Failed to contact math service: " + err.Error(),
		}, nil
	}

	return &exapigate.MathRecognizerResponse{
		Result: response.Result,
	}, nil
}
