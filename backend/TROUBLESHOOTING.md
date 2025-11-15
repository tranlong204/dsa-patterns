# Troubleshooting: Updates Going to Supabase Instead of RDS

## Verification Steps

### Step 1: Check Which API Your Frontend is Using

Open your browser's Developer Console (F12) and check:

1. **Network Tab**: When you make an update, check the request URL
   - Should be: `https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod/api/problems/...`
   - If you see `localhost:8000` or `dsa-patterns-backend.onrender.com`, that's the issue!

2. **Console Tab**: Check for any API_BASE_URL logs
   ```javascript
   console.log(localStorage.getItem('API_BASE_URL'))
   ```

3. **Clear localStorage**: If you have an old API URL cached:
   ```javascript
   localStorage.removeItem('API_BASE_URL')
   location.reload()
   ```

### Step 2: Verify Lambda is Using RDS

Test the debug endpoint:
```bash
curl https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod/debug/database \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Should return:
```json
{
  "RDS_HOST": "SET",
  "SUPABASE_URL": "NOT SET",
  "Database_Type": "RDS",
  "Client_Type": "RDSClient"
}
```

### Step 3: Test Update and Verify

1. Make an update through the UI
2. Note the exact title you set
3. Check RDS directly:
   ```bash
   # Connect to RDS and check the title
   ```
4. Check Supabase directly:
   ```bash
   # Connect to Supabase and check the title
   ```

**If RDS has the new title but Supabase has an old title → Lambda IS using RDS correctly!**

### Step 4: Check for Local Backend

If you have a local backend running, it might still be using Supabase:

```bash
# Check if local backend is running
lsof -i :8000

# If running, stop it or update its .env to use RDS
```

### Step 5: Browser Cache Issues

1. **Hard Refresh**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear Cache**: 
   - Chrome: Settings → Privacy → Clear browsing data → Cached images and files
   - Or use Incognito/Private mode
3. **Check localStorage**: 
   ```javascript
   // In browser console
   localStorage.getItem('API_BASE_URL')
   // Should be: https://5n2tv37eki.execute-api.us-west-1.amazonaws.com/prod
   ```

## Common Issues

### Issue 1: Frontend Using Wrong API URL
**Symptom**: Updates go to Supabase
**Solution**: Check `api.js` - ensure `API_BASE_URL` points to Lambda endpoint

### Issue 2: Local Backend Running
**Symptom**: Updates go to Supabase (local backend uses Supabase)
**Solution**: Stop local backend or update its `.env` to use RDS

### Issue 3: Browser Cache
**Symptom**: UI shows old data
**Solution**: Hard refresh or clear cache

### Issue 4: Wrong Supabase Project
**Symptom**: Checking different Supabase project than expected
**Solution**: Verify you're checking the correct Supabase project

## Current Lambda Configuration

- ✅ RDS_HOST: SET
- ✅ SUPABASE_URL: NOT SET (in Lambda)
- ✅ Database_Type: RDS
- ✅ Client_Type: RDSClient

**Lambda is correctly configured to use RDS!**

