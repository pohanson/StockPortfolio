package user

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"owlio-backend/internal/common/handler"
)

func CreateUserHandler(w http.ResponseWriter, r *http.Request) {
	var req CreateUserRequestJson
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

	// Process the valid request
	err := CreateUser(&User{
		Name:     req.Name,
		Username: req.Username,
		Password: req.Password,
	})

	if err != nil {
		handler.ErrorHandler(w, err)
		return
	}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"detail": "User created successfully"})
}
