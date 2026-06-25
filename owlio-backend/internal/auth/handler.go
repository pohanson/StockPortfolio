package auth

import (
	"encoding/json"
	"net/http"
	"owlio-backend/internal/common/apperror"
	"owlio-backend/internal/common/handler"
)

type AuthHandler struct {
	service *AuthService
}

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func NewAuthHandler(service *AuthService) *AuthHandler {
	return &AuthHandler{
		service: service,
	}
}

func (h *AuthHandler) LoginHandler(w http.ResponseWriter, r *http.Request) {
	loginReq, err := handler.ReadJsonBody[LoginRequest](r)
	if err != nil {
		apperror.APIErrorHandler(w, err)
		return
	}

	session, err := h.service.Login(loginReq.Username, loginReq.Password, r.Context())
	if err != nil {
		apperror.APIErrorHandler(w, apperror.ErrInvalidCredentials(err))
		return
	}

	session.SetSessionCookie(w)

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(session)
}
