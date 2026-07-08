package auth

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"owlio-backend/internal/common/apperror"
	"owlio-backend/internal/common/handler"
	"owlio-backend/internal/common/validation"
	"owlio-backend/internal/crypto"
	"owlio-backend/internal/user"

	"github.com/go-playground/validator/v10"
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
		apperror.APIErrorWriter(w, apperror.ErrUnauthorized(fmt.Errorf("Unauthorized: Invalid session not found")))
		return
	}
	user, err := h.service.userRepo.GetUserByID(session.UserID, r.Context())
	if err != nil {
		apperror.APIErrorWriter(w, apperror.ErrUnauthorized(err))
		return
	}
	json.NewEncoder(w).Encode(user)
}

type SignupRequest struct {
	Name     string `json:"name"`
	Username string `json:"username"`
	Password string `json:"password"`
}

func (h *AuthHandler) SignupHandler(w http.ResponseWriter, r *http.Request) {
	signupReq, err := handler.ReadJsonBody[SignupRequest](r)
	if err != nil {
		apperror.APIErrorWriter(w, err)
		return
	}

	if err := signupReq.Validate(); err != nil {
		apperror.APIErrorWriter(w, err)
		return
	}

	signupReq.Password, err = crypto.HashPassword(signupReq.Password)
	if err != nil {
		apperror.APIErrorWriter(w, apperror.ErrInvalidRequestBody(fmt.Errorf("Failed to sign up user")))
		return
	}

	// Process the valid request
	err = h.service.userRepo.CreateUser(&user.CreateUser{
		Name:     signupReq.Name,
		Username: signupReq.Username,
		Password: signupReq.Password,
	}, r.Context())

	if err != nil {
		apperror.APIErrorWriter(w, err)
		return
	}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"detail": "User created successfully"})
}

func (r *SignupRequest) Validate() error {
	var errs []error
	validate := validator.New()
	err := validate.Struct(r)
	if err != nil {
		if validationErrors, ok := err.(validator.ValidationErrors); ok {
			for _, v := range validationErrors {
				errs = append(errs, &validation.ValidationError{Field: v.Tag(), Detail: v.Error()})
			}
		}
	}

	if r.Name == "" {
		errs = append(errs, &validation.ValidationError{Field: "name", Detail: "Name is required"})
	} else if len(r.Name) > 50 {
		errs = append(errs, &validation.ValidationError{Field: "name", Detail: "Name must be at most 50 characters long"})
	}
	if r.Username == "" {
		errs = append(errs, &validation.ValidationError{Field: "username", Detail: "Username is required"})
	} else if len(r.Username) > 50 {
		errs = append(errs, &validation.ValidationError{Field: "username", Detail: "Username must be at most 50 characters long"})
	}
	if r.Password == "" {
		errs = append(errs, &validation.ValidationError{Field: "password", Detail: "Password is required"})
	}

	if len(errs) > 0 {
		return apperror.ErrInvalidRequestBody(errors.Join(errs...))
	}
	return nil
}
