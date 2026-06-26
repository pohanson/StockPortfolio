package auth

import (
	"context"
	"fmt"
	"net/http"
	"owlio-backend/internal/common/apperror"
	"owlio-backend/internal/crypto"
	"owlio-backend/internal/user"
	"time"
)

type AuthService struct {
	userRepo    user.UserRepository
	sessionRepo SessionRepository
}

func NewAuthService(userRepo user.UserRepository, sessionRepo SessionRepository) *AuthService {
	return &AuthService{
		userRepo:    userRepo,
		sessionRepo: sessionRepo,
	}
}

// Login authenticates the user and creates a session if successful
func (s *AuthService) Login(username, password string, ctx context.Context) (*Session, error) {
	user, err := s.Authenticate(username, password, ctx)
	if err != nil {
		return nil, err
	}

	session, err := s.CreateSession(user, ctx)
	if err != nil {
		return nil, err
	}

	return session, nil
}

// Returns user if user exists and password matches
func (s *AuthService) Authenticate(username, password string, ctx context.Context) (*user.User, error) {
	if username == "" || password == "" {
		return nil, apperror.ErrInvalidRequestBody(fmt.Errorf("Received: username: %s, password: %s", username, password))
	}
	user, passwordHash, exists := s.userRepo.GetUserByUsernameWithPassword(username, ctx)
	if !exists {
		return nil, apperror.ErrInvalidCredentials(fmt.Errorf("User with username %s does not exist", username))
	}

	isValid, err := crypto.VerifyPassword(password, passwordHash)

	if err != nil {
		return nil, apperror.ErrInvalidCredentials(err)
	}

	if isValid {
		return user, nil
	}

	return nil, apperror.ErrInvalidCredentials(err)
}

func (s *AuthService) CreateSession(user *user.User, ctx context.Context) (*Session, error) {
	token, err := crypto.GenerateRandomBytes(32)
	if err != nil {
		return nil, err
	}
	b64token := crypto.EncodeBase64(token)

	session := &Session{
		UserID:     user.ID,
		SessionKey: b64token,
		createdAt:  time.Now(),
	}

	if err := s.sessionRepo.CreateSession(session, ctx); err != nil {
		return nil, err
	}
	return session, nil
}

func (s *AuthService) GetSessionByToken(token string, ctx context.Context) (*Session, bool) {
	session, exists := s.sessionRepo.GetSessionByToken(token, ctx)
	return session, exists
}

func (s *AuthService) DeleteSessionByToken(token string, ctx context.Context) error {
	return s.sessionRepo.DeleteSessionByToken(token, ctx)
}

func (s *AuthService) GetSessionFromRequest(r *http.Request) (*Session, bool) {
	cookie, err := r.Cookie(SESSION_COOKIE_KEY)
	if err != nil {
		return nil, false
	}
	return s.sessionRepo.GetSessionByToken(cookie.Value, context.Background())

}
