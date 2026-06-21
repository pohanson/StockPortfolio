package crypto

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"strings"

	"golang.org/x/crypto/argon2"
)

type Argon2Algorithm string

const (
	Argon2id Argon2Algorithm = "argon2id"
	Argon2i  Argon2Algorithm = "argon2i"
)

type Argon2Config struct {
	Algorithm  Argon2Algorithm
	Time       uint32 // number of iterations
	Memory     uint32
	Threads    uint8
	SaltLength uint32
	KeyLen     uint32
}
type argon2Params struct {
	config Argon2Config
	salt   []byte
	hash   []byte
}

var DefaultArgon2Config = Argon2Config{
	Algorithm:  Argon2id,
	Time:       1,
	Memory:     64 * 1024, // 64 MB
	Threads:    4,
	SaltLength: 16,
	KeyLen:     32,
}

var argon2Config = DefaultArgon2Config

func SetArgon2Config(config Argon2Config) {
	argon2Config = config
}

func GetArgon2Config() Argon2Config {
	return argon2Config
}

func HashPassword(password string) (string, error) {
	salt, err := generateRandomBytes(argon2Config.SaltLength)
	if err != nil {
		return "", err
	}
	switch argon2Config.Algorithm {
	case Argon2id:
		return hashPasswordArgon2id(password, salt, argon2Config)
	case Argon2i:
		return hashPasswordArgon2i(password, salt, argon2Config)
	}
	return "", fmt.Errorf("unsupported Argon2 algorithm")
}

func VerifyPassword(password, hash string) (bool, error) {
	params, err := getArgon2ParamsFromHash(hash)
	if err != nil {
		return false, err
	}

	var computedKey []byte
	switch params.config.Algorithm {
	case Argon2id:
		computedKey = hashKeyArgon2id(password, params.salt, params.config)
	case Argon2i:
		computedKey = hashKeyArgon2i(password, params.salt, params.config)
	default:
		return false, fmt.Errorf("unsupported Argon2 algorithm")
	}

	return subtle.ConstantTimeCompare(computedKey, params.hash) == 1, nil
}

func getArgon2ParamsFromHash(hash string) (params argon2Params, err error) {
	parts := strings.Split(hash, "$")
	if len(parts) != 6 {
		return params, fmt.Errorf("invalid hash format")
	}

	params.config.Algorithm = Argon2Algorithm(parts[1])

	if _, err := fmt.Sscanf(parts[3], "m=%d,t=%d,p=%d", &params.config.Memory, &params.config.Time, &params.config.Threads); err != nil {
		return params, fmt.Errorf("failed to parse argon2 params: %w", err)
	}

	params.salt, err = decodeBase64(parts[4])
	if err != nil {
		return params, err
	}
	params.hash, err = decodeBase64(parts[5])
	if err != nil {
		return params, err
	}
	params.config.KeyLen = uint32(len(params.hash))
	return params, nil
}

func hashKeyArgon2id(password string, salt []byte, config Argon2Config) []byte {
	return argon2.IDKey([]byte(password), salt, config.Time, config.Memory, config.Threads, config.KeyLen)
}

func hashPasswordArgon2id(password string, salt []byte, config Argon2Config) (string, error) {
	key := argon2.IDKey([]byte(password), salt, config.Time, config.Memory, config.Threads, config.KeyLen)
	b64key := encodeBase64(key)
	b64salt := encodeBase64(salt)
	encodedhash := fmt.Sprintf("$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s", argon2.Version, config.Memory, config.Time, config.Threads, b64salt, b64key)

	return encodedhash, nil
}

func hashKeyArgon2i(password string, salt []byte, config Argon2Config) []byte {
	return argon2.Key([]byte(password), salt, config.Time, config.Memory, config.Threads, config.KeyLen)
}

func hashPasswordArgon2i(password string, salt []byte, config Argon2Config) (string, error) {
	key := argon2.Key([]byte(password), salt, config.Time, config.Memory, config.Threads, config.KeyLen)
	b64key := encodeBase64(key)
	b64salt := encodeBase64(salt)
	encodedhash := fmt.Sprintf("$argon2i$v=%d$m=%d,t=%d,p=%d$%s$%s", argon2.Version, config.Memory, config.Time, config.Threads, b64salt, b64key)
	return encodedhash, nil
}

func encodeBase64(key []byte) string {
	return base64.RawStdEncoding.EncodeToString(key)
}

func decodeBase64(encoded string) ([]byte, error) {
	return base64.RawStdEncoding.DecodeString(encoded)
}

func generateRandomBytes(length uint32) ([]byte, error) {
	salt := make([]byte, length)
	n, err := rand.Read(salt)
	if n != int(length) {
		return salt, fmt.Errorf("failed to generate random bytes")
	}
	return salt, err
}
