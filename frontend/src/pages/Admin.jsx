import React, { useState, useEffect } from "react";

export default function AdminPage() {
    const [currentUser, setCurrentUser] = useState(null);
    const [activeSection, setActiveSection] = useState('users');
    const [loading, setLoading] = useState(true);
    
    // User Management State
    const [users, setUsers] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [filteredUsers, setFilteredUsers] = useState([]);
    const [userError, setUserError] = useState('');
    
    // Research Data State
    const [researchData, setResearchData] = useState([]);
    const [researchLoading, setResearchLoading] = useState(false);
    const [researchError, setResearchError] = useState('');
    
    // Question Upload State
    const [questionText, setQuestionText] = useState('');
    const [questionImage, setQuestionImage] = useState(null);
    const [answer, setAnswer] = useState('');
    const [uploadError, setUploadError] = useState('');
    const [uploadSuccess, setUploadSuccess] = useState('');

    // Get auth token from localStorage
    const getAuthToken = () => {
        return localStorage.getItem('access_token');
    };

    // Check authentication and get current user
    useEffect(() => {
        async function checkAuth() {
            setLoading(true);
            try {
                const token = getAuthToken();
                if (!token) {
                    window.location.href = '/login';
                    return;
                }

                const res = await fetch("/auth/me", {
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                if (!res.ok) {
                    window.location.href = '/login';
                    return;
                }

                const data = await res.json();
                
                if (!data.is_admin) {
                    window.location.href = '/';
                    return;
                }

                setCurrentUser(data);
                await loadUsers(token);
            } catch (err) {
                console.error('Auth error:', err);
                window.location.href = '/login';
            } finally {
                setLoading(false);
            }
        }
        checkAuth();
    }, []);

    // Load all users
    async function loadUsers(token) {
        try {
            const res = await fetch('/auth/users', {
                headers: {
                    "Authorization": `Bearer ${token || getAuthToken()}`
                }
            });

            if (!res.ok) throw new Error('Failed to load users');
            
            const data = await res.json();
            setUsers(data);
            setFilteredUsers(data);
        } catch (err) {
            setUserError(err.message || 'Failed to load users');
        }
    }

    // Filter users based on search
    useEffect(() => {
        if (searchQuery.trim() === '') {
            setFilteredUsers(users);
        } else {
            const query = searchQuery.toLowerCase();
            setFilteredUsers(users.filter(u => 
                u.username.toLowerCase().includes(query) || 
                u.email.toLowerCase().includes(query)
            ));
        }
    }, [searchQuery, users]);

    // Promote user to admin
    async function promoteToAdmin(userEmail) {
        setUserError('');
        try {
            const token = getAuthToken();
            const res = await fetch(`/auth/admin/promote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ email: userEmail })
            });

            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || 'Failed to promote user');
            }
            
            await loadUsers(token);
            alert('User promoted to admin successfully!');
        } catch (err) {
            setUserError(err.message || 'Failed to promote user');
        }
    }

    // Demote user from admin
    async function demoteFromAdmin(userEmail) {
        setUserError('');
        try {
            const token = getAuthToken();
            const res = await fetch(`/auth/admin/demote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ email: userEmail })
            });

            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || 'Failed to demote user');
            }
            
            await loadUsers(token);
            alert('User demoted from admin successfully!');
        } catch (err) {
            setUserError(err.message || 'Failed to demote user');
        }
    }

    // Load research data (annotations from all users who consented)
    async function loadResearchData() {
        setResearchLoading(true);
        setResearchError('');
        try {
            const token = getAuthToken();
            const res = await fetch('/auth/annotations/all', {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!res.ok) throw new Error('Failed to load research data');
            
            const data = await res.json();
            setResearchData(data);
        } catch (err) {
            setResearchError(err.message || 'Failed to load research data');
        } finally {
            setResearchLoading(false);
        }
    }

    // Export research data to CSV
    function exportResearchCSV() {
        if (!researchData || researchData.length === 0) return;
        
        const keys = Object.keys(researchData[0]);
        const csv = [
            keys.join(","),
            ...researchData.map(row => keys.map(k => JSON.stringify(row[k] ?? "")).join(",")),
        ].join("\n");
        
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `research-data-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Upload question
    async function handleQuestionUpload() {
        setUploadError('');
        setUploadSuccess('');
        
        if (!questionText || !answer) {
            setUploadError('Question text and answer are required');
            return;
        }

        try {
            const token = getAuthToken();
            const formData = new FormData();
            formData.append('question', questionText);
            formData.append('answer', answer);
            if (questionImage) {
                formData.append('image', questionImage);
            }

            const res = await fetch('/auth/admin/questions', {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });

            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || 'Failed to upload question');
            }

            setUploadSuccess('Question uploaded successfully!');
            setQuestionText('');
            setAnswer('');
            setQuestionImage(null);
            
            // Clear file input
            const fileInput = document.querySelector('input[type="file"][accept="image/*"]');
            if (fileInput) fileInput.value = '';
        } catch (err) {
            setUploadError(err.message || 'Failed to upload question');
        }
    }

    // Handle image file selection
    function handleImageChange(e) {
        const file = e.target.files[0];
        if (file) {
            if (!file.type.startsWith('image/')) {
                setUploadError('Please select a valid image file');
                return;
            }
            setQuestionImage(file);
            setUploadError('');
        }
    }



    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen text-[#F4EBD3] text-xl">
                Loading admin dashboard...
            </div>
        );
    }

    if (!currentUser || !currentUser.is_admin) {
        return (
            <div className="flex justify-center items-center min-h-screen text-[#F4EBD3] text-xl">
                Access Denied
            </div>
        );
    }


    return (
        <div className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="bg-[#555879] rounded-2xl shadow-2xl p-8 mb-6">
                    <h1 className="text-center text-4xl font-bold text-[#F4EBD3] mb-2">Admin Dashboard</h1>
                    <p className="text-center text-[#F4EBD3] opacity-80">
                        Welcome, {currentUser.first_name} {currentUser.last_name}
                    </p>
                </div>

                {/* Navigation Tabs */}
                <div className="flex gap-4 mb-6 flex-wrap">
                    <button
                        onClick={() => setActiveSection('users')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${
                            activeSection === 'users'
                                ? 'bg-[#F4EBD3] text-[#555879]'
                                : 'bg-[#555879] text-[#F4EBD3] hover:bg-[#6b6b94]'
                        }`}
                    >
                        User Management
                    </button>
                    <button
                        onClick={() => setActiveSection('research')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${
                            activeSection === 'research'
                                ? 'bg-[#F4EBD3] text-[#555879]'
                                : 'bg-[#555879] text-[#F4EBD3] hover:bg-[#6b6b94]'
                        }`}
                    >
                        Research Data
                    </button>
                    <button
                        onClick={() => setActiveSection('questions')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${
                            activeSection === 'questions'
                                ? 'bg-[#F4EBD3] text-[#555879]'
                                : 'bg-[#555879] text-[#F4EBD3] hover:bg-[#6b6b94]'
                        }`}
                    >
                        Upload Questions
                    </button>
                </div>

                {/* User Management Section */}
                {activeSection === 'users' && (
                    <div className="bg-[#555879] rounded-2xl shadow-2xl p-8">
                        <h2 className="text-3xl font-bold text-[#F4EBD3] mb-6">User Management</h2>
                        
                        {userError && <div className="text-red-300 font-semibold mb-4">{userError}</div>}
                        
                        <div className="mb-6">
                            <label className="text-[#F4EBD3] font-semibold mb-2 block">
                                Search Users
                            </label>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search by username or email..."
                                className="w-full border p-3 rounded text-[#555879] bg-[#F4EBD3] placeholder-[#555879] placeholder-opacity-50"
                            />
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full border-collapse">
                                <thead>
                                    <tr className="border-b-2 border-[#F4EBD3]">
                                        <th className="text-left p-3 text-[#F4EBD3] font-bold">Username</th>
                                        <th className="text-left p-3 text-[#F4EBD3] font-bold">Email</th>
                                        <th className="text-left p-3 text-[#F4EBD3] font-bold">Role</th>
                                        <th className="text-left p-3 text-[#F4EBD3] font-bold">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredUsers.map((user) => (
                                        <tr key={user.id} className="border-b border-[#F4EBD3] border-opacity-30">
                                            <td className="p-3 text-[#F4EBD3]">{user.username}</td>
                                            <td className="p-3 text-[#F4EBD3]">{user.email}</td>
                                            <td className="p-3">
                                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                                    user.is_admin 
                                                        ? 'bg-[#F4EBD3] text-[#555879]' 
                                                        : 'bg-[#6b6b94] text-[#F4EBD3]'
                                                }`}>
                                                    {user.is_admin ? 'admin' : 'user'}
                                                </span>
                                            </td>
                                            <td className="p-3">
                                                {!user.is_admin ? (
                                                    <button
                                                        onClick={() => promoteToAdmin(user.email)}
                                                        className="px-4 py-2 rounded-lg bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all"
                                                    >
                                                        Promote to Admin
                                                    </button>
                                                ) : user.id !== currentUser.id && (
                                                    <button
                                                        onClick={() => demoteFromAdmin(user.email)}
                                                        className="px-4 py-2 rounded-lg bg-red-600 text-white font-bold hover:bg-red-700 transition-all"
                                                    >
                                                        Demote from Admin
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        
                        {filteredUsers.length === 0 && (
                            <div className="text-center text-[#F4EBD3] py-8">
                                No users found matching your search.
                            </div>
                        )}
                    </div>
                )}

                {/* Research Data Section */}
                {activeSection === 'research' && (
                    <div className="bg-[#555879] rounded-2xl shadow-2xl p-8">
                        <h2 className="text-3xl font-bold text-[#F4EBD3] mb-6">Research Data</h2>
                        
                        {researchError && <div className="text-red-300 font-semibold mb-4">{researchError}</div>}
                        
                        <div className="flex gap-4 mb-6">
                            <button
                                onClick={loadResearchData}
                                disabled={researchLoading}
                                className="flex-1 border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all disabled:opacity-50"
                            >
                                {researchLoading ? 'Loading...' : 'Load Research Data'}
                            </button>
                            <button
                                onClick={exportResearchCSV}
                                disabled={researchData.length === 0}
                                className="flex-1 border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all disabled:opacity-50"
                            >
                                Export to CSV
                            </button>
                        </div>

                        {researchData.length > 0 && (
                            <div className="overflow-x-auto border border-[#F4EBD3] rounded-lg p-4 bg-[#F4EBD3]">
                                <table className="w-full border-collapse">
                                    <thead>
                                        <tr>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">User</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Session ID</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Question ID</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Time Spent</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Correct</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Created</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {researchData.map((row, idx) => (
                                            <tr key={idx} className="hover:bg-[#D4C4A8] transition-all">
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.username || row.user_id}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.session_id}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.question_id}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.time_spent ? `${row.time_spent.toFixed(2)}s` : 'N/A'}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">
                                                    {row.is_correct === null ? 'Pending' : row.is_correct ? 'Yes' : 'No'}
                                                </td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">
                                                    {new Date(row.created_at).toLocaleDateString()}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {researchData.length === 0 && !researchLoading && (
                            <div className="text-center text-[#F4EBD3] py-8">
                                No research data loaded. Click "Load Research Data" to view results.
                            </div>
                        )}
                    </div>
                )}

                {/* Question Upload Section */}
                {activeSection === 'questions' && (
                    <div className="bg-[#555879] rounded-2xl shadow-2xl p-8">
                        <h2 className="text-3xl font-bold text-[#F4EBD3] mb-6">Upload Questions</h2>
                        
                        {uploadError && <div className="text-red-300 font-semibold mb-4">{uploadError}</div>}
                        {uploadSuccess && <div className="text-green-300 font-semibold mb-4">{uploadSuccess}</div>}
                        
                        <div className="space-y-4">
                            <div>
                                <label className="text-[#F4EBD3] font-semibold mb-2 block">
                                    Question Text
                                </label>
                                <textarea
                                    value={questionText}
                                    onChange={(e) => setQuestionText(e.target.value)}
                                    placeholder="Enter the question..."
                                    rows={4}
                                    className="w-full border p-3 rounded text-[#555879] bg-[#F4EBD3] placeholder-[#555879] placeholder-opacity-50 resize-none"
                                />
                            </div>

                            <div>
                                <label className="text-[#F4EBD3] font-semibold mb-2 block">
                                    Question Image (Optional)
                                </label>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageChange}
                                    className="w-full border p-3 rounded bg-[#F4EBD3] text-[#555879] file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-[#555879] file:text-[#F4EBD3] file:font-bold hover:file:bg-[#6b6b94]"
                                />
                                {questionImage && (
                                    <p className="text-[#F4EBD3] mt-2">Selected: {questionImage.name}</p>
                                )}
                            </div>

                            <div>
                                <label className="text-[#F4EBD3] font-semibold mb-2 block">
                                    Answer
                                </label>
                                <input
                                    type="text"
                                    value={answer}
                                    onChange={(e) => setAnswer(e.target.value)}
                                    placeholder="Enter the correct answer..."
                                    className="w-full border p-3 rounded text-[#555879] bg-[#F4EBD3] placeholder-[#555879] placeholder-opacity-50"
                                />
                            </div>

                            <button
                                onClick={handleQuestionUpload}
                                className="w-full border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all"
                            >
                                Upload Question
                            </button>
                        </div>
                    </div>
                )}


            </div>
        </div>
    );
}