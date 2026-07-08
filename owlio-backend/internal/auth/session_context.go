package auth

import "context"

const SESSION_CONTEXT_KEY = "session"

func GetSessionFromContext(ctx context.Context) (*Session, bool) {
	session, ok := ctx.Value(SESSION_CONTEXT_KEY).(*Session)
	return session, ok
}
