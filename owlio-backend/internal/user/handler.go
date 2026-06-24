package user

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
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
	var req CreateUser
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		if errors.Is(err, io.EOF) {
			handler.ErrorHandler(w, &handler.MissingRequestBody{})
		} else {
			handler.ErrorHandler(w, err)
		}
		return
	}

	if err := req.Validate(); err != nil {
		handler.ErrorHandler(w, err)
		return
	}
	fmt.Printf("Received request: %+v\n", req)

	// Process the valid request
	err := h.service.CreateUser(&CreateUser{
		Name:     req.Name,
		Username: req.Username,
		Password: req.Password,
	}, r.Context())

	if err != nil {
		handler.ErrorHandler(w, err)
		return
	}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"detail": "User created successfully"})
}
