"""
Simple script to test the API endpoints.
"""
import requests
import json
from uuid import UUID

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}\n")
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")


def test_sources():
    """Test source endpoints."""
    print("=" * 50)
    print("Testing Sources")
    print("=" * 50)
    
    # Get all sources
    print("1. Getting all sources...")
    try:
        response = requests.get(f"{BASE_URL}/api/sources/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            sources = response.json()
            print(f"Found {len(sources)} sources")
            if sources:
                print(f"First source: {sources[0]['name']}\n")
                return sources[0]['id']
            else:
                print("No sources found. Creating one...")
                # Create a test source
                new_source = {
                    "name": "Test Source",
                    "base_url": "https://example.com",
                    "country_code": "US",
                    "currency_code": "USD",
                    "rate_limit_per_minute": 60
                }
                response = requests.post(f"{BASE_URL}/api/sources/", json=new_source, timeout=5)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    source = response.json()
                    print(f"Created source: {source['name']} (ID: {source['id']})\n")
                    return source['id']
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    return None


def test_products():
    """Test product endpoints."""
    print("=" * 50)
    print("Testing Products")
    print("=" * 50)
    
    try:
        # Get all products
        print("1. Getting all products...")
        response = requests.get(f"{BASE_URL}/api/products/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"Found {len(products)} products")
            
            if products:
                product_id = products[0]['id']
                print(f"Using product: {products[0]['name']} (ID: {product_id})\n")
                
                # Get product by ID
                print("2. Getting product by ID...")
                response = requests.get(f"{BASE_URL}/api/products/{product_id}", timeout=5)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"Product: {response.json()['name']}\n")
                
                return product_id
            else:
                print("No products found. Creating one...")
                # Create a test product
                new_product = {
                    "name": "Test Product",
                    "category": "Electronics",
                    "brand": "Test Brand"
                }
                response = requests.post(f"{BASE_URL}/api/products/", json=new_product, timeout=5)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    product = response.json()
                    print(f"Created product: {product['name']} (ID: {product['id']})\n")
                    return product['id']
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    return None


def test_prices():
    """Test price endpoints."""
    print("=" * 50)
    print("Testing Prices")
    print("=" * 50)
    
    try:
        # Get latest prices
        print("1. Getting latest prices...")
        response = requests.get(f"{BASE_URL}/api/prices/latest?limit=10", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            prices = response.json()
            print(f"Found {len(prices)} latest prices\n")
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")


def test_comparisons():
    """Test comparison endpoints."""
    print("=" * 50)
    print("Testing Comparisons")
    print("=" * 50)
    
    try:
        # Get comparisons
        print("1. Getting price comparisons...")
        response = requests.get(f"{BASE_URL}/api/comparisons/?limit=10", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            comparisons = response.json()
            print(f"Found {len(comparisons)} comparisons\n")
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")


def test_alerts(product_id=None):
    """Test alert endpoints."""
    print("=" * 50)
    print("Testing Alerts")
    print("=" * 50)
    
    if not product_id:
        print("No product ID provided, skipping alert creation\n")
        return
    
    try:
        # Get all alerts
        print("1. Getting all alerts...")
        response = requests.get(f"{BASE_URL}/api/alerts/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            alerts = response.json()
            print(f"Found {len(alerts)} alerts\n")
        
        # Create an alert
        print("2. Creating a test alert...")
        new_alert = {
            "product_id": str(product_id),
            "target_price": 99.99,
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/alerts/", json=new_alert, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            alert = response.json()
            print(f"Created alert (ID: {alert['id']})\n")
            return alert['id']
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    return None


def test_analytics():
    """Test analytics endpoints."""
    print("=" * 50)
    print("Testing Analytics")
    print("=" * 50)
    
    try:
        # Get discount analysis
        print("1. Getting discount analysis...")
        response = requests.get(f"{BASE_URL}/api/analytics/discounts?limit=10", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            discounts = response.json()
            print(f"Found {len(discounts)} discount analyses\n")
        else:
            print(f"Error: {response.text}\n")
        
        # Get fake discounts
        print("2. Getting fake discounts...")
        response = requests.get(f"{BASE_URL}/api/analytics/discounts/fake?limit=10", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            fake_discounts = response.json()
            print(f"Found {len(fake_discounts)} fake discounts\n")
        else:
            print(f"Error: {response.text}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Response is not valid JSON")
        print(f"Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"Error: {e}\n")


def check_server():
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("API Testing Script")
    print("=" * 50 + "\n")
    
    # Check if server is running
    print("Checking if API server is running...")
    if not check_server():
        print("\n❌ ERROR: API server is not running or not accessible!")
        print("\nPlease start the server first:")
        print("  python run_api.py")
        print("  or")
        print("  uvicorn api.main:app --reload")
        print(f"\nExpected server URL: {BASE_URL}")
        return
    
    print("✅ Server is running!\n")
    
    try:
        # Test health
        test_health()
        
        # Test sources
        source_id = test_sources()
        
        # Test products
        product_id = test_products()
        
        # Test prices
        test_prices()
        
        # Test comparisons
        test_comparisons()
        
        # Test alerts
        test_alerts(product_id)
        
        # Test analytics
        test_analytics()
        
        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Lost connection to API server.")
        print("Make sure the server is still running.")
    except requests.exceptions.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON response - {e}")
        print("The server may have returned an error page instead of JSON.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

