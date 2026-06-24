package db

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

type DbService struct {
	Pool *pgxpool.Pool
}

func NewDbService(ctx context.Context, connectionString string) (*DbService, error) {
	config, err := pgxpool.ParseConfig(connectionString)
	if err != nil {
		return nil, fmt.Errorf("failed to parse pool config: %w", err)
	}
	// TODO: Edit config if db access is bottleneck
	pool, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create pool: %w", err)
	}

	// Test the connection
	err = pool.Ping(ctx)
	if err != nil {
		pool.Close()
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &DbService{Pool: pool}, nil
}

func (s *DbService) Close() {
	s.Pool.Close()
}
