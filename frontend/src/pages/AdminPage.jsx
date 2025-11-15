import React, { useState, useEffect } from "react";

export default function AdminPage() {
    const testUser = { id: 1, name: 'Admin User', role: 'admin' };
    const mockUsers = [
        { id: 1, username: 'johndoe', email: 'john@example.com', role: 'user', consentAccepted: true },
        { id: 2, username: 'janedoe', email: 'jane@example.com', role: 'admin', consentAccepted: true },
        { id: 3, username: 'bobsmith', email: 'bob@example.com', role: 'user', consentAccepted: false },
    ];
    const mockResearchData = [
        { userId: 1, username: 'johndoe', totalAttempts: 15, avgTimeSpent: '5m 32s', accuracy: 85.5, totalTime: '1h 23m', correctQuestions: 128, incorrectQuestions: 22, consentDate: '2024-01-15' },
        { userId: 2, username: 'janedoe', totalAttempts: 23, avgTimeSpent: '4m 18s', accuracy: 92.3, totalTime: '1h 39m', correctQuestions: 201, incorrectQuestions: 17, consentDate: '2024-01-10' },
    ];

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
    
    // Consent Form State
    const [consentFormType, setConsentFormType] = useState('default');
    const [customConsentForm, setCustomConsentForm] = useState(null);
    const [consentError, setConsentError] = useState('');
    const [consentSuccess, setConsentSuccess] = useState('');

    useEffect(() => {
        async function checkAuth() {
            setLoading(true);
            try {
                // const res = await fetch("/api/user", { credentials: "include" });
                // const data = await res.json();
                const data = testUser;
                
                if (data.role !== 'admin') {
                    window.location.href = '/';
                    return;
                }
                setCurrentUser(data);
                setUsers(mockUsers);
                setFilteredUsers(mockUsers);
            } catch (err) {
                window.location.href = '/login';
            } finally {
                setLoading(false);
            }
        }
        checkAuth();
    }, []);

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

    async function promoteToAdmin(userId) {
        setUserError('');
        try {
            // const res = await fetch(`/api/admin/users/${userId}/promote`, {
            //     method: 'POST',
            //     credentials: 'include'
            // });
            // if (!res.ok) throw new Error('Failed to promote user');
            
            setUsers(users.map(u => u.id === userId ? {...u, role: 'admin'} : u));
            alert('User promoted to admin successfully!');
        } catch (err) {
            setUserError(err.message || 'Failed to promote user');
        }
    }

    async function loadResearchData() {
        setResearchLoading(true);
        setResearchError('');
        try {
            // const res = await fetch('/api/admin/research', { credentials: 'include' });
            // if (!res.ok) throw new Error('Failed to load research data');
            // const data = await res.json();
            
            setResearchData(mockResearchData);
        } catch (err) {
            setResearchError(err.message || 'Failed to load research data');
        } finally {
            setResearchLoading(false);
        }
    }

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
        a.download = "research-data.csv";
        a.click();
        URL.revokeObjectURL(url);
    }

    async function handleQuestionUpload() {
        setUploadError('');
        setUploadSuccess('');
        
        if (!questionText || !answer) {
            setUploadError('Question text and answer are required');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('question', questionText);
            formData.append('answer', answer);
            if (questionImage) {
                formData.append('image', questionImage);
            }

            // const res = await fetch('/api/admin/questions', {
            //     method: 'POST',
            //     credentials: 'include',
            //     body: formData
            // });
            // if (!res.ok) throw new Error('Failed to upload question');

            setUploadSuccess('Question uploaded successfully!');
            setQuestionText('');
            setAnswer('');
            setQuestionImage(null);
        } catch (err) {
            setUploadError(err.message || 'Failed to upload question');
        }
    }

    function handleImageChange(e) {
        const file = e.target.files[0];
        if (file) {
            if (!file.type.startsWith('image/')) {
                setUploadError('Please select a valid image file');
                return;
            }
            setQuestionImage(file);
        }
    }

    async function handleConsentFormUpload() {
        setConsentError('');
        setConsentSuccess('');

        if (consentFormType === 'custom' && !customConsentForm) {
            setConsentError('Please select a consent form file');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('type', consentFormType);
            if (consentFormType === 'custom' && customConsentForm) {
                formData.append('consentForm', customConsentForm);
            }

            // const res = await fetch('/api/admin/consent-form', {
            //     method: 'POST',
            //     credentials: 'include',
            //     body: formData
            // });
            // if (!res.ok) throw new Error('Failed to update consent form');

            setConsentSuccess('Consent form updated successfully!');
            setCustomConsentForm(null);
        } catch (err) {
            setConsentError(err.message || 'Failed to update consent form');
        }
    }

    function handleConsentFormChange(e) {
        const file = e.target.files[0];
        if (file) {
            if (file.type !== 'application/pdf' && !file.type.startsWith('text/')) {
                setConsentError('Please select a PDF or text file');
                return;
            }
            setCustomConsentForm(file);
        }
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen text-[#F4EBD3] text-xl">
                Loading admin dashboard...
            </div>
        );
    }

    if (!currentUser || currentUser.role !== 'admin') {
        return (
            <div className="flex justify-center items-center min-h-screen text-[#F4EBD3] text-xl">
                Access Denied
            </div>
        );
    }

    const optedInCount = users.filter(u => u.consentAccepted).length;

    return (
        <div className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="bg-[#555879] rounded-2xl shadow-2xl p-8 mb-6">
                    <h1 className="text-center text-4xl font-bold text-[#F4EBD3] mb-2">Admin Dashboard</h1>
                    <p className="text-center text-[#F4EBD3] opacity-80">Welcome, {currentUser.name}</p>
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
                    <button
                        onClick={() => setActiveSection('consent')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${
                            activeSection === 'consent'
                                ? 'bg-[#F4EBD3] text-[#555879]'
                                : 'bg-[#555879] text-[#F4EBD3] hover:bg-[#6b6b94]'
                        }`}
                    >
                        Consent Form
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
                                        <th className="text-left p-3 text-[#F4EBD3] font-bold">Research Consent</th>
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
                                                    user.role === 'admin' 
                                                        ? 'bg-[#F4EBD3] text-[#555879]' 
                                                        : 'bg-[#6b6b94] text-[#F4EBD3]'
                                                }`}>
                                                    {user.role}
                                                </span>
                                            </td>
                                            <td className="p-3">
                                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                                    user.consentAccepted 
                                                        ? 'bg-green-600 text-white' 
                                                        : 'bg-red-600 text-white'
                                                }`}>
                                                    {user.consentAccepted ? 'Opted In' : 'Not Opted In'}
                                                </span>
                                            </td>
                                            <td className="p-3">
                                                {user.role !== 'admin' && (
                                                    <button
                                                        onClick={() => promoteToAdmin(user.id)}
                                                        className="px-4 py-2 rounded-lg bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all"
                                                    >
                                                        Promote to Admin
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
                        
                        <div className="bg-[#F4EBD3] rounded-lg p-4 mb-6">
                            <p className="text-[#555879] font-bold text-lg">
                                Total Users Opted In: {optedInCount}
                            </p>
                        </div>

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
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Username</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Consent Date</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Total Attempts</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Avg Time</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Accuracy</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Total Time</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Correct</th>
                                            <th className="text-left p-3 border-b-2 border-[#555879] text-[#555879] font-bold">Incorrect</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {researchData.map((row, idx) => (
                                            <tr key={idx} className="hover:bg-[#D4C4A8] transition-all">
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.username}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.consentDate}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.totalAttempts}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.avgTimeSpent}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.accuracy}%</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.totalTime}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.correctQuestions}</td>
                                                <td className="p-3 border-b border-[#555879] border-opacity-20 text-[#555879]">{row.incorrectQuestions}</td>
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

                {/* Consent Form Section */}
                {activeSection === 'consent' && (
                    <div className="bg-[#555879] rounded-2xl shadow-2xl p-8">
                        <h2 className="text-3xl font-bold text-[#F4EBD3] mb-6">Consent Form Settings</h2>
                        
                        {consentError && <div className="text-red-300 font-semibold mb-4">{consentError}</div>}
                        {consentSuccess && <div className="text-green-300 font-semibold mb-4">{consentSuccess}</div>}
                        
                        <div className="space-y-4">
                            <div>
                                <label className="text-[#F4EBD3] font-semibold mb-3 block">
                                    Select Consent Form Type
                                </label>
                                <div className="space-y-3">
                                    <label className="flex items-center space-x-3 cursor-pointer">
                                        <input
                                            type="radio"
                                            value="default"
                                            checked={consentFormType === 'default'}
                                            onChange={(e) => setConsentFormType(e.target.value)}
                                            className="w-5 h-5"
                                        />
                                        <span className="text-[#F4EBD3] text-lg">Use Default Consent Form</span>
                                    </label>
                                    <label className="flex items-center space-x-3 cursor-pointer">
                                        <input
                                            type="radio"
                                            value="custom"
                                            checked={consentFormType === 'custom'}
                                            onChange={(e) => setConsentFormType(e.target.value)}
                                            className="w-5 h-5"
                                        />
                                        <span className="text-[#F4EBD3] text-lg">Upload Custom Consent Form</span>
                                    </label>
                                </div>
                            </div>

                            {consentFormType === 'custom' && (
                                <div>
                                    <label className="text-[#F4EBD3] font-semibold mb-2 block">
                                        Upload Custom Consent Form (PDF or TXT)
                                    </label>
                                    <input
                                        type="file"
                                        accept=".pdf,.txt,text/plain,application/pdf"
                                        onChange={handleConsentFormChange}
                                        className="w-full border p-3 rounded bg-[#F4EBD3] text-[#555879] file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-[#555879] file:text-[#F4EBD3] file:font-bold hover:file:bg-[#6b6b94]"
                                    />
                                    {customConsentForm && (
                                        <p className="text-[#F4EBD3] mt-2">Selected: {customConsentForm.name}</p>
                                    )}
                                </div>
                            )}

                            <div className="bg-[#F4EBD3] rounded-lg p-4">
                                <p className="text-[#555879] font-semibold">
                                    Note: The consent form will be displayed to all users before they can participate in research. Make sure it clearly explains how their data will be used.
                                </p>
                            </div>

                            <button
                                onClick={handleConsentFormUpload}
                                className="w-full border p-3 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all"
                            >
                                Update Consent Form
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}