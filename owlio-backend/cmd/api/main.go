package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"owlio-backend/internal/app"
)

func main() {
	dbUrl := os.Getenv("DATABASE_URL")
	if dbUrl == "" {
		log.Fatal("DATABASE_URL is not set")
	}

	appContainer := app.NewAppContainer(dbUrl, context.Background())

	defer appContainer.Close()
	appContainer.InitDomains()

	fmt.Println("Starting server on https://localhost:8000")
	log.Fatal(http.ListenAndServeTLS(":8000", "./server.crt", "./server.key", appContainer.Mux))
}
