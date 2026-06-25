package auth

import (
	"net/http"
	"time"
)

type Session struct {
	UserId    int
	Token     string
	createdAt time.Time
}

func (s *Session) SetSessionCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     "session_token",
		Value:    s.Token,
		HttpOnly: true,
		SameSite: http.SameSiteStrictMode,
	})
}
