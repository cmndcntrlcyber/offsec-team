package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type Service struct {
	Name   string `json:"name"`
	URL    string `json:"url"`
	Health string `json:"health"`
	Status string `json:"status"`
}

type Gateway struct {
	services map[string]*Service
}

func NewGateway() *Gateway {
	return &Gateway{
		services: make(map[string]*Service),
	}
}

func (g *Gateway) RegisterService(name, url string) {
	g.services[name] = &Service{
		Name:   name,
		URL:    url,
		Health: fmt.Sprintf("%s/health", url),
		Status: "unknown",
	}
}

func (g *Gateway) CheckHealth(name string) error {
	service, exists := g.services[name]
	if !exists {
		return fmt.Errorf("service %s not found", name)
	}

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(service.Health)
	if err != nil {
		service.Status = "unhealthy"
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 {
		service.Status = "healthy"
	} else {
		service.Status = "unhealthy"
	}

	return nil
}

func (g *Gateway) GetServices() map[string]*Service {
	return g.services
}

func main() {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// CORS configuration
	config := cors.DefaultConfig()
	config.AllowOrigins = []string{
		"https://chat.attck.nexus",
		"https://tools.attck.nexus",
		"https://researcher.c3s.nexus",
		"https://mcp.c3s.nexus",
		"https://rtpi.attck.nexus",
		"http://localhost:3001",
		"http://localhost:8001",
		"http://localhost:8002",
		"http://localhost:8003",
		"http://localhost:8004",
		"http://localhost:8005",
	}
	config.AllowMethods = []string{"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
	config.AllowHeaders = []string{"*"}
	config.AllowCredentials = true

	r.Use(cors.New(config))

	gateway := NewGateway()

	// Register services with updated URLs
	gateway.RegisterService("chat-service", "http://chat-service:8080")
	gateway.RegisterService("tools-service", "http://tools-service:8001")
	gateway.RegisterService("research-service", "http://research-service:8002")
	gateway.RegisterService("mcp-service", "http://mcp-service:8003")
	gateway.RegisterService("rtpi-pen", "http://rtpi-pen:8080")

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":    "healthy",
			"timestamp": time.Now().UTC(),
			"gateway":   "service-gateway",
			"version":   "1.0.0",
			"port":      os.Getenv("PORT"),
		})
	})

	// Services endpoint with health checks
	r.GET("/services", func(c *gin.Context) {
		// Check health of all services
		for name := range gateway.GetServices() {
			gateway.CheckHealth(name)
		}

		c.JSON(200, gin.H{
			"services": gateway.GetServices(),
			"total":    len(gateway.GetServices()),
			"gateway":  "service-gateway",
		})
	})

	// Service discovery endpoint
	r.GET("/discover", func(c *gin.Context) {
		serviceEndpoints := make(map[string]interface{})
		
		for name, service := range gateway.GetServices() {
			gateway.CheckHealth(name)
			serviceEndpoints[name] = gin.H{
				"url":    service.URL,
				"health": service.Health,
				"status": service.Status,
				"endpoints": getServiceEndpoints(name),
			}
		}

		c.JSON(200, gin.H{
			"services": serviceEndpoints,
			"gateway_url": fmt.Sprintf("http://localhost:%s", os.Getenv("PORT")),
			"timestamp": time.Now().UTC(),
		})
	})

	// Proxy requests to services
	r.Any("/proxy/:service/*path", func(c *gin.Context) {
		serviceName := c.Param("service")
		path := c.Param("path")

		service, exists := gateway.services[serviceName]
		if !exists {
			c.JSON(404, gin.H{"error": "Service not found"})
			return
		}

		targetURL := fmt.Sprintf("%s%s", service.URL, path)

		// Forward the request
		client := &http.Client{Timeout: 30 * time.Second}
		req, err := http.NewRequest(c.Request.Method, targetURL, c.Request.Body)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}

		// Copy headers
		for name, values := range c.Request.Header {
			for _, value := range values {
				req.Header.Add(name, value)
			}
		}

		resp, err := client.Do(req)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()

		// Copy response headers
		for name, values := range resp.Header {
			for _, value := range values {
				c.Header(name, value)
			}
		}

		c.Status(resp.StatusCode)
		
		var response interface{}
		if err := json.NewDecoder(resp.Body).Decode(&response); err == nil {
			c.JSON(resp.StatusCode, response)
		}
	})

	// Configuration endpoint
	r.GET("/config", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"cloudflare": gin.H{
				"account_id": os.Getenv("CLOUDFLARE_ACCOUNT_ID"),
				"worker_domain": os.Getenv("WORKER_DOMAIN"),
			},
			"services": gin.H{
				"gateway_port": os.Getenv("PORT"),
				"chat_port": "3001",
				"tools_port": "8001",
				"research_port": "8002",
				"mcp_port": "8003",
				"rtpi_port": "8004",
			},
			"database": gin.H{
				"postgres_url": os.Getenv("POSTGRES_URL"),
				"redis_url": os.Getenv("REDIS_URL"),
			},
		})
	})

	// Start server with updated default port
	port := os.Getenv("PORT")
	if port == "" {
		port = "8005"  // Changed from "8000" to "8005"
	}

	log.Printf("🚀 Service Gateway starting on port %s", port)
	log.Printf("📋 Initialized %d services", len(gateway.services))
	log.Printf("🌐 Available endpoints:")
	log.Printf("   - Health: http://localhost:%s/health", port)
	log.Printf("   - Services: http://localhost:%s/services", port)
	log.Printf("   - Discovery: http://localhost:%s/discover", port)
	log.Printf("   - Config: http://localhost:%s/config", port)
	
	if err := r.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

func getServiceEndpoints(serviceName string) []string {
	endpoints := map[string][]string{
		"chat-service": {"/health", "/openapi.json", "/execute", "/execute/contextual", "/researcher/callback"},
		"tools-service": {"/health", "/agents", "/execute", "/openapi.json"},
		"research-service": {"/health", "/api/research/status", "/api/research/search", "/api/research/analyze"},
		"mcp-service": {"/health", "/api/mcp/status", "/api/mcp/context", "/api/mcp/models"},
		"rtpi-pen": {"/health", "/api/rtpi", "/status"},
	}
	
	if eps, exists := endpoints[serviceName]; exists {
		return eps
	}
	return []string{"/health"}
}
