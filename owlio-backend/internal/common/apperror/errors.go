package apperror

import (
	"encoding/json"
	"errors"
	"net/http"
)

type AppError struct {
	Detail     string
	StatusCode int // http.Status*
	Err        error
}

func ErrInvalidCredentials(err error) *AppError {
	return &AppError{
		Detail:     "Invalid username or password",
		StatusCode: http.StatusUnauthorized,
		Err:        err,
	}
}

func ErrMissingRequestBody(err error) *AppError {
	return &AppError{
		Detail:     "Request body is required",
		StatusCode: http.StatusBadRequest,
		Err:        err,
	}
}

func ErrInvalidRequestBody(err error) *AppError {
	return &AppError{
		Detail:     "Invalid request body",
		StatusCode: http.StatusBadRequest,
		Err:        err,
	}
}

func (e *AppError) Error() string {
	return e.Detail
}

func (e *AppError) WriteJson(w http.ResponseWriter) {
	writeJsonError(w, e.StatusCode, e.Detail)
}

func APIErrorHandler(w http.ResponseWriter, err error) {
	var appErr *AppError
	if errors.As(err, &appErr) {
		appErr.WriteJson(w)
		return
	}

	writeJsonError(w, http.StatusInternalServerError, err.Error())
}

func writeJsonError(w http.ResponseWriter, statusCode int, errorMsg string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": errorMsg})
}
