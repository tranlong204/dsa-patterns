// Load saved progress from localStorage
let solvedProblems = JSON.parse(localStorage.getItem('solvedProblems')) || [];
let activityDates = JSON.parse(localStorage.getItem('activityDates')) || {};
let revisionProblems = JSON.parse(localStorage.getItem('revisionProblems')) || [];
let isRevisionFilterActive = false;
let currentFilter = null; // 'solved', 'unsolved', or null (show all)

// Flag to use API instead of localStorage
const USE_API = true; // Set to false to use localStorage fallback

// Track activity when a problem is solved
async function trackActivity(problemId, date = new Date()) {
    const dateKey = formatDate(date);
    if (!activityDates[dateKey]) {
        activityDates[dateKey] = [];
    }
    if (!activityDates[dateKey].includes(problemId)) {
        activityDates[dateKey].push(problemId);
        localStorage.setItem('activityDates', JSON.stringify(activityDates));
        
        // Also save to API
        if (USE_API) {
            try {
                await api.markProblemSolved(problemId);
                // Refresh calendar from API after update
                await renderCalendar();
                await updateActivityGrid();
            } catch (error) {
                console.error('Failed to save to API:', error);
                // Fallback to local updates
                renderCalendar();
                updateActivityGrid();
            }
        } else {
            renderCalendar();
            updateActivityGrid();
        }
    }
}

// Remove activity when a problem is unchecked
async function removeActivity(problemId) {
    // Find and remove this problem from all dates
    for (const dateKey in activityDates) {
        if (activityDates[dateKey].includes(problemId)) {
            activityDates[dateKey] = activityDates[dateKey].filter(id => id !== problemId);
            // Remove the date entry if it's now empty
            if (activityDates[dateKey].length === 0) {
                delete activityDates[dateKey];
            }
        }
    }
    localStorage.setItem('activityDates', JSON.stringify(activityDates));
    
    // Also update API
    if (USE_API) {
        try {
            await api.markProblemUnsolved(problemId);
            // Refresh calendar from API after update
            await renderCalendar();
            await updateActivityGrid();
        } catch (error) {
            console.error('Failed to update API:', error);
            // Fallback to local updates
            renderCalendar();
            updateActivityGrid();
        }
    } else {
        renderCalendar();
        updateActivityGrid();
    }
}

// Clean up activity tracking to only include problems that are actually solved
function cleanupActivityTracking() {
    let hasChanges = false;
    
    // Create a Set of solved problem IDs for faster lookup
    const solvedSet = new Set(solvedProblems);
    
    // Go through all activity dates and remove problems that aren't solved
    for (const dateKey in activityDates) {
        const originalLength = activityDates[dateKey].length;
        activityDates[dateKey] = activityDates[dateKey].filter(id => solvedSet.has(id));
        
        // If no problems left for this date, remove the date
        if (activityDates[dateKey].length === 0) {
            delete activityDates[dateKey];
            hasChanges = true;
        } else if (activityDates[dateKey].length !== originalLength) {
            hasChanges = true;
        }
    }
    
    // If we made changes, save and re-render
    if (hasChanges) {
        localStorage.setItem('activityDates', JSON.stringify(activityDates));
        renderCalendar();
    }
}

// Format date as YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Group problems by topic
function groupProblemsByTopic(problems) {
    const grouped = {};
    problems.forEach(problem => {
        const topics = problem.topics || ['General'];
        topics.forEach(topic => {
            if (!grouped[topic]) {
                grouped[topic] = [];
            }
            grouped[topic].push(problem);
        });
    });
    return grouped;
}

// Count problems by difficulty
function countByDifficulty(problems) {
    return {
        easy: problems.filter(p => p.difficulty === 'Easy').length,
        medium: problems.filter(p => p.difficulty === 'Medium').length,
        hard: problems.filter(p => p.difficulty === 'Hard').length,
        solved: problems.filter(p => solvedProblems.includes(p.id)).length
    };
}

// Update sidebar statistics
async function updateSidebarStats() {
    if (USE_API) {
        try {
            const stats = await api.getStats();
            
            // Update total progress
            const percentage = stats.total_problems > 0 ? Math.round((stats.solved_problems / stats.total_problems) * 100) : 0;
            document.getElementById('totalProgress').textContent = percentage + '%';
            
            // Update difficulty progress
            document.getElementById('easyCount').textContent = `${stats.easy_solved}/${stats.easy_total}`;
            document.getElementById('mediumCount').textContent = `${stats.medium_solved}/${stats.medium_total}`;
            document.getElementById('hardCount').textContent = `${stats.hard_solved}/${stats.hard_total}`;
            
            // Update progress bars
            const easyPercentage = stats.easy_total > 0 ? (stats.easy_solved / stats.easy_total) * 100 : 0;
            const mediumPercentage = stats.medium_total > 0 ? (stats.medium_solved / stats.medium_total) * 100 : 0;
            const hardPercentage = stats.hard_total > 0 ? (stats.hard_solved / stats.hard_total) * 100 : 0;
            
            document.getElementById('easyFill').style.width = easyPercentage + '%';
            document.getElementById('mediumFill').style.width = mediumPercentage + '%';
            document.getElementById('hardFill').style.width = hardPercentage + '%';
            
            // Update solvedProblems array
            const solved = await api.getSolvedProblems();
            solvedProblems = solved;
            localStorage.setItem('solvedProblems', JSON.stringify(solvedProblems));
        } catch (error) {
            console.error('Failed to fetch stats from API, using local storage:', error);
            updateSidebarStatsLocal();
        }
    } else {
        updateSidebarStatsLocal();
    }
}

