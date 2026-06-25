package auth

import "context"

type SessionRepository interface {
	CreateSession(session *Session, ctx context.Context) error
	GetSessionByToken(token string, ctx context.Context) (*Session, bool)
	DeleteSessionByToken(token string, ctx context.Context) error
}

type InMemorySessionRepo struct {
	sessions map[string]*Session
}

func NewInMemorySessionRepo() *InMemorySessionRepo {
	return &InMemorySessionRepo{
		sessions: make(map[string]*Session),
	}
}

func (r *InMemorySessionRepo) CreateSession(session *Session, ctx context.Context) error {
	r.sessions[session.Token] = session
	return nil
}

func (r *InMemorySessionRepo) GetSessionByToken(token string, ctx context.Context) (*Session, bool) {
	session, exists := r.sessions[token]
	return session, exists
}

func (r *InMemorySessionRepo) DeleteSessionByToken(token string, ctx context.Context) error {
	delete(r.sessions, token)
	return nil
}
