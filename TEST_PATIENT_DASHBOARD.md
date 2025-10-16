# Testing Patient Dashboard Navigation

## Issue
The sidebar navigation links are not showing/hiding the different sections.

## What Was Fixed

### 1. Added Console Logging
Added detailed console logging to help debug:
- Dashboard initialization
- Event listener setup
- Section switching
- Data loading

### 2. Improved Error Handling
- Better authentication checks
- Patient ID fallback (id or _id)
- Try-catch blocks for data loading

### 3. Enhanced showSection Method
- Added logging to track section switching
- Better error messages if section not found
- Proper class management

## How to Test

### Step 1: Open Browser Console
1. Open patient dashboard
2. Press F12 to open Developer Tools
3. Go to Console tab

### Step 2: Check for Errors
Look for these console messages:
```
Patient dashboard initializing...
Patient ID: [your_id]
Event listeners set up
Dashboard data loaded
```

### Step 3: Test Navigation
Click each sidebar link and check console:
```
Showing section: records
Found sections: 5
Target section: [HTMLElement]
Section activated: records
```

### Step 4: Verify Sections Appear
- Click "My Records" - should show records section
- Click "Upload Document" - should show upload form
- Click "Access Control" - should show access control
- Click "Profile" - should show profile form

## Common Issues & Solutions

### Issue: "Section not found" in console
**Solution:** Check that section IDs match:
- HTML: `<section id="records">`
- Link: `<a data-section="records">`

### Issue: Navigation clicks don't work
**Solution:** 
1. Check browser console for JavaScript errors
2. Verify config.js is loaded before patient-dashboard.js
3. Hard refresh browser (Ctrl+Shift+R)

### Issue: Sections don't hide/show
**Solution:**
1. Check dashboard.css is loaded
2. Verify `.content-section` and `.active` classes exist
3. Inspect element to see if classes are being toggled

### Issue: "authManager is not defined"
**Solution:**
1. Ensure auth.js is loaded before patient-dashboard.js
2. Check script order in HTML
3. Verify you're logged in

## Debug Commands

Run these in browser console:

### Check if dashboard initialized
```javascript
window.patientDashboard
```

### Manually switch sections
```javascript
window.patientDashboard.showSection('records')
window.patientDashboard.showSection('upload')
window.patientDashboard.showSection('access')
window.patientDashboard.showSection('profile')
```

### Check all sections
```javascript
document.querySelectorAll('.content-section').forEach(s => {
  console.log(s.id, s.classList.contains('active'));
});
```

### Check navigation links
```javascript
document.querySelectorAll('.nav-link').forEach(link => {
  console.log(link.getAttribute('data-section'), link.classList.contains('active'));
});
```

## Expected Behavior

1. **On Page Load:**
   - Dashboard section visible
   - Other sections hidden
   - Dashboard link highlighted in sidebar

2. **On Click "My Records":**
   - Dashboard section hides
   - Records section shows
   - My Records link highlighted

3. **On Click "Upload Document":**
   - Previous section hides
   - Upload section shows
   - Upload link highlighted

4. **On Click "Access Control":**
   - Previous section hides
   - Access section shows
   - Access link highlighted

5. **On Click "Profile":**
   - Previous section hides
   - Profile section shows
   - Profile link highlighted

## Files to Check

1. **frontend/pages/patient-dashboard.html**
   - Verify section IDs: dashboard, records, upload, access, profile
   - Verify data-section attributes match IDs

2. **frontend/js/patient-dashboard.js**
   - Check initialization
   - Check event listeners
   - Check showSection method

3. **frontend/assets/css/dashboard.css**
   - Verify `.content-section { display: none; }`
   - Verify `.content-section.active { display: block; }`

4. **Script Load Order:**
   ```html
   <script src="../js/config.js"></script>
   <script src="../js/encryption.js"></script>
   <script src="../js/auth.js"></script>
   <script src="../js/api.js"></script>
   <script src="../js/ui.js"></script>
   <script src="../js/patient-dashboard.js"></script>
   ```

## Next Steps

1. **Hard refresh browser** (Ctrl+Shift+R)
2. **Open console** and check for errors
3. **Click navigation links** and watch console
4. **Report any errors** you see in console