function updateSidebarStatsLocal() {
    const counts = countByDifficulty(leetcodeProblems);
    const total = leetcodeProblems.length;
    
    // Update total progress
    const percentage = total > 0 ? Math.round((solvedProblems.length / total) * 100) : 0;
    document.getElementById('totalProgress').textContent = percentage + '%';
    
    // Update difficulty progress
    const easyProblems = leetcodeProblems.filter(p => p.difficulty === 'Easy');
    const mediumProblems = leetcodeProblems.filter(p => p.difficulty === 'Medium');
    const hardProblems = leetcodeProblems.filter(p => p.difficulty === 'Hard');
    
    const easySolved = easyProblems.filter(p => solvedProblems.includes(p.id)).length;
    const mediumSolved = mediumProblems.filter(p => solvedProblems.includes(p.id)).length;
    const hardSolved = hardProblems.filter(p => solvedProblems.includes(p.id)).length;
    
    document.getElementById('easyCount').textContent = `${easySolved}/${easyProblems.length}`;
    document.getElementById('mediumCount').textContent = `${mediumSolved}/${mediumProblems.length}`;
    document.getElementById('hardCount').textContent = `${hardSolved}/${hardProblems.length}`;
    
    // Update progress bars
    const easyPercentage = easyProblems.length > 0 ? (easySolved / easyProblems.length) * 100 : 0;
    const mediumPercentage = mediumProblems.length > 0 ? (mediumSolved / mediumProblems.length) * 100 : 0;
    const hardPercentage = hardProblems.length > 0 ? (hardSolved / hardProblems.length) * 100 : 0;
    
    document.getElementById('easyFill').style.width = easyPercentage + '%';
    document.getElementById('mediumFill').style.width = mediumPercentage + '%';
    document.getElementById('hardFill').style.width = hardPercentage + '%';
    
    // Update streak (simplified - you can enhance this with actual activity tracking)
    document.getElementById('currentStreak').textContent = '0';
}

// Render problems by topic with proper categorization
function renderProblemsByTopic(problems = leetcodeProblems) {
    const container = document.getElementById('problemCategories');
    container.innerHTML = '';
    
    // Apply revision filter if active
    let problemsToShow = problems;
    if (isRevisionFilterActive) {
        problemsToShow = problems.filter(p => revisionProblems.includes(p.id));
    }
    // Apply company tag filter if any selected (AND logic)
    if (USE_API && selectedCompanyTagIds.size > 0) {
        const required = Array.from(selectedCompanyTagIds);
        problemsToShow = problemsToShow.filter(p => {
            const tagIds = problemToTagIds[p.id] || [];
            return required.every(tid => tagIds.includes(tid));
        });
    }
    
    // Apply solved/unsolved filter if active
    if (currentFilter === 'solved') {
        problemsToShow = problemsToShow.filter(p => solvedProblems.includes(p.id));
    } else if (currentFilter === 'unsolved') {
        problemsToShow = problemsToShow.filter(p => !solvedProblems.includes(p.id));
    }
    
    const grouped = groupProblemsByTopic(problemsToShow);
    
    // Define order for main categories (matching Leetcode_problem_set.html pattern structure)
    // Pattern-based organization as in Leetcode_problem_set.html
    const categoryOrder = [
        // Programming and Fundamentals
        'Programming Fundamentals', 'Time and Space Complexity / Online Judge', 'Dsa Fundamentals',
        // Core DSA patterns  
        'Hashing', '2 Pointers', 'Two Pointers', 'Sliding Window',
        'Stack', 'Queue', 'Linked List', 'Linked Lists',
        'Binary Tree', 'Trees', 'Binary Search', 'Binary Search Tree',
        'Heap (Priority Queue)', 'Heap',
        'Recursion & Backtracking', 'Backtracking',
        'Dynamic Programming', 'Dynamic Programming Level 1', 'Dynamic Programming Level 2', 
        'Greedy', 'Graphs', 'Tries', 'Bit Manipulation', 
        'Matrix', 'Sorting', 'String Matching Algos', 'Prefix Sum',
        'Intervals', 'Game Theory', 'Combinatorics & Geometry',
        'Advance algorithm'
    ];
    
    // Render categories in order
    categoryOrder.forEach(categoryName => {
        if (grouped[categoryName] && grouped[categoryName].length > 0) {
            const section = createTopicSectionWithSubcategories(categoryName, grouped[categoryName], []);
            container.appendChild(section);
        }
    });
    
    // Add any remaining topics not in the ordered list
    Object.keys(grouped).forEach(topic => {
        if (!categoryOrder.includes(topic) && grouped[topic].length > 0) {
            const section = createTopicSectionWithSubcategories(topic, grouped[topic], []);
            container.appendChild(section);
        }
    });
    
    updateSidebarStats();
}

// Render company tag filter chips
async function renderCompanyTagFilter() {
    const container = document.getElementById('companyFilter');
    if (!container) return;
    if (!USE_API) { container.innerHTML = ''; return; }

    await ensureCompanyTagsCache();
    container.innerHTML = '';
    Object.keys(companyTagsCache || {})
        .sort((a,b) => companyTagsCache[a].localeCompare(companyTagsCache[b]))
        .forEach(id => {
            const tid = parseInt(id, 10);
            const chip = document.createElement('button');
            chip.className = 'chip' + (selectedCompanyTagIds.has(tid) ? ' active' : '');
            chip.textContent = companyTagsCache[id];
            chip.addEventListener('click', () => {
                if (selectedCompanyTagIds.has(tid)) selectedCompanyTagIds.delete(tid);
                else selectedCompanyTagIds.add(tid);
                renderCompanyTagFilter();
                renderProblemsByTopic();
            });
            container.appendChild(chip);
        });
}

