package user

import (
	"context"
)

type UserService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
	return &UserService{
		repo: repo,
	}
}

// TODO: Better error message, currently it exposes internal state.
func (s *UserService) CreateUser(user *CreateUser, ctx context.Context) error {
	return s.repo.CreateUser(user, ctx)
}
