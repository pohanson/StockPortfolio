package user

import (
	"net/http"
)

func RegisterUserRouter() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /", CreateUserHandler)
	return mux
}
