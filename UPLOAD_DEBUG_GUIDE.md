# Form Parser Error - Debugging Guide

## The Error You're Seeing
```
form, files = parser.parse(stream, boundary, content_length)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

This happens when **werkzeug** (Flask's form parser) encounters an issue parsing the multipart FormData.

## Common Causes

1. **Content-Length Mismatch** - The header says one size, but actual data is different
2. **Missing Boundary** - Multipart form data needs a boundary string
3. **Corrupt File Data** - File stream got interrupted or malformed
4. **Size Limits** - Form data exceeds Flask's limits
5. **Incorrect Content-Type** - Not properly set as `multipart/form-data`

## Solutions I've Implemented

### ✅ Fix 1: Increased Upload Limits
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['MAX_FORM_MEMORY_SIZE'] = 100 * 1024 * 1024  # 100MB
```

### ✅ Fix 2: Better Error Handling
```python
try:
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
except Exception as parse_error:
    print(f"❌ Error parsing request: {parse_error}")
    return jsonify({'error': f'Failed to parse request: {str(parse_error)}'}), 400
```

### ✅ Fix 3: FormData Debugging
Added detailed logging of:
- Content-Type header
- Content-Length value
- All files in request
- All form fields
- File sizes

### ✅ Fix 4: Test Endpoint
Created `/api/test-upload` endpoint to diagnose issues

## How to Test

### Step 1: Start Your App
```bash
python app.py
```

### Step 2: Add an Image to Your Entry
1. Open dashboard
2. Click "Attach" button
3. Select an image (preferably small, < 5MB)
4. You should see image preview

### Step 3: Test Upload (Option A - Using Console Function)

**Open browser DevTools (F12)** and in the **Console** tab, run:
```javascript
testUploadDiagnostics()
```

This will:
- Create a test FormData
- Log exactly what's being sent
- Send to `/api/test-upload` endpoint
- Show detailed diagnostics

**Expected output in Console:**
```
🧪 Starting upload diagnostics...

  ✓ Adding file 0: image.jpg
📦 Total FormData size: 45234 bytes
📁 Files attached: 1

Sending to /api/test-upload...

✅ Test upload successful!
Response: {success: true, message: "Test upload received"}
```

### Step 4: Check Server Terminal
Look for output like:
```
============================================================
🧪 TEST UPLOAD ENDPOINT
============================================================
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 45234
Request Method: POST

Request Files: ['file_0']
Request Form: ['date_id', 'title', 'font', 'theme', 'blocks']

  File 'file_0':
    Filename: image.jpg
    Content-Type: image/jpeg
    Size: 12345 bytes

  Form 'blocks': {"id":1,"type":"image",...}

============================================================
```

## If Test Upload Works but Save Doesn't

Then the issue is in the actual save logic, not the FormData parsing. Check:

1. **Cloudinary Upload**
   - Verify credentials in `.env`
   - Check if Cloudinary service is accessible

2. **Firebase Save**
   - Verify Firestore rules allow write
   - Check user permissions

3. **Block Processing**
   - Look for errors in terminal when processing blocks

## If Test Upload Fails

### Error: "Failed to parse request"
- File might be too large
- Check file size (should be < 100MB with current config)
- Try with smaller file (< 5MB)

### Error: "timeout" or "connection refused"
- Flask server not running
- Check terminal for startup errors

### Browser console shows no response
- Check Network tab (F12 > Network)
- Look for failed request to `/api/test-upload`
- Check response status and error message

## FormData Best Practices

✅ **DO:**
- Don't set Content-Type header for FormData (browser handles it)
- Append files as Blob/File objects, not strings
- Append other data before files (optional but cleaner)
- Test with small files first

❌ **DON'T:**
- Don't manually set `Content-Type: application/json` with FormData
- Don't try to stringify File objects
- Don't send corrupted or incomplete files

## Troubleshooting Checklist

- [ ] File size is < 100MB
- [ ] Browser console shows "✓ Appending file" messages
- [ ] Network tab shows FormData in request
- [ ] Server logs show "Parsing as FormData"
- [ ] No circular references in contentBlocks
- [ ] Flask server has restarted after config changes
- [ ] No timeout or connection errors

## Quick Test Commands

**From Python terminal:**
```python
# Check upload size limits
from app import app
print(f"Max content length: {app.config['MAX_CONTENT_LENGTH']}")
print(f"Max form memory: {app.config['MAX_FORM_MEMORY_SIZE']}")
```

**From Browser Console:**
```javascript
// Check FormData contents
const formData = new FormData();
formData.append('test', 'value');
for (let [key, value] of formData) {
    console.log(`${key}:`, value);
}
```

---

## Next Steps

1. Try `testUploadDiagnostics()` first to isolate the issue
2. Compare test upload vs actual save to find the difference
3. Share terminal output if still having issues
