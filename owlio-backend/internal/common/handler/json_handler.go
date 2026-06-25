package handler

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"owlio-backend/internal/common/apperror"
)

func ReadJsonBody[T any](r *http.Request) (*T, error) {
	var req T
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		if errors.Is(err, io.EOF) {
			return nil, apperror.ErrMissingRequestBody(err)
		} else {
			return nil, apperror.ErrInvalidRequestBody(err)
		}
	}
	return &req, nil
}
