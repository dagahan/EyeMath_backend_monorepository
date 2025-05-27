package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/BurntSushi/toml"
)

type EnvConfig struct {
	HOST string `toml:"HOST"`
	PORT int    `toml:"PORT"`
}

type RootConfig struct {
	Env EnvConfig `toml:"env"`
}

type GatewayRequestModel struct {
	request_from string `json:"host"`
	requst_type  string `json:"type"`
}

func readConfig(path string) (*EnvConfig, error) {
	var root RootConfig
	if _, err := toml.DecodeFile(path, &root); err != nil {
		return nil, fmt.Errorf("cannot load config %q: %w", path, err)
	}
	return &root.Env, nil
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "hello world!!533 whaat??\n")
	println("WOW!")
}

func main() {
	cfg, err := readConfig(".air.toml")
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	addr := fmt.Sprintf("%s:%d", cfg.HOST, cfg.PORT)

	// Канал для отслеживания запуска сервера
	// serverReady := make(chan bool)

	// Запускаем сервер в горутине
	go func() {
		log.Printf("Starting server on %s\n", addr)
		http.HandleFunc("/", handler)
		if err := http.ListenAndServe(addr, nil); err != nil {
			log.Fatalf("Server failed: %v", err)
		}
	}()

	// Ждем немного чтобы сервер успел запуститься
	// go func() {
	// 	time.Sleep(500 * time.Millisecond)
	// 	serverReady <- true
	// }()

	// // Ждем сигнала о готовности сервера
	// <-serverReady

	// addr_sent := fmt.Sprintf("%s:%d", "service_math_solve", 8001)

	// // Теперь отправляем запрос
	// url := fmt.Sprintf("http://%s/MaL/5+4%%5E2-30", addr_sent) // Используем адрес из конфига
	// log.Printf("Sending request to: %s\n", url)

	// resp, err := http.Get(url)
	// if err != nil {
	// 	log.Fatalf("Request error: %v", err)
	// }
	// defer resp.Body.Close()

	// body, err := io.ReadAll(resp.Body)
	// if err != nil {
	// 	log.Fatalf("Read error: %v", err)
	// }

	// log.Printf("Response Status: %s", resp.Status)
	// log.Printf("Response Body: %s", body)
}
