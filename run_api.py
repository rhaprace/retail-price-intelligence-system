"""
Simple script to run the API server.
"""
import uvicorn


def main():
    """Main entry point for API server."""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()

