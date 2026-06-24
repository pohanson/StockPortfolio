package user

import (
	"errors"
	"fmt"
	"owlio-backend/internal/common/validation"
	"time"

	"github.com/go-playground/validator/v10"
)

type User struct {
	Name      string    `json:"name"`
	Username  string    `json:"username"`
	CreatedAt time.Time `json:"created_at"`
}

type CreateUser struct {
	Name     string `json:"name"`
	Username string `json:"username"`
	Password string `json:"password"`
}

func (r *CreateUser) Validate() error {
	var errs []error
	validate := validator.New()
	err := validate.Struct(r)
	if err != nil {
		fmt.Printf("Validation error: %v\n", err)
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
		return errors.Join(errs...)
	}
	return nil
}
