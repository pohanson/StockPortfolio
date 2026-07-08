package middleware

import (
	"encoding/json"
	"net/http"
	"strings"
)

type statusResponseWriter struct {
	ResponseWriter http.ResponseWriter
	statusCode     int
	storedWrite    []byte
}

func (srw *statusResponseWriter) WriteHeader(code int) {
	srw.statusCode = code
	// Do not write to header first, allow JsonErrorMiddleware
	// to write header to set the content.
}

func (srw *statusResponseWriter) Write(b []byte) (int, error) {
	srw.storedWrite = b
	return len(b), nil
}

func (srw *statusResponseWriter) Header() http.Header {
	return srw.ResponseWriter.Header()
}

func JSONErrorMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		srw := &statusResponseWriter{
			ResponseWriter: w,
			statusCode:     http.StatusOK,
		}

		next.ServeHTTP(srw, r)

		// Only target this 2, as they are returned from library.
		if srw.statusCode == http.StatusMethodNotAllowed || srw.statusCode == http.StatusNotFound {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(srw.statusCode)
			json.NewEncoder(w).Encode(map[string]string{"error": strings.TrimSpace(string(srw.storedWrite))})
		} else {
			w.WriteHeader(srw.statusCode)
			w.Write(srw.storedWrite)
		}
	})
}
