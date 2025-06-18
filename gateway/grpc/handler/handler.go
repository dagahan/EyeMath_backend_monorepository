package handler

import (
	"context"
	"os"
	"strings"

	exapigate "github.com/dagahan/EyeMath_protos/go/exapigate"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"

	mathrecognize "github.com/dagahan/EyeMath_protos/go/math_recognize"
	mathsolve "github.com/dagahan/EyeMath_protos/go/math_solve"
)

type ServerAPI struct {
	exapigate.UnimplementedExternalApiGatewayServer
}

func isRunningInDocker() bool {
	return os.Getenv("RUNNING_INSIDE_DOCKER") != "1"
}

func SendRequestMathSolver(expression string, show_solving_steps bool, render_latex_expressions bool) (*mathsolve.SolveResponse, error) {
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
		LatexExpression:        expression,
		ShowSolvingSteps:       show_solving_steps,
		RenderLatexExpressions: render_latex_expressions,
	}

	res, err := client.Solve(context.Background(), req)
	if err != nil {
		return nil, err
	}

	return res, nil

}

func SendRequestMathRecognizer(normalize_for_sympy bool, image_in_bytes []byte) (*mathrecognize.RecognizeResponse, error) {
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
		NormalizeForSympy: normalize_for_sympy,
		ImageInBytes:      image_in_bytes,
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
	response, err := SendRequestMathSolver(req.LatexExpression, req.ShowSolvingSteps, req.RenderLatexExpressions)

	if err != nil {
		return &exapigate.MathSolverResponse{
			Result: "Failed to contact math service: " + err.Error(),
		}, nil
	}

	// Собираем все результаты в одну строку
	var combinedResults string
	if len(response.Results) > 0 {
		combinedResults = strings.Join(response.Results, "; ")
	}

	// Собираем шаги решения (если есть)
	var solvingSteps string
	if len(response.SolvingSteps) > 0 {
		solvingSteps = strings.Join(response.SolvingSteps, "\n\n")
	}

	return &exapigate.MathSolverResponse{
		Result:       combinedResults,
		SolvingSteps: solvingSteps,
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
