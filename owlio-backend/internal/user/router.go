package user

import (
	"net/http"
)

func RegisterUserRouter(mux *http.ServeMux, h *UserHandler) http.Handler {
	mux.HandleFunc("POST /user", h.CreateUserHandler)
	return mux
}
