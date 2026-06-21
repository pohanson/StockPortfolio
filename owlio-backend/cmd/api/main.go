package main

import (
	"fmt"
	"log"
	"net/http"
	"owlio-backend/internal/user"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Hello!"))
	})
	mux.Handle("/user/", http.StripPrefix("/user", user.RegisterUserRouter()))
	fmt.Println("Starting server on https://localhost:8000")
	log.Fatal(http.ListenAndServeTLS(":8000", "./server.crt", "./server.key", mux))
}
