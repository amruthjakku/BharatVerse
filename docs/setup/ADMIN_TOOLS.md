# 🛡️ Admin Tools for BharatVerse

This document explains how to create and manage admin users in BharatVerse.

## 🚀 Quick Start - Make First Admin

### Method 1: Simple Script (Recommended)
```bash
# Interactive mode - shows all users and lets you select
python make_admin.py

# Direct mode - promote specific user
python make_admin.py username_here
```

### Method 2: Existing Setup Script
```bash
# Interactive admin setup
python scripts/setup_admin.py

# List all users
python scripts/setup_admin.py list
```

### Method 3: Advanced Admin Tools
```bash
# Make user admin
python scripts/admin_tools.py make-admin username_here

# List all users
python scripts/admin_tools.py list-users

# Remove admin privileges
python scripts/admin_tools.py remove-admin username_here
```

## 🌐 Web-Based Admin Management

Once you have at least one admin, you can manage users through the web interface:

1. **Login as admin** to your BharatVerse app
2. **Go to Admin Dashboard** (🛡️ button in sidebar)
3. **Select "👑 User Roles"** from the menu
4. **Promote/demote users** with the web interface

## 📋 Step-by-Step Process

### 1. First User Registration
1. Deploy your BharatVerse app
2. Have the first user login via GitLab OAuth
3. This creates the user in the database

### 2. Make First Admin
```bash
# Run the simple admin tool
python make_admin.py

# Select the user to promote
# Confirm the promotion
```

### 3. Admin Access
The promoted user can now:
- ✅ Access **Admin Dashboard** (`/Admin_Dashboard`)
- ✅ Access **Database Admin** (`/Database_Admin`)
- ✅ Access **Performance Monitor** (`/Performance`)
- ✅ Access **Community Admin** (`/Community_Admin`)
- ✅ Promote other users to admin via web interface

## 🛠️ Available Admin Tools

### Command Line Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `make_admin.py` | Simple admin promotion | `python make_admin.py [username]` |
| `scripts/setup_admin.py` | Interactive admin setup | `python scripts/setup_admin.py` |
| `scripts/admin_tools.py` | Advanced admin management | `python scripts/admin_tools.py make-admin user` |

### Web Interface Tools

| Feature | Location | Purpose |
|---------|----------|---------|
| User Role Management | Admin Dashboard → User Roles | Promote/demote users |
| User Database | Database Admin → User Overview | View all users |
| User Search | Database Admin → User Search | Find specific users |
| System Health | Admin Dashboard → System Health | Monitor system status |

## 🔒 Security Notes

### Admin Privileges
Admins can:
- ✅ View all user data
- ✅ Promote/demote other users
- ✅ Access system performance data
- ✅ Manage community features
- ✅ Export user data
- ✅ Monitor system health

### Best Practices
- 🛡️ **Keep admin count low** - Only promote trusted users
- 🔄 **Regular audits** - Review admin list periodically
- 📊 **Monitor activity** - Check admin actions in logs
- 🚫 **Don't demote last admin** - Always keep at least one admin

## 🆘 Troubleshooting

### "No users found"
- Ensure at least one user has logged in via GitLab OAuth
- Check database path: `data/users.db`

### "Database not found"
- Run the app first to create the database
- Have a user login to initialize tables

### "Permission denied"
- Make sure you're running from the project root directory
- Check file permissions: `chmod +x make_admin.py`

### "User not found"
- List all users first: `python make_admin.py` (interactive mode)
- Use exact username (case-sensitive)

## 📞 Support

If you need help with admin setup:

1. **Check logs** in the app for any errors
2. **Verify database** exists at `data/users.db`
3. **Test login** - ensure GitLab OAuth works
4. **Run interactive tool** - `python make_admin.py`

## 🎯 Quick Commands Reference

```bash
# List all users
python make_admin.py

# Make specific user admin
python make_admin.py their_username

# Check if database exists
ls -la data/users.db

# View database content (advanced)
sqlite3 data/users.db "SELECT username, role FROM users;"
```

---

**🛡️ Admin tools are ready to use!** Choose the method that works best for your setup.