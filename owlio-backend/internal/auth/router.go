package auth

import (
	"net/http"
)

func RegisterAuthRouter(mux *http.ServeMux, h *AuthHandler) http.Handler {
	mux.HandleFunc("POST /login", h.LoginHandler)
	mux.HandleFunc("GET /auth/me", h.GetMeHandler)
	return mux
}
