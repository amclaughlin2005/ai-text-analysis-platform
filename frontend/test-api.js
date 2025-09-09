// Quick test script to verify backend API connectivity

async function testBackendAPI() {
    console.log('🧪 Testing Backend API Connection...');
    
    try {
        // Test root endpoint
        console.log('1. Testing root endpoint...');
        const rootResponse = await fetch('http://localhost:8001/');
        const rootData = await rootResponse.json();
        console.log('✅ Root endpoint:', rootData.message);
        
        // Test word cloud modes
        console.log('2. Testing modes endpoint...');
        const modesResponse = await fetch('http://localhost:8001/api/wordcloud/modes');
        const modesData = await modesResponse.json();
        console.log('✅ Available modes:', modesData.modes);
        
        // Test word cloud generation
        console.log('3. Testing word cloud generation...');
        const wordcloudResponse = await fetch('http://localhost:8001/api/wordcloud/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dataset_id: 'frontend-test',
                mode: 'all',
                filters: {}
            })
        });
        
        const wordcloudData = await wordcloudResponse.json();
        console.log('✅ Word cloud data received:', wordcloudData.words?.length, 'words');
        console.log('📊 Sentiment distribution:', wordcloudData.insights?.sentiment_distribution);
        
        console.log('🎉 Backend API is fully functional!');
        console.log('🔗 Frontend can now connect to real backend data');
        
        return true;
        
    } catch (error) {
        console.error('❌ API Test Failed:', error);
        return false;
    }
}

// Run the test if this is executed directly
if (typeof window !== 'undefined') {
    testBackendAPI().then(success => {
        if (success) {
            alert('✅ Backend API is working! Check console for details.');
        } else {
            alert('❌ Backend API test failed. Check console for errors.');
        }
    });
} else {
    // Node.js environment
    testBackendAPI();
}
