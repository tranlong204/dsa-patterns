# LeetCode Patterns Tracker

A beautiful, interactive website to track your LeetCode problem-solving progress with organized patterns, search, and filtering capabilities.

## Features

- ✅ **Progress Tracking**: Check off problems as you solve them
- 🔍 **Search**: Find problems by title or number
- 🏷️ **Filtering**: Filter by difficulty (Easy/Medium/Hard) and topic
- 💾 **Persistent Storage**: Your progress is saved locally using browser storage
- 📊 **Progress Bar**: Visual indicator of your completion percentage
- 🎨 **Beautiful UI**: Modern, responsive design with gradient colors
- 🔗 **Direct Links**: Click on any problem to open it on LeetCode

## Usage

1. Open `index.html` in your web browser
2. Browse the problems organized by topics
3. Check the boxes for problems you've solved
4. Use the search bar to find specific problems
5. Use the filters to narrow down by difficulty or topic
6. Your progress is automatically saved locally

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

- HTML5
- CSS3 (with gradients and modern styling)
- Vanilla JavaScript
- Local Storage API for persistence

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

