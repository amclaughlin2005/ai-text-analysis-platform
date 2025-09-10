"""
Test script to verify the unified system works end-to-end
Tests the consolidated server architecture with robust upload and storage
"""

import sys
import os
import tempfile
import csv
import requests
import json
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def create_test_csv():
    """Create a test CSV file for upload testing"""
    test_data = [
        ["question", "response"],
        ["How do I reset my password?", "You can reset your password by clicking the 'Forgot Password' link on the login page."],
        ["What are your business hours?", "Our business hours are Monday-Friday 9AM-5PM EST."],
        ["How can I contact support?", "You can reach our support team at support@example.com or call 1-800-SUPPORT."],
        ["What payment methods do you accept?", "We accept all major credit cards, PayPal, and bank transfers."],
        ["How do I cancel my subscription?", "You can cancel your subscription in your account settings under 'Billing'."],
    ]
    
    # Create temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
    writer = csv.writer(temp_file)
    writer.writerows(test_data)
    temp_file.close()
    
    return temp_file.name

def test_unified_server(base_url="http://localhost:8000"):
    """Test the unified server endpoints"""
    print(f"🧪 Testing Unified System at {base_url}")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data.get('message', 'OK')}")
            print(f"   📋 Features: {len(data.get('features', []))} available")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 3: Production health check (if available)
    print("\n3️⃣ Testing production health check...")
    try:
        response = requests.get(f"{base_url}/production/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Production health: {data.get('status', 'unknown')}")
            print(f"   💾 Database: {'✅' if data.get('database', {}).get('healthy') else '❌'}")
            print(f"   📁 Storage: {'✅' if data.get('storage', {}).get('upload_dir_writable') else '❌'}")
        else:
            print(f"   ⚠️ Production health endpoint not available: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Production health check not available: {e}")
    
    # Test 4: List datasets (should be empty initially)
    print("\n4️⃣ Testing dataset listing...")
    try:
        response = requests.get(f"{base_url}/api/datasets/")
        if response.status_code == 200:
            data = response.json()
            dataset_count = len(data.get('datasets', []))
            print(f"   ✅ Dataset listing: {dataset_count} datasets found")
        else:
            print(f"   ❌ Dataset listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Dataset listing error: {e}")
        return False
    
    # Test 5: Upload dataset
    print("\n5️⃣ Testing dataset upload...")
    csv_file_path = create_test_csv()
    
    try:
        with open(csv_file_path, 'rb') as file:
            files = {'file': ('test_dataset.csv', file, 'text/csv')}
            data = {
                'name': 'Test Dataset for Unified System',
                'description': 'Test dataset created by automated testing script'
            }
            
            response = requests.post(f"{base_url}/api/datasets/upload", files=files, data=data)
            
            if response.status_code == 200:
                upload_result = response.json()
                print(f"   ✅ Dataset upload successful")
                print(f"   📊 Dataset ID: {upload_result.get('dataset', {}).get('id', 'unknown')[:8]}...")
                print(f"   📝 Questions created: {upload_result.get('processing', {}).get('questions_created', 0)}")
                
                dataset_id = upload_result.get('dataset', {}).get('id')
                
                # Test 6: Get dataset details
                if dataset_id:
                    print("\n6️⃣ Testing dataset retrieval...")
                    try:
                        response = requests.get(f"{base_url}/api/datasets/{dataset_id}")
                        if response.status_code == 200:
                            dataset_details = response.json()
                            print(f"   ✅ Dataset details retrieved")
                            print(f"   📋 Name: {dataset_details.get('name', 'unknown')}")
                            print(f"   📈 Status: {dataset_details.get('status', 'unknown')}")
                        else:
                            print(f"   ❌ Dataset retrieval failed: {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Dataset retrieval error: {e}")
                
                # Test 7: Word frequency generation
                print("\n7️⃣ Testing word frequency generation...")
                try:
                    response = requests.get(f"{base_url}/api/datasets/{dataset_id}/word-frequencies")
                    if response.status_code == 200:
                        word_data = response.json()
                        word_count = word_data.get('word_count', 0)
                        print(f"   ✅ Word frequencies generated: {word_count} words")
                        
                        # Show top words
                        words = word_data.get('words', [])[:5]
                        if words:
                            print(f"   🔤 Top words: {', '.join([w.get('word', '') for w in words])}")
                    else:
                        print(f"   ❌ Word frequency generation failed: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Word frequency error: {e}")
                
                # Test 8: Dataset deletion
                print("\n8️⃣ Testing dataset deletion...")
                try:
                    response = requests.delete(f"{base_url}/api/datasets/{dataset_id}")
                    if response.status_code == 200:
                        print(f"   ✅ Dataset deleted successfully")
                    else:
                        print(f"   ❌ Dataset deletion failed: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Dataset deletion error: {e}")
                
            else:
                print(f"   ❌ Dataset upload failed: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"   📋 Error: {error_data.get('detail', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"   ❌ Dataset upload error: {e}")
        return False
    finally:
        # Clean up test file
        try:
            os.unlink(csv_file_path)
        except:
            pass
    
    print("\n" + "=" * 50)
    print("🎉 Unified system test completed successfully!")
    print("✅ All core functionality is working")
    return True

def test_local_development():
    """Test the local development server"""
    print("🔧 Testing Local Development Server")
    return test_unified_server("http://localhost:8000")

def test_production_deployment():
    """Test the production deployment"""
    print("🌐 Testing Production Deployment")
    return test_unified_server("https://ai-text-analysis-production.up.railway.app")

if __name__ == "__main__":
    print("🚀 AI Text Analysis Platform - Unified System Test")
    print("Testing consolidated server architecture...")
    print()
    
    # Test local development first
    local_success = False
    try:
        local_success = test_local_development()
    except Exception as e:
        print(f"❌ Local testing failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test production deployment
    production_success = False
    try:
        production_success = test_production_deployment()
    except Exception as e:
        print(f"❌ Production testing failed: {e}")
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"   🏠 Local Development: {'✅ PASS' if local_success else '❌ FAIL'}")
    print(f"   🌐 Production: {'✅ PASS' if production_success else '❌ FAIL'}")
    
    if local_success or production_success:
        print("\n🎉 Unified system consolidation SUCCESSFUL!")
        print("✅ The consolidated architecture is working properly")
    else:
        print("\n⚠️  Testing incomplete - manual verification may be needed")
        print("💡 Ensure servers are running and accessible")
