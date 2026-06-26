package user

import (
	"encoding/json"
	"net/http"
	"owlio-backend/internal/common/apperror"
	"owlio-backend/internal/common/handler"
)

type UserHandler struct {
	service *UserService
}

func NewUserHandler(service *UserService) *UserHandler {
	return &UserHandler{
		service: service,
	}
}

func (h *UserHandler) CreateUserHandler(w http.ResponseWriter, r *http.Request) {
	req, err := handler.ReadJsonBody[CreateUser](r)
	if err != nil {
		apperror.APIErrorWriter(w, err)
		return
	}

	if err := req.Validate(); err != nil {
		apperror.APIErrorWriter(w, err)
		return
	}

	// Process the valid request
	err = h.service.CreateUser(&CreateUser{
		Name:     req.Name,
		Username: req.Username,
		Password: req.Password,
	}, r.Context())

	if err != nil {
		apperror.APIErrorWriter(w, err)
		return
	}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"detail": "User created successfully"})
}