// Create topic section with subcategories
function createTopicSectionWithSubcategories(categoryName, problems, subcategoryNames) {
    const section = document.createElement('div');
    section.className = 'category';
    
    const header = document.createElement('div');
    header.className = 'category-header';
    header.innerHTML = `
        <span class="category-title">${categoryName}</span>
        <span class="category-arrow">›</span>
    `;
    
    const content = document.createElement('div');
    content.className = 'category-content';
    
    // Special handling for categories with subcategories (like Sliding Window, 2 Pointers, Stack, etc.)
    if (categoryName === 'Sliding Window') {
        const { fixedSize, dynamicSize } = categorizeSlidingWindow(problems);
        
        if (fixedSize.length > 0) {
            const subcategory = createSubcategory('Fixed Size Sliding-Window', fixedSize);
            content.appendChild(subcategory);
        }
        
        if (dynamicSize.length > 0) {
            const subcategory = createSubcategory('Dynamic Size Sliding-Window', dynamicSize);
            content.appendChild(subcategory);
        }
        
        // If no subcategories match, show all problems in a single table
        if (fixedSize.length === 0 && dynamicSize.length === 0) {
            const table = document.createElement('table');
            table.className = 'problem-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Problem</th>
                        <th>Difficulty</th>
                        <th>Practice</th>
                        <th>Company</th>
                        <th>Solution</th>
                        <th>Revision</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            const tbody = table.querySelector('tbody');
            problems.forEach(problem => {
                const row = createProblemRow(problem);
                tbody.appendChild(row);
            });
            
            content.appendChild(table);
        }
    } else if (categoryName === 'Two Pointers' || categoryName === '2 Pointers') {
        // Categorize 2 Pointers problems into Arrays vs Strings
        const arrayProblems = problems.filter(p => {
            const title = p.title.toLowerCase();
            return !title.includes('string') || (title.includes('string') && title.includes('array'));
        });
        const stringProblems = problems.filter(p => {
            const title = p.title.toLowerCase();
            return title.includes('string') && !title.includes('array');
        });
        
        if (arrayProblems.length > 0) {
            const subcategory = createSubcategory('Two Pointer on Arrays', arrayProblems);
            content.appendChild(subcategory);
        }
        
        if (stringProblems.length > 0) {
            const subcategory = createSubcategory('Two Pointer on Strings', stringProblems);
            content.appendChild(subcategory);
        }
        
        // If no subcategories match, show all problems in a single table
        if (arrayProblems.length === 0 && stringProblems.length === 0) {
            const table = document.createElement('table');
            table.className = 'problem-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Problem</th>
                        <th>Difficulty</th>
                        <th>Practice</th>
                        <th>Company</th>
                        <th>Solution</th>
                        <th>Revision</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            const tbody = table.querySelector('tbody');
            problems.forEach(problem => {
                const row = createProblemRow(problem);
                tbody.appendChild(row);
            });
            
            content.appendChild(table);
        }
    } else if (categoryName === 'Stack') {
        // Group Stack problems by subtopic
        const subtopicGroups = {};
        
        problems.forEach(problem => {
            const subtopic = problem.subtopic || 'Other';
            if (!subtopicGroups[subtopic]) {
                subtopicGroups[subtopic] = [];
            }
            subtopicGroups[subtopic].push(problem);
        });
        
        // Define order for Stack subcategories
        const stackSubcategoryOrder = [
            'Parentheses Problem',
            'Design Problems',
            'Advance Stack Problems',
            'Monotonic Stack'
        ];
        
        // Render subcategories in order
        const otherTopics = [];
        stackSubcategoryOrder.forEach(subtopicName => {
            if (subtopicGroups[subtopicName] && subtopicGroups[subtopicName].length > 0) {
                const subcategory = createSubcategory(subtopicName, subtopicGroups[subtopicName]);
                content.appendChild(subcategory);
            }
        });
        
        // Add any remaining topics not in the ordered list
        Object.keys(subtopicGroups).forEach(subtopic => {
            if (!stackSubcategoryOrder.includes(subtopic)) {
                otherTopics.push(...subtopicGroups[subtopic]);
            }
        });
        
        if (otherTopics.length > 0) {
            const subcategory = createSubcategory('Other', otherTopics);
            content.appendChild(subcategory);
        }
    } else if (categoryName === 'Queue') {
        // Group Queue problems by subtopic
        const subtopicGroups = {};
        
        problems.forEach(problem => {
            const subtopic = problem.subtopic || 'Other';
            if (!subtopicGroups[subtopic]) {
                subtopicGroups[subtopic] = [];
            }
            subtopicGroups[subtopic].push(problem);
        });
        
        // Define order for Queue subcategories
        const queueSubcategoryOrder = [
            'Implementation Problems',
            'Singly-Ended Queue',
            'Doubly-Ended Queue'
        ];
        
        // Render subcategories in order
        const otherTopics = [];
        queueSubcategoryOrder.forEach(subtopicName => {
            if (subtopicGroups[subtopicName] && subtopicGroups[subtopicName].length > 0) {
                const subcategory = createSubcategory(subtopicName, subtopicGroups[subtopicName]);
                content.appendChild(subcategory);
            }
        });
        
        // Add any remaining topics not in the ordered list
        Object.keys(subtopicGroups).forEach(subtopic => {
            if (!queueSubcategoryOrder.includes(subtopic)) {
                otherTopics.push(...subtopicGroups[subtopic]);
            }
        });
        
        if (otherTopics.length > 0) {
            const subcategory = createSubcategory('Other', otherTopics);
            content.appendChild(subcategory);
        }
    } else {
        // Check if this category has subtopics (general handler for all categories with subtopics)
        const hasSubtopics = problems.some(p => p.subtopic && p.subtopic.trim() !== '');
        
        if (hasSubtopics) {
            // Group problems by subtopic
            const subtopicGroups = {};
            
            problems.forEach(problem => {
                const subtopic = problem.subtopic || 'Other';
                if (!subtopicGroups[subtopic]) {
                    subtopicGroups[subtopic] = [];
                }
                subtopicGroups[subtopic].push(problem);
            });
            
            // Render all subcategories in alphabetical order
            const sortedSubtopics = Object.keys(subtopicGroups).sort();
            sortedSubtopics.forEach(subtopicName => {
                if (subtopicGroups[subtopicName].length > 0) {
                    const subcategory = createSubcategory(subtopicName, subtopicGroups[subtopicName]);
                    content.appendChild(subcategory);
                }
            });
        } else {
            // No subcategories, create a simple table
            const table = document.createElement('table');
            table.className = 'problem-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Problem</th>
                        <th>Difficulty</th>
                        <th>Practice</th>
                        <th>Company</th>
                        <th>Solution</th>
                        <th>Revision</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            const tbody = table.querySelector('tbody');
            problems.forEach(problem => {
                const row = createProblemRow(problem);
                tbody.appendChild(row);
            });
            
            content.appendChild(table);
            
            // Add "Add Problem" button at the end of category
            const addProblemBtn = document.createElement('div');
            addProblemBtn.className = 'add-problem-btn';
            addProblemBtn.innerHTML = '<button class="add-btn">+ Add Problem</button>';
            addProblemBtn.onclick = () => showAddProblemModal(categoryName, [categoryName]);
            content.appendChild(addProblemBtn);
        }
    }
    
    // Add event listener for collapse/expand
    header.addEventListener('click', () => {
        content.classList.toggle('expanded');
        header.classList.toggle('expanded');
    });
    
    section.appendChild(header);
    section.appendChild(content);
    
    return section;
}

