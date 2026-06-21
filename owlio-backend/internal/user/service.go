package user

import (
	"owlio-backend/internal/crypto"
)

var repo UserRepository = NewInMemoryUserRepository()

func CreateUser(user *User) error {
	hash, err := crypto.HashPassword(user.Password)
	if err != nil {
		return err
	}
	user.Password = hash

	return repo.SaveUser(user)
}
