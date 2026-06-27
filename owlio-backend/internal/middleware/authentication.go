package middleware

import (
	"context"
	"net/http"
	"owlio-backend/internal/auth"
	"owlio-backend/internal/common/apperror"
	"slices"
)

type AuthMiddleware struct {
	authService      AuthServiceInterface
	whitelistedPaths []string
}

type AuthServiceInterface interface {
	GetSessionFromRequest(r *http.Request) (*auth.Session, bool)
}

func NewAuthMiddleware(authService AuthServiceInterface) *AuthMiddleware {
	return &AuthMiddleware{
		authService:      authService,
		whitelistedPaths: []string{},
	}
}

func (m *AuthMiddleware) SetWhitelistedPaths(paths []string) {
	m.whitelistedPaths = paths
}

func (m *AuthMiddleware) AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Implement your authentication logic here
		// For example, check for a valid token in the request header
		if slices.Contains(m.whitelistedPaths, r.URL.Path) {
			next.ServeHTTP(w, r)
			return
		}

		session, exists := m.authService.GetSessionFromRequest(r)
		if !exists {
			apperror.ErrUnauthorized(nil).WriteJSON(w)
			return
		}
		ctx := context.WithValue(r.Context(), auth.SESSION_CONTEXT_KEY, session)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
