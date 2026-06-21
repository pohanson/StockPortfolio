package handler

import (
	"encoding/json"
	"net/http"
)

func ErrorHandler(w http.ResponseWriter, err error) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError)
	json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
}

type MissingRequestBody struct{}

func (e *MissingRequestBody) Error() string {
	return "Request body is required"
}
