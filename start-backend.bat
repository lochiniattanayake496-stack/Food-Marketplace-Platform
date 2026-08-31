@echo off
echo Starting Backend Microservices...

:: Start Product Service on Port 8001
start "Product Service (8001)" cmd /k "cd backend\product-service && uvicorn app.main:app --reload --port 8001"

:: Start User Service on Port 8002
start "User Service (8002)" cmd /k "cd backend\user-service && uvicorn app.main:app --reload --port 8002"

:: Start Cart Service on Port 8003
start "Cart Service (8003)" cmd /k "cd backend\cart-service && uvicorn app.main:app --reload --port 8003"

:: Wait 3 seconds for Uvicorn servers to initialize
timeout /t 3 /nobreak >nul

:: Open Chrome tabs for all backend OpenAPI/Swagger docs
start chrome "http://localhost:8001/docs" "http://localhost:8002/docs" "http://localhost:8003/docs"

echo All services started and Chrome documentation tabs opened!