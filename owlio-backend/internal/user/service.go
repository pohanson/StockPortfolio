package user

import (
	"context"
	"owlio-backend/internal/crypto"
)

type UserService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
	return &UserService{
		repo: repo,
	}
}

func (s *UserService) CreateUser(user *CreateUser, ctx context.Context) error {
	hash, err := crypto.HashPassword(user.Password)
	if err != nil {
		return err
	}
	user.Password = hash

	return s.repo.CreateUser(user, ctx)
}
