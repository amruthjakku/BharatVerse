# 🚀 Quick Supabase Setup (2 Minutes)

## Step 1: Execute SQL in Supabase Dashboard

1. **Go to your Supabase project**: https://supabase.com/dashboard/project/hzjbpthvkekfahwiujbz
2. **Click "SQL Editor"** in the left sidebar
3. **Copy the entire content** from `supabase_tables.sql` file
4. **Paste it into the SQL editor**
5. **Click "Run"** button

## Step 2: Verify Setup

```bash
python verify_supabase_setup.py
```

## Step 3: Test Your App

```bash
streamlit run BharatVerse.py
```

## ✅ What You Should See

After running the SQL script, you should see these tables in your Supabase dashboard:

- **users** (for user accounts)
- **contributions** (for text stories, proverbs, etc.)
- **analytics** (for tracking user activity)
- **community_interactions** (for likes, comments, etc.)

## 🎯 Expected Results

1. **Text submissions** → Stored directly in Supabase `contributions` table
2. **Browse page** → Shows contributions from Supabase
3. **Analytics** → Real-time data from cloud database
4. **User dashboard** → Personal contributions from Supabase

## 🔧 If Something Goes Wrong

1. **Check Supabase project is active**
2. **Verify database password is "BharatVerse"**
3. **Make sure SQL script executed without errors**
4. **Run the verification script to diagnose issues**

---

**That's it! Your Supabase database will be ready in 2 minutes.** 🎉