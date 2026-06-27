package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"owlio-backend/internal/app"
	"owlio-backend/internal/middleware"
)

func main() {
	dbUrl := os.Getenv("DATABASE_URL")
	if dbUrl == "" {
		log.Fatal("DATABASE_URL is not set")
	}

	appContainer := app.NewAppContainer(dbUrl, context.Background())

	defer appContainer.Close()
	appContainer.InitDomains()

	muxWithMiddleware := middleware.JSONErrorMiddleware(appContainer.Mux)
	fmt.Println("Starting server on http://localhost:8000")
	log.Fatal(http.ListenAndServe(":8000", muxWithMiddleware))
	// Uncomment the following line to enable HTTPS with self-signed certificates
	// log.Fatal(http.ListenAndServeTLS(":8000", "./server.crt", "./server.key", apiMux))
}