// Categorize sliding window problems
function categorizeSlidingWindow(problems) {
    const fixedSizeKeywords = ['size', 'length', 'k radius', 'non-overlapping', 'distinct subarrays', 'sliding subarray', 'sliding window median', 'sliding window maximum', 'points you can obtain', 'size three', 'binary codes of size k', 'vowels in a substring of given length', 'average subarray', 'threshold', 'subarray beauty'];
    const dynamicSizeKeywords = ['longest', 'repeating character replacement', 'minimum size', 'max consecutive', 'product less than', 'minimum window', 'substring with concatenation', 'dominant ones', 'absolute diff less than', 'subarray product', 'grumpy', 'nice subarrays', 'bounded maximum', 'frequency of the most frequent', 'minimum consecutive cards', 'good subarrays', 'subarrays with k different'];
    
    const fixedSize = [];
    const dynamicSize = [];
    
    problems.forEach(problem => {
        const title = problem.title.toLowerCase();
        
        // Check for fixed size keywords
        const isFixedSize = fixedSizeKeywords.some(keyword => title.includes(keyword.toLowerCase()));
        
        if (isFixedSize) {
            fixedSize.push(problem);
        } else {
            // Check for dynamic size keywords
            const isDynamicSize = dynamicSizeKeywords.some(keyword => title.includes(keyword.toLowerCase()));
            
            if (isDynamicSize) {
                dynamicSize.push(problem);
            } else {
                // Default to dynamic size for unknown patterns
                dynamicSize.push(problem);
            }
        }
    });
    
    return { fixedSize, dynamicSize };
}

// Create a collapsible topic section with subcategories
function createTopicSection(topic, problems) {
    const section = document.createElement('div');
    section.className = 'category';
    
    const header = document.createElement('div');
    header.className = 'category-header';
    header.innerHTML = `
        <span class="category-title">${topic}</span>
        <span class="category-arrow">›</span>
    `;
    
    const content = document.createElement('div');
    content.className = 'category-content';
    
    // Special handling for Sliding Window with subcategories
    if (topic === 'Sliding Window') {
        const { fixedSize, dynamicSize } = categorizeSlidingWindow(problems);
        
        // Fixed Size Subcategory
        if (fixedSize.length > 0) {
            const subcategory = createSubcategory('Fixed Size Sliding-Window', fixedSize);
            content.appendChild(subcategory);
        }
        
        // Dynamic Size Subcategory
        if (dynamicSize.length > 0) {
            const subcategory = createSubcategory('Dynamic Size Sliding-Window', dynamicSize);
            content.appendChild(subcategory);
        }
    } else {
        // Regular single-level category
        const table = document.createElement('table');
        table.className = 'problem-table';
        table.innerHTML = `
            <thead>
                <tr>
                        <th>Problem</th>
                        <th>Difficulty</th>
                        <th>Practice</th>
                        <th>Company</th>
                        <th>Solution</th>
                        <th>Revision</th>
                        <th>Actions</th>
                </tr>
            </thead>
            <tbody id="problems-${topic}"></tbody>
        `;
        
        content.appendChild(table);
        
        // Render problems
        const tbody = table.querySelector('tbody');
        problems.forEach(problem => {
            const row = createProblemRow(problem);
            tbody.appendChild(row);
        });
    }
    
    // Add event listener for collapse/expand
    header.addEventListener('click', () => {
        content.classList.toggle('expanded');
        header.classList.toggle('expanded');
    });
    
    section.appendChild(header);
    section.appendChild(content);
    
    return section;
}

// Create a subcategory section
function createSubcategory(name, problems) {
    const subcategory = document.createElement('div');
    subcategory.className = 'subcategory';
    
    const subHeader = document.createElement('div');
    subHeader.className = 'subcategory-header';
    subHeader.innerHTML = `
        <span class="subcategory-arrow">›</span>
        <span class="subcategory-title">${name}</span>
    `;
    
    const subContent = document.createElement('div');
    subContent.className = 'subcategory-content';
    
    // Create table wrapper with indentation
    const tableWrapper = document.createElement('div');
    tableWrapper.className = 'subcategory-table-wrapper';
    
    const table = document.createElement('table');
    table.className = 'problem-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Problem</th>
                <th>Difficulty</th>
                <th>Practice</th>
                <th>Company</th>
                <th>Solution</th>
                <th>Revision</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;
    
    // Render problems
    const tbody = table.querySelector('tbody');
    problems.forEach(problem => {
        const row = createProblemRow(problem);
        tbody.appendChild(row);
    });
    
    tableWrapper.appendChild(table);
    subContent.appendChild(tableWrapper);
    
    // Add "Add Problem" button at the end of subcategory
    const addProblemBtn = document.createElement('div');
    addProblemBtn.className = 'add-problem-btn';
    addProblemBtn.innerHTML = '<button class="add-btn">+ Add Problem</button>';
    addProblemBtn.onclick = () => showAddProblemModal(name, problems.length > 0 ? problems[0].topics : []);
    subContent.appendChild(addProblemBtn);
    
    // Add event listener
    subHeader.addEventListener('click', () => {
        subContent.classList.toggle('expanded');
        subHeader.classList.toggle('expanded');
    });
    
    subcategory.appendChild(subHeader);
    subcategory.appendChild(subContent);
    
    return subcategory;
}

