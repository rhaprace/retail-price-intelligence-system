"""
FastAPI application for Retail Price Intelligence System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import products, prices, sources, comparisons, alerts, analytics
from .dependencies import test_db_connection

app = FastAPI(
    title="Retail Price Intelligence API",
    description="API for price tracking, comparison, and analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(comparisons.router, prefix="/api/comparisons", tags=["comparisons"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Retail Price Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/health/db")
def health_db():
    """Database health check endpoint."""
    return test_db_connection()

