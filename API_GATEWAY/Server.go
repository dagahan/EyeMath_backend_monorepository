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

	fmt.Printf("Loaded config: HOST=%s, PORT=%d\n", cfg.HOST, cfg.PORT)

	addr := fmt.Sprintf("%s:%d", cfg.HOST, cfg.PORT)

	log.Printf("Starting server on %s\n", addr)

	http.HandleFunc("/", handler)
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
