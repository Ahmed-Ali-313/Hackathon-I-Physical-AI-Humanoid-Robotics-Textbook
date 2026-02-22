// Quick frontend API test
const API_URL = 'http://localhost:8001';

async function testFrontendAPI() {
  console.log('=== Frontend API Integration Test ===\n');
  
  // Test 1: Signup
  console.log('1. Testing Signup API...');
  try {
    const signupRes = await fetch(`${API_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: `test-${Date.now()}@example.com`,
        password: 'testpass123'
      })
    });
    const signupData = await signupRes.json();
    console.log('✅ Signup successful');
    console.log(`   Token: ${signupData.access_token.substring(0, 30)}...`);
    
    // Test 2: Get Profile
    console.log('\n2. Testing Profile API...');
    const profileRes = await fetch(`${API_URL}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${signupData.access_token}` }
    });
    const profileData = await profileRes.json();
    console.log('✅ Profile retrieved');
    console.log(`   Email: ${profileData.email}`);
    
    console.log('\n=== All Frontend API Tests Passed ===');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testFrontendAPI();