// Create a problem table row
let companyTagsCache = null; // id -> name cache
let companyTagsCachePromise = null; // in-flight request
let problemToTagIds = {}; // problem_id -> [tag_id]
let selectedCompanyTagIds = new Set();

async function ensureCompanyTagsCache() {
    if (!USE_API) return {};
    if (companyTagsCache) return companyTagsCache;
    if (!companyTagsCachePromise) {
        companyTagsCachePromise = (async () => {
            try {
                const tags = await api.listCompanyTags();
                const map = {};
                tags.forEach(t => { map[t.id] = t.name; });
                companyTagsCache = map;
                return companyTagsCache;
            } catch (e) {
                console.error('Failed to load company tags list', e);
                companyTagsCachePromise = null; // allow retries
                return {};
            }
        })();
    }
    return companyTagsCachePromise;
}

async function populateCompanyTags(problemId) {
    if (!USE_API) return;
    try {
        await ensureCompanyTagsCache();
        const tagIds = problemToTagIds[problemId] || [];
        const container = document.querySelector(`.company-tags[data-problem-id="${problemId}"]`);
        if (!container) return;
        container.innerHTML = '';
        tagIds.forEach(id => {
            const name = companyTagsCache && companyTagsCache[id] ? companyTagsCache[id] : `#${id}`;
            const el = document.createElement('span');
            el.className = 'tag-badge';
            el.textContent = name;
            container.appendChild(el);
        });
    } catch (e) {
        console.error('Failed to populate company tags', e);
    }
}

function createProblemRow(problem) {
    const row = document.createElement('tr');
    row.className = 'problem-row';
    const isSolved = solvedProblems.includes(problem.id);
    const isInRevision = revisionProblems.includes(problem.id);
    
    row.innerHTML = `
        <td>
            <div class="problem-name">
                <input type="checkbox" class="problem-checkbox" ${isSolved ? 'checked' : ''} 
                       data-problem-id="${problem.id}" />
                <span>${problem.title}</span>
            </div>
        </td>
        <td>
            <span class="difficulty-badge ${problem.difficulty.toLowerCase()}">${problem.difficulty}</span>
        </td>
        <td>
            <a href="${problem.link}" target="_blank" class="practice-link">🔗</a>
        </td>
        <td>
            <div class="company-cell">
                <div class="company-tags" data-problem-id="${problem.id}"></div>
                <button class="btn-tags" data-problem-id="${problem.id}" title="Manage company tags">🏷️ Tags</button>
            </div>
        </td>
        <td>
            <a href="solution.html?id=${problem.id}" class="solution-link" target="_blank">
                ${problem.solution_text ? '📝 Edit Solution' : '📝 Coming Soon'}
            </a>
        </td>
        <td>
            <span class="revision-icon ${isInRevision ? 'in-revision' : ''}" data-problem-id="${problem.id}" style="cursor: pointer;">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="${isInRevision ? '#1f2937' : 'none'}" stroke="#9ca3af" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 2v14l4-3 4 3V2"></path>
                </svg>
            </span>
        </td>
        <td>
            <button class="remove-btn" data-problem-id="${problem.id}" title="Remove problem">🗑️</button>
        </td>
    `;
    
    // Add checkbox event listener
    const checkbox = row.querySelector('.problem-checkbox');
    checkbox.addEventListener('change', (e) => handleCheckboxChange(e, problem.id));
    
    // Add revision icon event listener
    const revisionIcon = row.querySelector('.revision-icon');
    revisionIcon.addEventListener('click', (e) => toggleRevision(problem.id));
    
    // Add remove button event listener
    const removeBtn = row.querySelector('.remove-btn');
    removeBtn.addEventListener('click', (e) => handleRemoveProblem(problem.id));

    // Add tags button
    const tagsBtn = row.querySelector('.btn-tags');
    if (tagsBtn) {
        tagsBtn.addEventListener('click', () => openTagsModal(problem.id));
    }

    // Populate company tags asynchronously
    populateCompanyTags(problem.id);
    
    return row;
}

// Toggle revision status
async function toggleRevision(problemId) {
    const index = revisionProblems.indexOf(problemId);
    const isInRevision = index === -1; // Will be in revision after toggle
    
    if (index > -1) {
        // remove locally only if API disabled; API path will source truth
        if (!USE_API) {
            revisionProblems.splice(index, 1);
            localStorage.setItem('revisionProblems', JSON.stringify(revisionProblems));
        }
    } else {
        if (!USE_API) {
            revisionProblems.push(problemId);
            localStorage.setItem('revisionProblems', JSON.stringify(revisionProblems));
        }
    }
    
    // Sync with API (source of truth)
    if (USE_API) {
        try {
            if (isInRevision) {
                await api.addToRevision(problemId);
            } else {
                await api.removeFromRevision(problemId);
            }
            // Refresh revision list from API to keep local state in sync
            const revision = await api.getRevisionList();
            revisionProblems = revision;
        } catch (e) {
            console.error('Failed to sync revision with API', e);
        }
    }
    
    // Update the icon in the UI
    const icon = document.querySelector(`.revision-icon[data-problem-id="${problemId}"]`);
    if (icon) {
        icon.classList.toggle('in-revision');
        
        // Update the SVG fill attribute
        const svg = icon.querySelector('svg');
        if (svg) {
            svg.setAttribute('fill', isInRevision ? '#1f2937' : 'none');
        }
    }
}

