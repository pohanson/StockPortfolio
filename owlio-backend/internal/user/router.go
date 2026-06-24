package user

import (
	"net/http"
)

func RegisterUserRouter(mux *http.ServeMux, h *UserHandler) http.Handler {
	mux.HandleFunc("POST /", h.CreateUserHandler)
	return mux
}
