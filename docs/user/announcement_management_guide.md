# #FahanieCares Latest Updates Management Guide

*Complete Administrator Guide for Managing Announcements and Updates*

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Accessing the Admin Panel](#accessing-the-admin-panel)
4. [Creating New Announcements](#creating-new-announcements)
5. [Managing Photos and Images](#managing-photos-and-images)
6. [Publishing Workflow](#publishing-workflow)
7. [Managing Existing Announcements](#managing-existing-announcements)
8. [Categories and Organization](#categories-and-organization)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Technical Reference](#technical-reference)

---

## Overview

The #FahanieCares Latest Updates system allows administrators to create, manage, and publish announcements that appear on the website's homepage and dedicated announcements page. This system supports rich content, photo uploads, categorization, and flexible publishing controls.

### Key Features

- ✅ **Rich Content Management**: Create announcements with titles, excerpts, and full content
- ✅ **Photo Upload Support**: Add images to announcements for visual appeal
- ✅ **Category Organization**: Organize updates by type (News, Events, Parliament, Programs, Updates)
- ✅ **Publishing Control**: Draft → Published → Archived workflow
- ✅ **Homepage Integration**: Feature important announcements on the homepage
- ✅ **SEO-Friendly URLs**: Automatic slug generation for better search engine visibility
- ✅ **Mobile Responsive**: All announcements display properly on all devices

### Where Announcements Appear

1. **Homepage "Latest Updates" Section**: Shows up to 3 featured announcements with images and excerpts
2. **Full Announcements Page** (`/announcements/`): Displays all published announcements in a grid layout
3. **Individual Announcement Pages** (`/announcements/<title>/`): Full article view with complete content

---

## Getting Started

### Prerequisites

Before you can manage announcements, ensure you have:

- [ ] **Admin Account**: You need an administrator or staff account
- [ ] **Login Credentials**: Username and password for the #FahanieCares system
- [ ] **Internet Connection**: Access to the website admin panel
- [ ] **Modern Web Browser**: Chrome, Firefox, Safari, or Edge (recommended)

### Required Permissions

You need one of the following permission levels:
- **Superuser**: Full system access
- **Staff Member**: Can create and manage announcements
- **Content Manager**: Specific announcement management permissions

---

## Accessing the Admin Panel

### Step 1: Navigate to the Admin Panel

1. **Open your web browser**
2. **Go to the admin URL**:
   - **Development**: `http://localhost:3000/admin/`
   - **Production**: `https://fahaniecares.ph/admin/`
3. **Bookmark this page** for easy future access

### Step 2: Login

1. **Enter your username** in the "Username" field
2. **Enter your password** in the "Password" field
3. **Click "Log in"**

*If you don't have login credentials, contact the system administrator.*

### Step 3: Locate Announcements

1. **Look for the "CORE" section** on the admin homepage
2. **Find "Announcements"** under the CORE section
3. **Click on "Announcements"** to access the management interface

---

## Creating New Announcements

### Quick Start: Adding Your First Announcement

1. **Click "Add Announcement"** (green button in top-right)
2. **Fill in the required fields**:
   - **Title**: Enter your announcement title
   - **Excerpt**: Write a brief summary (max 300 characters)
   - **Content**: Write the full announcement content
3. **Upload an image** (optional but recommended)
4. **Set the category** (News, Event, Parliament, Program, Update)
5. **Set status to "Published"**
6. **Check "Is featured"** if you want it on the homepage
7. **Set the published date**
8. **Click "Save"**

### Detailed Step-by-Step Guide

#### Step 1: Start Creating

1. **In the Announcements list**, click the **"Add Announcement"** button
2. **You'll see a form** with several sections: Content, Publishing, and Metadata

#### Step 2: Content Section

**Title** (Required)
- Enter a clear, descriptive title for your announcement
- Keep it under 200 characters
- The system will automatically create a URL-friendly version

**Slug** (Auto-generated)
- This is the URL-friendly version of your title
- Usually auto-filled, but you can customize it
- Use lowercase letters, numbers, and hyphens only
- Example: "new-community-program" for title "New Community Program"

**Excerpt** (Required)
- Write a brief summary of your announcement
- Maximum 300 characters
- This appears on the homepage and listing pages
- Make it engaging to encourage readers to click "Read More"

**Content** (Required)
- Write the full content of your announcement
- You can use basic formatting
- Include all important details here
- This appears on the individual announcement page

**Image** (Optional)
- Click "Choose File" to upload a photo
- Recommended size: 1200x600 pixels or larger
- Supported formats: JPG, PNG, GIF
- File size: Keep under 5MB for best performance

#### Step 3: Publishing Section

**Category** (Required)
- **News**: General news and updates
- **Event**: Upcoming or past events
- **Parliament**: Parliamentary activities and legislation
- **Program**: #FahanieCares program announcements
- **Update**: Status updates and progress reports

**Status** (Required)
- **Draft**: Not visible to the public (for preparing content)
- **Published**: Visible to everyone on the website
- **Archived**: No longer featured but still accessible

**Is Featured** (Optional)
- Check this box to display the announcement on the homepage
- Only 3 featured announcements show on the homepage
- Use for the most important updates

**Published Date** (Optional)
- Set when the announcement should be considered "published"
- Leave blank to use the current date/time
- Use for scheduling announcements or backdating

#### Step 4: Save Your Work

1. **Click "Save and add another"** to create more announcements
2. **Click "Save and continue editing"** to save and keep editing
3. **Click "Save"** to save and return to the list

---

## Managing Photos and Images

### Image Upload Process

#### Step 1: Prepare Your Images

**Recommended Specifications:**
- **Dimensions**: 1200x600 pixels (2:1 ratio) for best appearance
- **File Format**: JPG (best for photos), PNG (best for graphics with text)
- **File Size**: Under 5MB (under 2MB recommended for faster loading)
- **Quality**: High quality but web-optimized

**Image Editing Tips:**
- Use photo editing software to resize images before upload
- Ensure images are clear and professional-looking
- Consider adding the #FahanieCares logo if appropriate
- Crop images to focus on the most important elements

#### Step 2: Upload Images

1. **In the announcement form**, scroll to the "Image" field
2. **Click "Choose File"** or "Browse"
3. **Navigate to your image file** and select it
4. **Click "Open"** to upload
5. **The filename will appear** next to the button when successful

#### Step 3: Image Management

**After Upload:**
- The image is automatically saved to the server
- It will appear on the homepage (if featured) and announcement page
- Images are automatically resized for mobile devices

**Changing Images:**
- To replace an image, simply upload a new one
- The old image will be automatically replaced
- No need to delete the old image manually

**Removing Images:**
- Check the "Clear" checkbox next to the image field
- Save the announcement to remove the image

### Image Best Practices

**Content Guidelines:**
- Use high-quality, relevant images that support your announcement
- Ensure you have permission to use the image
- Avoid images with too much text (may not be readable on mobile)
- Use images that represent the #FahanieCares brand positively

**Technical Guidelines:**
- Always test how images look on mobile devices
- Use consistent image styles across announcements
- Keep file sizes reasonable for fast loading
- Consider accessibility - add descriptive alt text when possible

---

## Publishing Workflow

### Understanding Status States

#### Draft Status
- **Purpose**: For preparing content that's not ready for publication
- **Visibility**: Not visible to the public
- **Use Case**: Work in progress, content under review
- **Best Practice**: Always start new announcements as drafts

#### Published Status
- **Purpose**: Makes content visible to the public
- **Visibility**: Appears on the website immediately
- **Use Case**: Ready-to-share announcements
- **Best Practice**: Double-check content before publishing

#### Archived Status
- **Purpose**: For old content that should no longer be featured
- **Visibility**: Accessible via direct links but not listed prominently
- **Use Case**: Outdated announcements that need to remain accessible
- **Best Practice**: Archive announcements after events or when superseded

### Publishing Checklist

Before publishing any announcement, verify:

- [ ] **Title is clear and accurate**
- [ ] **Excerpt is engaging and under 300 characters**
- [ ] **Content is complete and error-free**
- [ ] **Image is uploaded and appropriate** (if applicable)
- [ ] **Category is correctly selected**
- [ ] **Published date is set correctly**
- [ ] **Featured status is appropriate**
- [ ] **Content follows #FahanieCares brand guidelines**

### Publishing Process

#### Method 1: Immediate Publishing
1. **Create your announcement**
2. **Set status to "Published"**
3. **Set published date to now** (or leave blank)
4. **Click "Save"**
5. **Announcement appears immediately**

#### Method 2: Scheduled Publishing
1. **Create your announcement**
2. **Set status to "Draft"**
3. **Set published date to future date**
4. **Save as draft**
5. **Change status to "Published" when ready**

### Editorial Review Process

**For Important Announcements:**
1. **Create as Draft**
2. **Share the draft URL with reviewers**
3. **Make necessary revisions**
4. **Get final approval**
5. **Change status to Published**
6. **Announce on social media** (if applicable)

---

## Managing Existing Announcements

### Viewing All Announcements

1. **Go to Admin Panel** → **Core** → **Announcements**
2. **You'll see a list** of all announcements with:
   - Title
   - Category (with colored badge)
   - Status (with colored badge)
   - Featured status (checkmark)
   - Published date
   - Author

### List View Features

**Filtering Options:**
- **By Category**: Filter by News, Event, Parliament, Program, Update
- **By Status**: Show only Draft, Published, or Archived announcements
- **By Featured Status**: Show only featured announcements
- **By Date**: Filter by creation date or published date

**Search Functionality:**
- Use the search box to find announcements by title, excerpt, or content
- Search is case-insensitive and matches partial words

**Quick Actions:**
- **Toggle Featured Status**: Click the checkbox in the "Is featured" column
- **Bulk Actions**: Select multiple announcements and perform actions

### Editing Existing Announcements

#### Step 1: Find the Announcement
1. **Use filters or search** to locate the announcement
2. **Click on the title** to open the edit form

#### Step 2: Make Changes
1. **Edit any field** as needed
2. **Upload new images** if required
3. **Change status** if needed
4. **Update published date** if necessary

#### Step 3: Save Changes
1. **Click "Save"** to apply changes
2. **Changes take effect immediately** for published announcements

### Deleting Announcements

**⚠️ Warning**: Deletion is permanent and cannot be undone.

#### Safe Deletion Process
1. **Consider archiving instead** of deleting
2. **If deletion is necessary**:
   - Select the announcement(s) in the list
   - Choose "Delete selected announcements" from Actions
   - Confirm deletion

#### Alternative: Archiving
1. **Open the announcement** for editing
2. **Change status to "Archived"**
3. **Save the changes**
4. **Announcement remains accessible** but not prominently featured

---

## Categories and Organization

### Available Categories

#### News
- **Purpose**: General news and organizational updates
- **Examples**: Staff changes, office moves, general updates
- **Badge Color**: Blue
- **Homepage Display**: Shows with info badge

#### Event
- **Purpose**: Announcements about events, activities, and gatherings
- **Examples**: Community meetings, celebrations, workshops
- **Badge Color**: Orange
- **Homepage Display**: Shows with warning badge

#### Parliament
- **Purpose**: Parliamentary activities, legislation, and official government business
- **Examples**: Bill updates, parliamentary sessions, policy announcements
- **Badge Color**: Green
- **Homepage Display**: Shows with success badge

#### Program
- **Purpose**: #FahanieCares program announcements and updates
- **Examples**: New programs, program results, beneficiary updates
- **Badge Color**: Primary Green
- **Homepage Display**: Shows with primary badge

#### Update
- **Purpose**: Status updates and progress reports
- **Examples**: Project progress, implementation updates, milestone achievements
- **Badge Color**: Gray
- **Homepage Display**: Shows with secondary badge

### Category Best Practices

**Choosing the Right Category:**
- **Be consistent** in category usage
- **Consider your audience** when categorizing
- **Use "Program"** for content directly related to #FahanieCares initiatives
- **Use "Parliament"** for official government-related content
- **Use "Event"** for time-sensitive announcements
- **Use "News"** for general updates
- **Use "Update"** for progress reports

**Category Strategy:**
- **Maintain balance** across categories
- **Don't overuse any single category**
- **Review categories monthly** to ensure proper distribution
- **Train team members** on category guidelines

---

## Best Practices

### Content Guidelines

#### Writing Effective Titles
- **Keep titles clear and descriptive**
- **Use action words when appropriate**
- **Include key information** (what, when, where)
- **Avoid jargon or technical terms**
- **Maximum 200 characters**

**Examples of Good Titles:**
- "New Healthcare Assistance Program Launches March 2025"
- "Community Meeting: Budget Discussion February 15"
- "Parliamentary Session Results: Education Bill Passed"

#### Writing Compelling Excerpts
- **Summarize the key point** in the first sentence
- **Answer "why should I care?"**
- **Include a call to action** when appropriate
- **Use active voice**
- **Keep under 300 characters**

**Examples of Good Excerpts:**
- "A new program providing free healthcare assistance to 500 families will begin accepting applications next month. Learn how to apply and check eligibility requirements."

#### Writing Complete Content
- **Start with the most important information**
- **Use clear, simple language**
- **Include all relevant details** (dates, locations, contact information)
- **Break up long paragraphs**
- **End with next steps** or contact information

### Image Guidelines

#### Technical Standards
- **Minimum Size**: 800x400 pixels
- **Recommended Size**: 1200x600 pixels
- **Aspect Ratio**: 2:1 (twice as wide as tall)
- **File Format**: JPG for photos, PNG for graphics
- **File Size**: Under 2MB for best performance

#### Content Standards
- **High Quality**: Sharp, well-lit, professional appearance
- **Relevant**: Directly related to the announcement content
- **Brand Consistent**: Aligns with #FahanieCares visual identity
- **Accessible**: Avoid images with essential text
- **Rights Cleared**: Ensure you have permission to use the image

### SEO and Accessibility

#### Search Engine Optimization
- **Use descriptive titles** with relevant keywords
- **Write complete excerpts** that summarize content
- **Include location names** when relevant
- **Use consistent categorization**
- **Set appropriate published dates**

#### Accessibility Considerations
- **Use clear, simple language**
- **Structure content with headings** when appropriate
- **Provide context for images**
- **Ensure good contrast** in uploaded images
- **Test on mobile devices**

### Publication Timing

#### Best Times to Publish
- **Weekday Mornings**: 8-10 AM for maximum visibility
- **Tuesday-Thursday**: Generally highest engagement
- **Avoid Late Fridays**: Lower weekend traffic
- **Consider Time Zones**: Target your primary audience

#### Frequency Guidelines
- **Regular Updates**: Aim for 2-4 announcements per month
- **Event-Driven**: Publish as needed for timely information
- **Seasonal Content**: Plan around holidays and important dates
- **Avoid Overwhelming**: Don't publish too many announcements at once

---

## Troubleshooting

### Common Issues and Solutions

#### Login Problems

**Issue**: Can't access the admin panel
**Solutions:**
1. **Check URL**: Ensure you're using the correct admin URL
2. **Verify Credentials**: Double-check username and password
3. **Clear Browser Cache**: Try a different browser or incognito mode
4. **Contact Administrator**: Request password reset if needed

**Issue**: Don't see "Announcements" option
**Solutions:**
1. **Check Permissions**: Ensure your account has staff privileges
2. **Contact Administrator**: Request appropriate permissions
3. **Refresh Page**: Sometimes a page refresh resolves display issues

#### Image Upload Problems

**Issue**: Image won't upload
**Solutions:**
1. **Check File Size**: Ensure image is under 5MB
2. **Check File Format**: Use JPG, PNG, or GIF only
3. **Try Different Browser**: Some browsers handle uploads differently
4. **Rename File**: Remove special characters from filename

**Issue**: Image appears distorted
**Solutions:**
1. **Check Dimensions**: Use recommended 2:1 aspect ratio
2. **Resize Before Upload**: Use image editing software
3. **Try Different Format**: Convert PNG to JPG or vice versa

#### Publishing Problems

**Issue**: Announcement doesn't appear on website
**Solutions:**
1. **Check Status**: Ensure status is set to "Published"
2. **Check Published Date**: Make sure date is not in the future
3. **Clear Browser Cache**: Refresh the public website
4. **Wait a Few Minutes**: Changes may take time to appear

**Issue**: Announcement appears in wrong location
**Solutions:**
1. **Check Category**: Verify correct category is selected
2. **Check Featured Status**: Ensure "Is featured" is set correctly
3. **Review Date**: Check published date for proper ordering

#### Content Formatting Issues

**Issue**: Text appears incorrectly formatted
**Solutions:**
1. **Use Plain Text**: Copy from plain text editor to avoid formatting conflicts
2. **Check for Special Characters**: Remove unusual characters
3. **Save and Refresh**: Sometimes saving and reopening fixes formatting

**Issue**: Links don't work
**Solutions:**
1. **Include Full URLs**: Use complete web addresses (https://...)
2. **Test Links**: Click links in preview mode
3. **Check Formatting**: Ensure no extra spaces or characters

### Getting Help

#### Self-Help Resources
1. **This Documentation**: Comprehensive guide for common tasks
2. **Admin Panel Help**: Look for help text next to form fields
3. **Website Testing**: Always preview your announcements on the public site

#### Contacting Support
**For Technical Issues:**
- Email: dev@fahaniecares.ph
- Include: Description of issue, steps you tried, browser information

**For Content Questions:**
- Contact: Communications Team
- Include: Draft content for review, questions about guidelines

**For Permission Issues:**
- Contact: System Administrator
- Include: Your username, specific permissions needed

---

## Technical Reference

### System Architecture

**Frontend Display:**
- **Homepage Integration**: Automatically displays 3 most recent featured announcements
- **Dedicated Page**: `/announcements/` shows all published announcements
- **Individual Pages**: `/announcements/<slug>/` for full content

**Backend Management:**
- **Django Admin**: Web-based interface for content management
- **Database Storage**: PostgreSQL database with Django ORM
- **File Storage**: Images stored in `/media/announcements/` directory

**URL Structure:**
- **Admin Panel**: `/admin/core/announcement/`
- **Public Listing**: `/announcements/`
- **Individual Posts**: `/announcements/<slug>/`

### Database Schema

**Announcement Model Fields:**
- `title`: CharField(max_length=200)
- `slug`: SlugField(max_length=200, unique=True)
- `excerpt`: TextField(max_length=300)
- `content`: TextField
- `category`: CharField with choices
- `status`: CharField with choices (draft/published/archived)
- `image`: ImageField(upload_to='announcements/')
- `is_featured`: BooleanField
- `created_by`: ForeignKey to User
- `published_date`: DateTimeField
- `created_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)

### File Management

**Image Storage:**
- **Location**: `/media/announcements/`
- **URL Pattern**: `/media/announcements/<filename>`
- **Automatic Processing**: Images are automatically served with proper headers

**Backup Considerations:**
- **Database**: Regular backups include all announcement data
- **Media Files**: Image files should be included in backup strategy
- **Recovery**: Both database and media files needed for complete restoration

### Integration Points

**Homepage Integration:**
- Template: `templates/core/home.html`
- Context Variable: `announcements`
- Query: Featured announcements, ordered by published date

**Navigation Integration:**
- Main menu links to `/announcements/`
- Breadcrumb navigation on individual pages
- Social sharing integration available

**SEO Integration:**
- Automatic meta tags generation
- OpenGraph tags for social sharing
- Sitemap inclusion for search engines

---

## Conclusion

This documentation provides comprehensive guidance for managing the #FahanieCares Latest Updates system. By following these guidelines, you can effectively create, manage, and publish announcements that keep your community informed and engaged.

### Quick Reference Summary

**To Add a New Announcement:**
1. Go to Admin Panel → Core → Announcements
2. Click "Add Announcement"
3. Fill in title, excerpt, content
4. Upload image (optional)
5. Set category and status
6. Check "Featured" for homepage display
7. Save

**To Edit an Existing Announcement:**
1. Find announcement in the list
2. Click on the title
3. Make changes
4. Save

**To Feature on Homepage:**
1. Edit announcement
2. Check "Is featured" box
3. Set status to "Published"
4. Save

**For Support:**
- Technical: dev@fahaniecares.ph
- Content: Communications Team
- Permissions: System Administrator

---

*Last Updated: January 2025*  
*#FahanieCares Development Team*