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
		apperror.APIErrorWriter(w, err)
		return
	}

	session, err := h.service.Login(loginReq.Username, loginReq.Password, r.Context())
	if err != nil {
		apperror.APIErrorWriter(w, apperror.ErrInvalidCredentials(err))
		return
	}

	session.SetSessionCookie(w)

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(session)
}

func (h *AuthHandler) GetMeHandler(w http.ResponseWriter, r *http.Request) {
	session, exists := h.service.GetSessionFromRequest(r)
	if !exists {
		apperror.APIErrorWriter(w, apperror.ErrUnauthorized(nil))
		return
	}
	user, err := h.service.userRepo.GetUserByID(session.UserID, r.Context())
	if err != nil {
		apperror.APIErrorWriter(w, apperror.ErrUnauthorized(err))
		return
	}

	json.NewEncoder(w).Encode(user)
}
