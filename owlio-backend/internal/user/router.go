package user

import (
	"net/http"
)

func RegisterUserRouter(mux *http.ServeMux, h *UserHandler) http.Handler {
	return mux
}
