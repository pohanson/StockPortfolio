package auth

import (
	"net/http"
	"time"
)

const SESSION_COOKIE_KEY = "session_key"

type Session struct {
	UserID int `json:"-"`
	// TODO: Consider not exposing the session key in the JSON response.
	SessionKey string    `json:"session_key"`
	createdAt  time.Time `json:"-"`
}

func (s *Session) SetSessionCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     SESSION_COOKIE_KEY,
		Value:    s.SessionKey,
		HttpOnly: true,
		SameSite: http.SameSiteStrictMode,
	})
}
