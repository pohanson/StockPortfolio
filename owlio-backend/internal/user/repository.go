package user

import (
	"context"
	db "owlio-backend/internal/db/sqlc"
)

type UserRepository interface {
	CreateUser(user *CreateUser, ctx context.Context) error
	GetUserByUsername(username string, ctx context.Context) (*User, bool)
}

type PgUserRepo struct {
	q *db.Queries
}

func (r *PgUserRepo) CreateUser(user *CreateUser, ctx context.Context) error {
	_, err := r.q.CreateUser(ctx, db.CreateUserParams{
		Username: user.Username,
		Name:     user.Name,
		Email:    "", // TODO: Edit this when email is implemented
		Password: user.Password,
	})
	return err
}

func (r *PgUserRepo) GetUserByUsername(username string, ctx context.Context) (*User, bool) {
	user, err := r.q.GetUserByUsername(ctx, username)
	if err != nil {
		return nil, false
	}
	return &User{
		Name:     user.Name,
		Username: user.Username,
	}, true
}

func NewPgUserRepo(pool db.DBTX) *PgUserRepo {
	return &PgUserRepo{
		q: db.New(pool),
	}
}
