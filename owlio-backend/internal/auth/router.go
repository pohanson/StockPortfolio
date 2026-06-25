package auth

import (
	"net/http"
)

func RegisterAuthRouter(mux *http.ServeMux, h *AuthHandler) http.Handler {
	mux.HandleFunc("POST /login", h.LoginHandler)
	return mux
}
