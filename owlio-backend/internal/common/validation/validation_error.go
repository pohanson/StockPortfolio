package validation

import "fmt"

type ValidationError struct {
	Field  string
	Input  string
	Detail string
}

func (e *ValidationError) Error() string {
	return e.Detail
}

func (e *ValidationError) Log() string {
	return fmt.Sprintf("Validation error on field '%s': %s (input: '%s')", e.Field, e.Detail, e.Input)
}