// Update activity grid with bar heights
async function updateActivityGrid() {
    const grid = document.getElementById('activityGrid');
    if (!grid) return;
    
    // Get last 7 days
    const today = new Date();
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        days.push({
            date: formatDate(date),
            dayName: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()]
        });
    }
    
    // Count activity per day - use API data if available
    const activityCounts = {};
    
    if (USE_API) {
        try {
            const apiCalendarData = await api.getCalendarData();
            for (const item of apiCalendarData) {
                activityCounts[item.date] = item.problem_count;
            }
        } catch (error) {
            console.error('Failed to fetch calendar data for activity grid, using localStorage:', error);
            // Fallback to localStorage
            Object.keys(activityDates).forEach(dateKey => {
                activityCounts[dateKey] = activityDates[dateKey].length;
            });
        }
    } else {
        Object.keys(activityDates).forEach(dateKey => {
            activityCounts[dateKey] = activityDates[dateKey].length;
        });
    }
    
    // Find max count for scaling
    const maxCount = Math.max(...Object.values(activityCounts), 1);
    
    // Update grid
    grid.innerHTML = '';
    days.forEach(day => {
        const count = activityCounts[day.date] || 0;
        const height = count > 0 ? (count / maxCount) * 100 : 8;
        const dayEl = document.createElement('div');
        dayEl.className = 'activity-day';
        dayEl.textContent = day.dayName;
        if (count > 0) {
            dayEl.classList.add('active');
            dayEl.style.height = `${height}%`;
            dayEl.title = `${count} problem(s) on ${day.date}`;
        } else {
            dayEl.style.height = '8px';
        }
        grid.appendChild(dayEl);
    });
    
    // Update days spent
    const activeDays = days.filter(d => activityCounts[d.date] > 0).length;
    document.getElementById('daysSpent').textContent = String(activeDays).padStart(2, '0');
}

// Calculate streaks
function calculateStreaks(calendarDataMap = null) {
    // Use provided calendar data map (from API) or fallback to localStorage
    let datesWithActivity = [];
    
    if (calendarDataMap) {
        // Use API calendar data
        datesWithActivity = Object.keys(calendarDataMap)
            .filter(date => calendarDataMap[date] > 0)
            .sort();
    } else {
        // Use localStorage data
        datesWithActivity = Object.keys(activityDates)
            .filter(date => activityDates[date] && activityDates[date].length > 0)
            .sort();
    }
    
    let currentStreak = 0;
    let maxStreak = 0;
    let tempStreak = 0;
    
    const today = new Date();
    
    // Check if today has activity
    let checkDate = new Date(today);
    let hasCurrentActivity = false;
    
    if (datesWithActivity.length > 0) {
        const firstActivityDate = new Date(datesWithActivity[0]);
        
        // Calculate current streak (backwards from today)
        while (checkDate >= firstActivityDate) {
            const dateKey = formatDate(checkDate);
            let hasActivity = false;
            
            if (calendarDataMap) {
                hasActivity = (calendarDataMap[dateKey] || 0) > 0;
            } else {
                hasActivity = activityDates[dateKey] && activityDates[dateKey].length > 0;
            }
            
            if (hasActivity) {
                if (!hasCurrentActivity) {
                    currentStreak++;
                    hasCurrentActivity = true;
                }
            } else {
                break; // Streak broken
            }
            checkDate.setDate(checkDate.getDate() - 1);
        }
        
        // Calculate max streak
        for (let i = 0; i < datesWithActivity.length; i++) {
            if (i === 0) {
                tempStreak = 1;
                maxStreak = 1;
            } else {
                const prevDate = new Date(datesWithActivity[i - 1]);
                const currDate = new Date(datesWithActivity[i]);
                const diffDays = Math.floor((currDate - prevDate) / (1000 * 60 * 60 * 24));
                
                if (diffDays === 1) {
                    tempStreak++;
                } else {
                    tempStreak = 1;
                }
                maxStreak = Math.max(maxStreak, tempStreak);
            }
        }
    }
    
    return { currentStreak, maxStreak };
}

