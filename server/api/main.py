from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import products, prices, sources, comparisons, alerts, analytics, auth
from .dependencies import test_db_connection
from .rate_limit import setup_rate_limiting

app = FastAPI(
    title="Retail Price Intelligence API",
    description="API for price tracking, comparison, and analytics",
    version="1.0.0"
)

setup_rate_limiting(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(comparisons.router, prefix="/api/comparisons", tags=["comparisons"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/")
def root():
    return {
        "message": "Retail Price Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.get("/api/health/db")
def health_db():
    return test_db_connection()

