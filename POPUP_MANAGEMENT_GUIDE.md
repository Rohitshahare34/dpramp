# Website Popup/Poster Management Guide

## 🎯 Feature Overview

You can now **control the website popup** directly from the Django Admin Panel! 

### What You Can Do:

1. **Disable the popup** completely
2. **Upload an image poster/banner** to show instead of the old hardcoded popup
3. **Customize popup settings** (delay, session control, action links)

---

## 📋 How to Use (Step-by-Step)

### Step 1: Access Admin Panel
1. Go to: `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials
3. Find **"Website Popups/Posters"** section

### Step 2: Add New Popup/Poster
1. Click **"+ Add"** next to "Website Popups/Posters"
2. Fill in the details:

#### **Option A: Image Poster/Banner** (Recommended - Simple & Professional)
- **Title**: Give it a name (e.g., "Summer Sale Poster")
- **Popup Type**: Select **"Image Banner/Poster"**
- **Is Active**: ✅ Check this to enable it on the website
- **Poster Image**: Upload your image (JPG, PNG)
- **Action Link** (Optional): Add a URL where users go when they click the button
  - Example: `http://127.0.0.1:8000/pdf-notes/`
- **Action Text** (Optional): Button text (e.g., "Shop Now", "Learn More")
- **Display Delay**: How long to wait before showing popup (in milliseconds)
  - 2000 = 2 seconds (default)
  - 3000 = 3 seconds
- **Show Once Per Session**: ✅ Check to show only once per browser visit

#### **Option B: Modal Popup** (With Custom HTML Content)
- **Title**: Popup title
- **Popup Type**: Select **"Modal Popup"**
- **Is Active**: ✅ Check to enable
- **Modal Content**: Write HTML content for the popup
- **Action Link & Text**: Same as above
- **Display Settings**: Same as above

### Step 3: Save & View
1. Click **"Save"**
2. Visit your homepage: `http://127.0.0.1:8000/`
3. The popup will appear after the delay you set!

---

## 🎨 Design Features

### Image Poster Mode:
- ✅ Clean, professional look
- ✅ Matches your website theme (green-blue gradient header)
- ✅ Full-width image display
- ✅ Optional action button at bottom
- ✅ Mobile responsive

### Modal Popup Mode:
- ✅ Custom HTML content
- ✅ Green-blue gradient header
- ✅ Fully responsive
- ✅ Supports all HTML elements

---

## 💡 Pro Tips

### For Best Results:
1. **Image Size**: Use images around **800x1000 pixels** (portrait) or **1200x800 pixels** (landscape)
2. **File Format**: JPG or PNG
3. **File Size**: Keep under 500KB for faster loading
4. **One Active Popup**: Only the **first active popup** will show on the website
5. **Disable Old Popup**: To remove popup, either:
   - Uncheck "Is Active" 
   - OR delete the popup entry

### Common Use Cases:
- 🎓 **Course Announcements** - Upload poster for new courses
- 💰 **Sale/Promotions** - Show discount offers
- 📢 **Event Posters** - Workshop or event announcements
- 🎯 **Product Launches** - New drone or study material launches

---

## 🔧 Admin Panel Fields Explained

| Field | Description | Example |
|-------|-------------|---------|
| **Title** | Admin reference name | "Diwali Sale 2024" |
| **Popup Type** | Choose: Modal or Banner | "Image Banner/Poster" |
| **Is Active** | Enable/disable on website | ✅ Checked = Show |
| **Poster Image** | Upload image file | `poster.jpg` |
| **Modal Content** | HTML for modal popup | `<h1>Hello</h1>` |
| **Action Link** | Button destination URL | `http://127.0.0.1:8000/pdf-notes/` |
| **Action Text** | Button label | "Shop Now" |
| **Display Delay** | Wait time (milliseconds) | 2000 = 2 seconds |
| **Show Once Per Session** | Show only once per visit | ✅ Checked |

---

## 🚀 Quick Start Example

### Want to show an image poster?

1. **Create Design** in Canva/Photoshop (e.g., 800x1000px)
2. **Go to Admin Panel** → Add Website Popup
3. **Fill in**:
   - Title: "New Drone Launch"
   - Popup Type: "Image Banner/Poster"
   - Is Active: ✅ Yes
   - Poster Image: Upload your design
   - Action Link: `http://127.0.0.1:8000/drones/`
   - Action Text: "View Drones"
   - Display Delay: 2000
   - Show Once Per Session: ✅ Yes
4. **Save** → Done! 🎉

---

## 📱 How It Works on Website

### When Active:
- ✅ Popup appears after delay (e.g., 2 seconds)
- ✅ Shows once per browser session (if enabled)
- ✅ User can close with X button
- ✅ Mobile responsive design
- ✅ Matches your website's green-blue theme

### When Disabled:
- ❌ No popup shows
- ❌ Clean homepage experience
- ❌ No performance impact

---

## 🎨 Design Matches Your Website

The popup uses your website's color scheme:
- **Primary Color**: `#00A86B` (Emerald Green)
- **Secondary Color**: `#00B4D8` (Sky Blue)
- **Gradient**: Green → Blue
- **Border Radius**: 15px (rounded corners)
- **Shadows**: Professional shadow effects

---

## 🐛 Troubleshooting

### Popup not showing?
1. Check if **"Is Active"** is enabled
2. Make sure **Popup Type** is selected
3. For image poster: Verify **Poster Image** is uploaded
4. Clear browser cache and refresh

### Image not displaying?
1. Check if image file is uploaded correctly
2. Verify file format (JPG/PNG)
3. Check media folder permissions

### Want to change popup?
1. Edit existing popup in admin
2. OR create new one and disable old one
3. Only **first active popup** will show

---

## 📞 Need Help?

If you face any issues:
1. Check Django admin for errors
2. Verify popup is active
3. Check browser console for JavaScript errors
4. Restart Django server if needed

---

**Enjoy your new dynamic popup system! 🎉**
