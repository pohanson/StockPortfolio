package user

type UserRepository interface {
	SaveUser(user *User) error
	GetUserByUsername(username string) (*User, bool)
}

type InMemoryUserRepository struct {
	users map[string]*User
}

func (r *InMemoryUserRepository) SaveUser(user *User) error {
	r.users[user.Username] = user
	return nil
}

func (r *InMemoryUserRepository) GetUserByUsername(username string) (*User, bool) {
	if user, exists := r.users[username]; exists {
		return user, true
	}
	return nil, false
}

func NewInMemoryUserRepository() *InMemoryUserRepository {
	return &InMemoryUserRepository{
		users: make(map[string]*User),
	}
}