// Render calendar heatmap
async function renderCalendar() {
    const container = document.getElementById('calendarHeatmap');
    container.innerHTML = '';
    
    const today = new Date();
    const daysToShow = 371; // Show about 1 year + a few extra days
    const weeks = Math.ceil(daysToShow / 7);
    
    // Load calendar data from API or localStorage
    let calendarDataMap = {};
    let usedApiData = false;
    
    if (USE_API) {
        try {
            const apiCalendarData = await api.getCalendarData();
            for (const item of apiCalendarData) {
                calendarDataMap[item.date] = item.problem_count;
            }
            usedApiData = true;
        } catch (error) {
            console.error('Failed to fetch calendar data from API, using local storage:', error);
        }
    }
    
    // Only merge localStorage activity if API data wasn't used (prevents double counting)
    if (!usedApiData) {
        for (const dateKey in activityDates) {
            const count = activityDates[dateKey].length;
            calendarDataMap[dateKey] = (calendarDataMap[dateKey] || 0) + count;
        }
    }
    
    // Create calendar data
    const heatmapData = [];
    
    for (let i = daysToShow - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateKey = formatDate(date);
        const problemCount = calendarDataMap[dateKey] || 0;
        const hasActivity = problemCount > 0;
        
        heatmapData.push({
            date: dateKey,
            hasActivity,
            problemCount
        });
    }
    
    // Create heatmap structure
    const heatmapWrapper = document.createElement('div');
    heatmapWrapper.className = 'calendar-heatmap-container';
    
    // Group by weeks (columns)
    const weekColumns = [];
    for (let w = 0; w < weeks; w++) {
        const weekData = heatmapData.slice(w * 7, (w + 1) * 7);
        weekColumns.push(weekData);
    }
    
    // Render week columns
    weekColumns.forEach((week, weekIndex) => {
        const weekColumn = document.createElement('div');
        weekColumn.className = 'heatmap-column';
        
        week.forEach(dayData => {
            const dayCell = document.createElement('div');
            
            // Determine intensity level based on problem count
            if (dayData.hasActivity && dayData.problemCount > 0) {
                let intensityLevel = 'no-activity';
                if (dayData.problemCount >= 11) {
                    intensityLevel = 'intensity-4';
                } else if (dayData.problemCount >= 6) {
                    intensityLevel = 'intensity-3';
                } else if (dayData.problemCount >= 3) {
                    intensityLevel = 'intensity-2';
                } else {
                    intensityLevel = 'intensity-1';
                }
                dayCell.className = `calendar-day has-activity ${intensityLevel}`;
                dayCell.title = `${dayData.problemCount} problem(s) solved on ${dayData.date}`;
            } else {
                dayCell.className = 'calendar-day no-activity';
                dayCell.title = `No activity on ${dayData.date}`;
            }
            
            weekColumn.appendChild(dayCell);
        });
        
        heatmapWrapper.appendChild(weekColumn);
    });
    
    container.appendChild(heatmapWrapper);
    
    // Update streaks - pass calendarDataMap to use API data
    const { currentStreak, maxStreak } = calculateStreaks(usedApiData ? calendarDataMap : null);
    document.getElementById('currentStreak').textContent = currentStreak;
    document.getElementById('maxStreak').textContent = maxStreak;
}

// Handle checkbox changes
async function handleCheckboxChange(event, problemId) {
    const isChecked = event.target.checked;
    
    if (isChecked) {
        if (!solvedProblems.includes(problemId)) {
            solvedProblems.push(problemId);
            localStorage.setItem('solvedProblems', JSON.stringify(solvedProblems));
            await trackActivity(problemId); // Track activity when solved
            await updateSidebarStats();
        }
    } else {
        solvedProblems = solvedProblems.filter(id => id !== problemId);
        localStorage.setItem('solvedProblems', JSON.stringify(solvedProblems));
        await removeActivity(problemId); // Remove activity tracking when unchecked
        await updateSidebarStats();
    }
}

// Initialize categories as collapsed
function initCategories() {
    // Start with first category expanded
    const firstCategory = document.querySelector('.category-header');
    if (firstCategory) {
        firstCategory.click();
    }
}

// Search functionality
document.getElementById('searchInput').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    if (searchTerm === '') {
        renderProblemsByTopic();
    } else {
        const filtered = leetcodeProblems.filter(p => 
            p.title.toLowerCase().includes(searchTerm) ||
            p.topics.some(topic => topic.toLowerCase().includes(searchTerm))
        );
        renderProblemsByTopic(filtered);
    }
});

// Tab functionality
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
    });
});

// Initialize
async function initApp() {
    cleanupActivityTracking(); // Clean up any orphaned activity tracking
    
    // Load data from API if enabled
    if (USE_API) {
        try {
            // Load problems from API
            const allProblems = await api.getAllProblems();
            leetcodeProblems.length = 0;
            leetcodeProblems.push(...allProblems);
            
            // Load solved problems from API
            const solved = await api.getSolvedProblems();
            solvedProblems = solved;
            localStorage.setItem('solvedProblems', JSON.stringify(solvedProblems));
            // Load revision list from API only
            const revision = await api.getRevisionList();
            revisionProblems = revision;
            
            // Load progress stats
            await updateSidebarStats();
        } catch (error) {
            console.error('API not available, using local storage:', error);
            updateSidebarStatsLocal();
        }
    } else {
        updateSidebarStatsLocal();
    }
    
    await renderCalendar();
    await updateActivityGrid();
    // Preload company tags mapping once (avoid per-row requests)
    if (USE_API) {
        try {
            await ensureCompanyTagsCache();
            problemToTagIds = await api.getAllProblemCompanyTags();
        } catch (e) {
            problemToTagIds = {};
        }
    }
    await renderCompanyTagFilter();
    renderProblemsByTopic();
    initCategories();
}

// Start the app
initApp();

// Expand/Collapse functionality
document.getElementById('expandAllBtn').addEventListener('click', () => {
    // Expand main categories
    document.querySelectorAll('.category-content').forEach(content => {
        content.classList.add('expanded');
    });
    document.querySelectorAll('.category-header').forEach(header => {
        header.classList.add('expanded');
    });
    
    // Expand subcategories
    document.querySelectorAll('.subcategory-content').forEach(content => {
        content.classList.add('expanded');
    });
    document.querySelectorAll('.subcategory-header').forEach(header => {
        header.classList.add('expanded');
    });
});

document.getElementById('collapseAllBtn').addEventListener('click', () => {
    // Collapse main categories
    document.querySelectorAll('.category-content').forEach(content => {
        content.classList.remove('expanded');
    });
    document.querySelectorAll('.category-header').forEach(header => {
        header.classList.remove('expanded');
    });
    
    // Collapse subcategories
    document.querySelectorAll('.subcategory-content').forEach(content => {
        content.classList.remove('expanded');
    });
    document.querySelectorAll('.subcategory-header').forEach(header => {
        header.classList.remove('expanded');
    });
});

// Filter button functionality
document.getElementById('showSolvedBtn').addEventListener('click', () => {
    if (currentFilter === 'solved') {
        // Toggle off
        currentFilter = null;
        document.getElementById('showSolvedBtn').classList.remove('active');
    } else {
        // Activate solved filter
        currentFilter = 'solved';
        document.getElementById('showSolvedBtn').classList.add('active');
        document.getElementById('showUnsolvedBtn').classList.remove('active');
    }
    renderProblemsByTopic();
});

