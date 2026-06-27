package app

import (
	"context"
	"fmt"
	"net/http"
	"owlio-backend/internal/auth"
	"owlio-backend/internal/db"
	"owlio-backend/internal/middleware"
	"owlio-backend/internal/user"
)

type AppContainer struct {
	DbPool *db.DbService
	Mux    *http.ServeMux
}

func NewAppContainer(connString string, ctx context.Context) *AppContainer {
	dbPool, err := db.NewDbService(ctx, connString)
	if err != nil {
		panic(fmt.Errorf("failed to create database service: %w", err))
	}

	return &AppContainer{
		DbPool: dbPool,
		Mux:    http.NewServeMux(),
	}
}

func (c *AppContainer) InitDomains() {
	mux := http.NewServeMux()
	// Initialize User domain
	userRepo := user.NewPgUserRepo(c.DbPool.Pool)
	userService := user.NewUserService(userRepo)
	userHandler := user.NewUserHandler(userService)
	user.RegisterUserRouter(mux, userHandler)

	// Initialize Auth domain
	authRepo := auth.NewInMemorySessionRepo()
	authService := auth.NewAuthService(userRepo, authRepo)
	authHandler := auth.NewAuthHandler(authService)
	auth.RegisterAuthRouter(mux, authHandler)

	// Create auth middleware
	authMiddleware := middleware.NewAuthMiddleware(authService)
	authMiddleware.SetWhitelistedPaths([]string{"/login", "/signup"})

	c.Mux.Handle("/api/v1/", http.StripPrefix("/api/v1", authMiddleware.AuthMiddleware(mux)))

}

func (c *AppContainer) Close() {
	c.DbPool.Close()
}
