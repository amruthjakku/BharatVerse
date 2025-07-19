# 🛡️ Admin Management Guide - BharatVerse

This guide explains how to add and manage administrators in the BharatVerse platform.

## 🚀 Quick Start

### Method 1: Command Line Tool (Recommended)

The easiest way to manage admins is using the command line tool:

```bash
# List all users
python admin_tools.py list

# Make a user admin (they must login first)
python admin_tools.py make-admin <username>

# Remove admin privileges
python admin_tools.py remove-admin <username>

# List current admins
python admin_tools.py admins
```

**Example:**
```bash
# Make user 'john_doe' an admin
python admin_tools.py make-admin john_doe

# List all current admins
python admin_tools.py admins
```

### Method 2: Environment Variables (First Admin)

For the very first admin, you can set environment variables in `.env`:

```bash
# Add to .env file
INITIAL_ADMIN_USERNAME=your_gitlab_username
INITIAL_ADMIN_EMAIL=your@email.com
```

When a user with this username or email logs in for the first time, they'll automatically become an admin.

### Method 3: Admin Dashboard (For Existing Admins)

Once you have at least one admin, they can promote other users through the web interface:

1. Login as an admin
2. Go to Dashboard → **🛡️ Admin Management** tab
3. Enter the username of the user to promote
4. Click "🛡️ Make Admin"

## 📋 Prerequisites

### For Command Line Method:
- User must have logged in at least once via GitLab OAuth
- You need access to the server/terminal where BharatVerse is running

### For Environment Variable Method:
- Set variables before the user's first login
- Restart the application after setting variables

### For Dashboard Method:
- At least one existing admin must be logged in
- Target user must have logged in at least once

## 🔐 Security Features

- **Last Admin Protection**: Cannot remove the last admin from the system
- **Authentication Required**: All admin functions require proper authentication
- **Role-Based Access**: Only admins can access admin management features
- **Audit Trail**: All role changes are logged in the database

## 🛠️ Troubleshooting

### "User not found" Error
```bash
❌ User 'username' not found.
```
**Solution**: The user must login via GitLab OAuth at least once before they can be made an admin.

### "No administrators found" Warning
If you see this in the admin dashboard, it means there are no admins in the system. Use the command line tool or environment variables to create the first admin.

### Environment Variables Not Working
1. Check that variables are set in `.env` file
2. Restart the Streamlit application
3. Ensure the user hasn't logged in before (this only works on first login)

## 📊 Admin Capabilities

Once a user becomes an admin, they get access to:

- **🛡️ Admin Management**: Add/remove other admins
- **👥 User Management**: View and manage all users
- **📁 Content Management**: Moderate content and contributions
- **📈 Analytics**: View system statistics and reports
- **⚙️ System Settings**: Configure platform settings

## 🔄 Role Hierarchy

1. **Admin**: Full system access, can manage other admins
2. **Moderator**: Can moderate content, manage users (not implemented yet)
3. **User**: Regular user with contribution capabilities

## 📝 Examples

### Complete Admin Setup Workflow

1. **Start the application:**
   ```bash
   streamlit run Home.py --server.port 8501
   ```

2. **User logs in via GitLab OAuth** (creates user account)

3. **Make them admin via command line:**
   ```bash
   python admin_tools.py make-admin their_username
   ```

4. **Verify admin creation:**
   ```bash
   python admin_tools.py admins
   ```

5. **Admin can now access admin dashboard** and manage other users

### Setting Up Initial Admin

**Option A: Environment Variables**
```bash
# In .env file
INITIAL_ADMIN_USERNAME=admin_user
INITIAL_ADMIN_EMAIL=admin@company.com
```

**Option B: Command Line (after first login)**
```bash
python admin_tools.py make-admin admin_user
```

## 🚨 Important Notes

- **Backup First**: Always backup your database before making role changes
- **Test Environment**: Test admin functionality in a development environment first
- **Single Admin Risk**: Avoid having only one admin - always have at least 2
- **Regular Audits**: Regularly review admin list and remove unnecessary privileges

## 📞 Support

If you encounter issues with admin management:

1. Check the application logs for error messages
2. Verify database connectivity
3. Ensure GitLab OAuth is properly configured
4. Check that users have logged in at least once

For technical support, check the main README.md or contact the development team.