document.getElementById('showUnsolvedBtn').addEventListener('click', () => {
    if (currentFilter === 'unsolved') {
        // Toggle off
        currentFilter = null;
        document.getElementById('showUnsolvedBtn').classList.remove('active');
    } else {
        // Activate unsolved filter
        currentFilter = 'unsolved';
        document.getElementById('showUnsolvedBtn').classList.add('active');
        document.getElementById('showSolvedBtn').classList.remove('active');
    }
    renderProblemsByTopic();
});

// Revision List filter
document.getElementById('revisionListBtn').addEventListener('click', () => {
    isRevisionFilterActive = !isRevisionFilterActive;
    const btn = document.getElementById('revisionListBtn');
    
    if (isRevisionFilterActive) {
        btn.classList.add('active');
        btn.textContent = 'Exit Revision';
    } else {
        btn.classList.remove('active');
        btn.textContent = 'Revision List';
    }
    
    renderProblemsByTopic();
});

// Logout button
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
});

// Show add problem modal
function showAddProblemModal(subtopic, topics) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('addProblemModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'addProblemModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal">&times;</span>
                <h2>Add New Problem</h2>
                <form id="addProblemForm">
                    <div class="form-group">
                        <label for="problemTitle">Problem Title</label>
                        <input type="text" id="problemTitle" name="title" required>
                    </div>
                    <div class="form-group">
                        <label for="problemNumber">Problem Number</label>
                        <input type="number" id="problemNumber" name="number" required>
                    </div>
                    <div class="form-group">
                        <label for="problemDifficulty">Difficulty</label>
                        <select id="problemDifficulty" name="difficulty" required>
                            <option value="Easy">Easy</option>
                            <option value="Medium">Medium</option>
                            <option value="Hard">Hard</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="problemLink">LeetCode Link</label>
                        <input type="url" id="problemLink" name="link" required>
                    </div>
                    <div class="form-group">
                        <label for="problemSubtopic">Subtopic</label>
                        <input type="text" id="problemSubtopic" name="subtopic" readonly>
                    </div>
                    <button type="submit" class="submit-btn">Add Problem</button>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Close modal when clicking X or outside
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Set subtopic and topics
    document.getElementById('problemSubtopic').value = subtopic;
    
    // Show modal
    modal.style.display = 'block';
    
    // Handle form submission
    const form = document.getElementById('addProblemForm');
    const oldHandler = form.onclick;
    form.onsubmit = async (e) => {
        e.preventDefault();
        const problemData = {
            number: parseInt(document.getElementById('problemNumber').value),
            title: document.getElementById('problemTitle').value,
            difficulty: document.getElementById('problemDifficulty').value,
            topics: topics,
            link: document.getElementById('problemLink').value,
            subtopic: subtopic
        };
        
        try {
            const newProblem = await api.createProblem(problemData);
            modal.style.display = 'none';
            // Reload problems from API and re-render
            const allProblems = await api.getAllProblems();
            leetcodeProblems.length = 0;
            leetcodeProblems.push(...allProblems);
            renderProblemsByTopic();
            alert('Problem added successfully!');
        } catch (error) {
            console.error('Failed to add problem:', error);
            alert('Failed to add problem. Please try again.');
        }
    };
}

// Handle remove
async function handleRemoveProblem(problemId) {
    if (!confirm('Are you sure you want to remove this problem?')) return;
    try {
        await api.deleteProblem(problemId);
        // Refresh problems and UI
        const allProblems = await api.getAllProblems();
        leetcodeProblems.length = 0;
        leetcodeProblems.push(...allProblems);
        renderProblemsByTopic();
    } catch (err) {
        console.error('Failed to delete problem:', err);
        alert('Failed to delete problem.');
    }
}

// Company tags modal
async function openTagsModal(problemId) {
    // Fetch all tags and current selections
    let allTags = [];
    let selected = [];
    try {
        allTags = await api.listCompanyTags();
        selected = await api.getProblemCompanyTags(problemId);
    } catch (e) {
        console.error('Failed to load company tags', e);
        alert('Failed to load company tags');
        return;
    }

    // Build modal
    let modal = document.getElementById('tagsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'tagsModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
              <span class="close-modal">&times;</span>
              <h2>Assign Company Tags</h2>
              <div id="tagsList" style="max-height:260px;overflow:auto;margin:12px 0;"></div>
              <div style="display:flex;gap:8px;justify-content:flex-end;">
                <a class="submit-btn" id="manageTagsLink" href="company.html" target="_blank">Manage Tags</a>
                <button class="submit-btn" id="saveTagsBtn">Save</button>
              </div>
            </div>`;
        document.body.appendChild(modal);
        modal.querySelector('.close-modal').addEventListener('click', () => modal.style.display = 'none');
        window.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
    }

    const list = modal.querySelector('#tagsList');
    list.innerHTML = '';
    allTags.forEach(tag => {
        const id = `tag_${tag.id}`;
        const div = document.createElement('div');
        div.innerHTML = `<label style="display:flex;align-items:center;gap:8px;">
            <input type="checkbox" value="${tag.id}" ${selected.includes(tag.id) ? 'checked' : ''}/>
            ${tag.name}
        </label>`;
        list.appendChild(div);
    });

    modal.style.display = 'block';

    modal.querySelector('#saveTagsBtn').onclick = async () => {
        const chosen = Array.from(list.querySelectorAll('input[type="checkbox"]:checked')).map(i => parseInt(i.value, 10));
        try {
            await api.setProblemCompanyTags(problemId, chosen);
            modal.style.display = 'none';
            // Refresh badges for this row
            await ensureCompanyTagsCache();
            problemToTagIds[problemId] = chosen;
            await populateCompanyTags(problemId);
        } catch (e) {
            console.error('Failed to save tags', e);
            alert('Failed to save tags');
        }
    };
}
