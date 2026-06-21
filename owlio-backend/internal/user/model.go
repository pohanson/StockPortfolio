package user

import (
	"errors"
	"owlio-backend/internal/common/validation"
	"time"
)

type User struct {
	Name      string    `json:"name"`
	Username  string    `json:"username"`
	Password  string    `json:"password"`
	CreatedAt time.Time `json:"created_at"`
}

type CreateUserRequestJson struct {
	Name     string `json:"name"`
	Username string `json:"username"`
	Password string `json:"password"`
}

func (r *CreateUserRequestJson) Validate() error {
	var errs []error

	if r.Name == "" {
		errs = append(errs, &validation.ValidationError{Field: "name", Detail: "Name is required"})
	}
	if r.Username == "" {
		errs = append(errs, &validation.ValidationError{Field: "username", Detail: "Username is required"})
	}
	if r.Password == "" {
		errs = append(errs, &validation.ValidationError{Field: "password", Detail: "Password is required"})
	}

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}
