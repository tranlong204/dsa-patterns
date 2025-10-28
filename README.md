# DSA Patterns Practice Tracker

A comprehensive tool for tracking your LeetCode problem-solving progress with organized patterns, search, filtering, and backend API integration.

## Features

- ✅ **Progress Tracking**: Check off problems as you solve them
- 🔍 **Search & Filter**: Search problems by title, filter by Solved/Unsolved status
- 🎯 **Difficulty Tracking**: Separate tracking for Easy (413), Medium (652), and Hard (367) problems
- 📊 **Visual Calendar**: Activity heatmap with intensity levels based on problems solved per day
- 🔗 **Direct Links**: Click on any problem to open it on LeetCode
- 💾 **Hybrid Storage**: Supabase backend with localStorage fallback
- 🚀 **FastAPI Backend**: RESTful API for CRUD operations
- 🗄️ **Supabase Integration**: Persistent database storage

## Quick Start

### Frontend Only (Local Storage)
1. Open `index.html` in your web browser
2. Your progress is automatically saved locally

### With Backend API (Supabase)
1. Set up Supabase and run migrations (see `backend/README.md`)
2. Configure environment variables in `backend/.env`
3. Start the backend: `cd backend && uvicorn app.main:app --reload`
4. Open `index.html` - it will automatically connect to the API
5. Your progress is saved to Supabase database

## Topics Covered

- Arrays & Hashing
- Two Pointers
- Sliding Window
- Stack
- Binary Search
- Linked Lists
- Trees
- Tries
- Heap/Priority Queue
- Intervals
- Greedy
- Backtracking
- Graphs
- Dynamic Programming

## Technologies Used

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: FastAPI, Python 3
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase with localStorage fallback

## Browser Compatibility

Works on all modern browsers (Chrome, Firefox, Safari, Edge).

## Customization

You can customize the problems list by editing `data.js`. Each problem follows this structure:

```javascript
{
    id: 1,
    number: 1,
    title: "Two Sum",
    difficulty: "Easy",
    topics: ["Arrays"],
    link: "https://leetcode.com/problems/two-sum/"
}
```

