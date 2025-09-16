#!/usr/bin/env python3
"""
Test script to verify the organization filter fix works correctly
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to production URL if needed
TEST_CSV_FILE = "/Users/alexmclaughlin/Desktop/Cursor Projects/WordCloud/test 1.csv"

def test_filter_options(dataset_id):
    """Test the filter-options API endpoint"""
    print(f"\n📊 Testing filter options for dataset: {dataset_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/wordcloud/filter-options/{dataset_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filter options retrieved successfully!")
            print(f"   Organizations found: {len(data.get('organizations', []))}")
            print(f"   User emails found: {len(data.get('user_emails', []))}")
            
            if data.get('organizations'):
                print(f"   Sample organizations: {data['organizations'][:5]}")
            else:
                print(f"   ⚠️  No organizations found - this might be the issue!")
                
            if data.get('user_emails'):
                print(f"   Sample user emails: {data['user_emails'][:5]}")
            else:
                print(f"   ⚠️  No user emails found - this might be the issue!")
                
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_populate_existing_dataset(dataset_id, csv_file_path):
    """Test the populate-existing-dataset API endpoint"""
    print(f"\n🔧 Testing populate existing dataset: {dataset_id}")
    
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': ('test.csv', f, 'text/csv')}
            response = requests.post(
                f"{API_BASE_URL}/api/wordcloud/populate-existing-dataset/{dataset_id}",
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset populated successfully!")
            print(f"   Questions updated: {data.get('statistics', {}).get('questions_updated', 0)}")
            print(f"   Organizations found: {data.get('statistics', {}).get('organizations_found', 0)}")
            print(f"   User emails found: {data.get('statistics', {}).get('user_emails_found', 0)}")
            
            if data.get('statistics', {}).get('unique_organizations'):
                print(f"   Sample organizations: {data['statistics']['unique_organizations']}")
            if data.get('statistics', {}).get('unique_emails'):
                print(f"   Sample emails: {data['statistics']['unique_emails']}")
                
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_wordcloud_with_filters(dataset_id):
    """Test word cloud generation with organization filters"""
    print(f"\n🌈 Testing word cloud with org filters for dataset: {dataset_id}")
    
    try:
        # First, get available organizations
        filter_response = requests.get(f"{API_BASE_URL}/api/wordcloud/filter-options/{dataset_id}")
        if filter_response.status_code != 200:
            print(f"❌ Could not get filter options: {filter_response.status_code}")
            return None
            
        filter_data = filter_response.json()
        orgs = filter_data.get('organizations', [])
        
        if not orgs:
            print(f"⚠️  No organizations available for filtering")
            return None
            
        # Test with the first organization
        test_org = orgs[0]
        print(f"🔍 Testing filter with organization: {test_org}")
        
        payload = {
            "dataset_id": dataset_id,
            "mode": "all",
            "filters": {
                "org_names": [test_org],
                "max_words": 20
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/wordcloud/generate-fast",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Word cloud generated successfully!")
            print(f"   Words generated: {len(data.get('words', []))}")
            print(f"   Organization filter applied: {test_org}")
            
            if data.get('words'):
                print(f"   Sample words: {[w.get('word', w.get('text', '')) for w in data['words'][:5]]}")
            
            return data
        else:
            print(f"❌ Word cloud error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing Organization Filter Fix")
    print("=" * 50)
    
    # You'll need to replace this with an actual dataset ID from your system
    dataset_id = input("Enter a dataset ID to test (or press Enter to skip): ").strip()
    
    if not dataset_id:
        print("⏭️  No dataset ID provided. You can manually test with these URLs:")
        print(f"   Filter options: {API_BASE_URL}/api/wordcloud/filter-options/YOUR_DATASET_ID")
        print(f"   Populate dataset: {API_BASE_URL}/api/wordcloud/populate-existing-dataset/YOUR_DATASET_ID")
        return
    
    # Test 1: Check current filter options (might be empty)
    current_filters = test_filter_options(dataset_id)
    
    # Test 2: Populate the dataset with organization data
    if current_filters and not current_filters.get('organizations'):
        print("\n🔧 No organizations found. Trying to populate from CSV...")
        populate_result = test_populate_existing_dataset(dataset_id, TEST_CSV_FILE)
        
        if populate_result and populate_result.get('success'):
            # Test 3: Check filter options again after population
            print("\n📊 Checking filter options after population...")
            updated_filters = test_filter_options(dataset_id)
            
            # Test 4: Try generating word cloud with org filter
            if updated_filters and updated_filters.get('organizations'):
                test_wordcloud_with_filters(dataset_id)
        else:
            print("❌ Failed to populate dataset. Check if the CSV file path is correct.")
    else:
        print("✅ Organizations already available!")
        # Test with existing organizations
        test_wordcloud_with_filters(dataset_id)
    
    print("\n🎉 Testing complete!")
    print("\nNext steps:")
    print("1. Upload a new CSV file - it should now automatically extract org data")
    print("2. Use the filter options API to get available organizations")
    print("3. Apply organization filters in the word cloud interface")

if __name__ == "__main__":
    main()
