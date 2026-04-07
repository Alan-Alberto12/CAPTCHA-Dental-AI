import React, { useState, useRef, useEffect, useCallback } from 'react';
import { API_URL } from '../config';

// helper functions
const fmtMins = (m) => {
  if (m == null) return '—';
  return `${Math.floor(m / 60)}h ${m % 60}m`;
};

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function exportCSV(users) {
  const headers = ['Username', 'Email', 'Date Joined', 'Annotations', 'Total Time (mins)', 'Avg Session Time (mins)'];
  const rows = users.map(u => [
    u.username,
    u.email,
    u.created_at ? new Date(u.created_at).toLocaleDateString() : '',
    u.stats?.total_annotations ?? 0,
    u.stats?.total_time_minutes ?? 0,
    u.stats?.avg_session_time_minutes ?? 0,
  ]);
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'user_statistics.csv'; a.click();
  URL.revokeObjectURL(url);
}

function SearchBar({ value, onChange, placeholder }) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold mb-2 text-[#F4EBD3]">Search Users</label>
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder || 'Search by username or email...'}
        className="w-full bg-[#F4EBD3] rounded-2xl px-6 py-4 text-base focus:outline-none focus:ring-2 focus:ring-[#98A1BC] placeholder-gray-500 shadow-sm"
      />
    </div>
  );
}

function StatusBadge({ ok, text }) {
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
      {text}
    </span>
  );
}

// User Management Tab
function UserManagement() {
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionMsg, setActionMsg] = useState(null);
  const [actionError, setActionError] = useState(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/auth/admin/users`, { headers: authHeaders() });
      if (!res.ok) throw new Error(`Failed to load users (${res.status})`);
      const data = await res.json();
      setUsers(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const filtered = users.filter(u =>
    u.username.toLowerCase().includes(query.toLowerCase()) ||
    u.email.toLowerCase().includes(query.toLowerCase())
  );

  const changeRole = async (user, promote) => {
    setActionMsg(null);
    setActionError(null);
    const endpoint = promote ? '/auth/admin/promote' : '/auth/admin/demote';
    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ email: user.email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Action failed');
      setActionMsg(`${user.username} ${promote ? 'promoted to admin' : 'demoted to user'} successfully.`);
      setUsers(prev => prev.map(u => u.id === user.id ? { ...u, is_admin: promote } : u));
    } catch (e) {
      setActionError(e.message);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-[#F4EBD3]">User Management</h2>

      {actionMsg && (
        <div className="mb-4 bg-green-100 text-green-800 rounded-xl px-4 py-3 text-sm font-semibold">{actionMsg}</div>
      )}
      {actionError && (
        <div className="mb-4 bg-red-100 text-red-800 rounded-xl px-4 py-3 text-sm font-semibold">{actionError}</div>
      )}

      <SearchBar value={query} onChange={setQuery} />

      {loading ? (
        <div className="text-[#F4EBD3] text-center py-12 text-lg">Loading users...</div>
      ) : error ? (
        <div className="bg-red-100 text-red-800 rounded-xl px-6 py-4 text-sm font-semibold">
          {error}
          <button onClick={fetchUsers} className="ml-4 underline">Retry</button>
        </div>
      ) : (
        <div className="bg-[#F4EBD3] rounded-2xl shadow-md overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-[#c9bfa8]">
                {['Username', 'Email', 'Role', 'Actions'].map(h => (
                  <th key={h} className="text-left px-6 py-4 text-sm font-bold text-[#525470]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((u, i) => (
                <tr key={u.id} className={`border-b border-[#ddd3bc] ${i % 2 === 0 ? '' : 'bg-[#EDE4CC]'} hover:bg-[#DED3C4] transition-colors`}>
                  <td className="px-6 py-4 font-semibold text-[#2a2a2a]">{u.username}</td>
                  <td className="px-6 py-4 text-[#555]">{u.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${u.is_admin ? 'bg-[#525470] text-white' : 'bg-[#ddd3bc] text-[#444]'}`}>
                      {u.is_admin ? 'admin' : 'user'}
                    </span>
                  </td>
                  <td className="px-6 py-4 flex gap-2 flex-wrap">
                    {!u.is_admin ? (
                      <button
                        onClick={() => changeRole(u, true)}
                        className="bg-[#F4EBD3] border-2 border-[#c9bfa8] hover:bg-[#DED3C4] text-[#2a2a2a] font-semibold text-sm px-4 py-2 rounded-xl transition-colors shadow-sm"
                      >
                        Promote
                      </button>
                    ) : (
                      <button
                        onClick={() => changeRole(u, false)}
                        className="bg-red-50 border-2 border-red-200 hover:bg-red-100 text-red-700 font-semibold text-sm px-4 py-2 rounded-xl transition-colors shadow-sm"
                      >
                        Demote
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="px-6 py-10 text-center text-gray-500">No users found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// Statistics tab
function Statistics() {
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/auth/admin/users`, { headers: authHeaders() });
      if (!res.ok) throw new Error(`Failed to load statistics (${res.status})`);
      const data = await res.json();
      setUsers(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const filtered = users.filter(u =>
    u.username.toLowerCase().includes(query.toLowerCase()) ||
    u.email.toLowerCase().includes(query.toLowerCase())
  );

  const totalAnnotations = filtered.reduce((s, u) => s + (u.stats?.total_annotations ?? 0), 0);
  const totalTimeMins = filtered.reduce((s, u) => s + (u.stats?.total_time_minutes ?? 0), 0);
  const avgSession = filtered.length
    ? Math.round(filtered.reduce((s, u) => s + (u.stats?.avg_session_time_minutes ?? 0), 0) / filtered.length)
    : 0;

  const summaryCards = [
    { label: 'Total Users', value: filtered.length },
    { label: 'Total Annotations', value: totalAnnotations },
    { label: 'Total Time', value: fmtMins(totalTimeMins) },
    { label: 'Avg Session', value: `${avgSession}m` },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-[#F4EBD3]">User Statistics</h2>
        <button
          onClick={() => exportCSV(filtered)}
          className="flex items-center gap-2 bg-[#F4EBD3] border-2 border-[#c9bfa8] hover:bg-[#DED3C4] text-[#2a2a2a] font-semibold px-5 py-2.5 rounded-2xl transition-colors shadow-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12v6m0 0l-3-3m3 3l3-3M12 3v9" />
          </svg>
          Export CSV
        </button>
      </div>

      <SearchBar value={query} onChange={setQuery} />

      {loading ? (
        <div className="text-[#F4EBD3] text-center py-12 text-lg">Loading statistics...</div>
      ) : error ? (
        <div className="bg-red-100 text-red-800 rounded-xl px-6 py-4 text-sm font-semibold">
          {error}
          <button onClick={fetchUsers} className="ml-4 underline">Retry</button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {summaryCards.map((c, i) => (
              <div key={i} className="bg-[#F4EBD3] rounded-3xl p-6 text-center shadow-md">
                <p className="text-sm font-bold text-[#525470] mb-2">{c.label}</p>
                <p className="text-4xl font-bold text-[#525470]">{c.value}</p>
              </div>
            ))}
          </div>

          <div className="bg-[#F4EBD3] rounded-2xl shadow-md overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-[#c9bfa8]">
                  {['Username', 'Date Joined', 'Annotations', 'Total Time', 'Avg Session Time'].map(h => (
                    <th key={h} className="text-left px-6 py-4 text-sm font-bold text-[#525470]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((u, i) => (
                  <tr key={u.id} className={`border-b border-[#ddd3bc] ${i % 2 === 0 ? '' : 'bg-[#EDE4CC]'} hover:bg-[#DED3C4] transition-colors`}>
                    <td className="px-6 py-4 font-semibold text-[#2a2a2a]">{u.username}</td>
                    <td className="px-6 py-4 text-[#555]">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-6 py-4 text-[#555]">{u.stats?.total_annotations ?? 0}</td>
                    <td className="px-6 py-4 text-[#555]">{fmtMins(u.stats?.total_time_minutes ?? 0)}</td>
                    <td className="px-6 py-4 text-[#555]">{u.stats?.avg_session_time_minutes ?? 0}m</td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={5} className="px-6 py-10 text-center text-gray-500">No users found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

// Upload Images tab
function exportUploadResultsCSV(results) {
  const headers = ['Filename', 'Upload Status', 'Label', 'Confidence Score', 'Already Existed'];
  const rows = results.map(r => [
    r.filename,
    r.uploaded ? 'Uploaded' : 'Failed',
    r.label || '—',
    r.confidence != null ? (r.confidence * 100).toFixed(1) + '%' : '—',
    r.already_existed ? 'Yes' : 'No',
  ]);
  const csv = [headers, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'upload_results.csv'; a.click();
  URL.revokeObjectURL(url);
}

function UploadImages() {
  const [uploads, setUploads] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [uploadResults, setUploadResults] = useState(null); // null = no results yet
  const [showResults, setShowResults] = useState(false);
  const fileRef = useRef();

  const handleFiles = async (files) => {
    const valid = Array.from(files).filter(f => f.type.startsWith('image/'));
    if (!valid.length) return;

    const previews = valid.map(f => ({
      id: Date.now() + Math.random(),
      name: f.name,
      size: (f.size / 1024).toFixed(1) + ' KB',
      preview: URL.createObjectURL(f),
      status: 'Uploading...',
    }));
    setUploads(prev => [...prev, ...previews]);
    setUploading(true);
    setUploadMsg(null);
    setUploadError(null);
    setUploadResults(null);
    setShowResults(false);

    try {
      const formData = new FormData();
      valid.forEach(f => formData.append('files', f));

      const res = await fetch(`${API_URL}/auth/admin/import-images-file`, {
        method: 'POST',
        headers: authHeaders(),
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');

      const successMap = {};
      (data.results || []).forEach(r => { successMap[r.filename] = r; });
      const failedMap = {};
      (data.failures || []).forEach(r => { failedMap[r.filename] = r; });

      setUploads(prev => prev.map(u => {
        if (successMap[u.name]) {
          const r = successMap[u.name];
          const savedToDB = r.label === 'needs_expert_review' || r.already_existed;
          return { ...u, status: r.already_existed ? 'Already Uploaded' :savedToDB ? 'Uploaded' : 'Not Uploaded' };
        }
        if (failedMap[u.name])  return { ...u, status: 'Failed ✗' };
        return u;
      }));

      // Build unified results array for the results table
      const combined = [
        ...(data.results || []).map(r => ({
          filename: r.filename,
          uploaded: true,
          label: r.label ?? null,
          confidence: r.confidence ?? null,
          already_existed: r.already_existed ?? false,
          reason: r.reason || null,
        })),
        ...(data.failures || []).map(r => ({
          filename: r.filename,
          uploaded: false,
          label: r.label ?? null,
          confidence: r.confidence ?? null,
          already_existed: r.already_existed ?? false,
          reason: r.reason || r.error || null,
        })),
      ];
      setUploadResults(combined);
      setUploadMsg(`Uploaded ${data.uploaded} image(s)${data.failed > 0 ? `, ${data.failed} failed` : ''}.`);
    } catch (e) {
      setUploadError(e.message);
      setUploads(prev => prev.map(u =>
        u.status === 'Uploading...' ? { ...u, status: 'Failed ✗' } : u
      ));
    } finally {
      setUploading(false);
    }
  };

  const remove = (id) => setUploads(prev => prev.filter(u => u.id !== id));

  const uploadDone = !uploading && uploadResults !== null;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-2 text-[#F4EBD3]">Upload Images</h2>
      <p className="text-[#F4EBD3] opacity-80 mb-6">Upload images for annotation sessions.</p>

      {uploadMsg && (
        <div className="mb-4 bg-green-100 text-green-800 rounded-xl px-4 py-3 text-sm font-semibold">{uploadMsg}</div>
      )}
      {uploadError && (
        <div className="mb-4 bg-red-100 text-red-800 rounded-xl px-4 py-3 text-sm font-semibold">{uploadError}</div>
      )}

      <div
        onClick={() => !uploading && fileRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); if (!uploading) handleFiles(e.dataTransfer.files); }}
        className={`border-4 border-dashed rounded-3xl p-12 text-center transition-colors mb-6 ${
          uploading
            ? 'opacity-50 cursor-not-allowed border-[#c9bfa8] bg-[#F4EBD3]'
            : dragging
              ? 'cursor-pointer border-[#6b7a99] bg-[#e5dcc8]'
              : 'cursor-pointer border-[#c9bfa8] bg-[#F4EBD3] hover:bg-[#EDE4CC]'
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={e => handleFiles(e.target.files)}
        />
        <svg className="w-14 h-14 mx-auto mb-4 text-[#98A1BC]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p className="text-lg font-bold text-[#2a2a2a] mb-1">
          {uploading ? 'Uploading to S3...' : 'Drop images here or click to browse'}
        </p>
        <p className="text-sm text-[#777]">Multiple files supported</p>
      </div>

      {/* Post-upload action buttons */}
      {uploadDone && (
        <div className="flex items-center gap-3 mb-8">
          <button
            onClick={() => setShowResults(prev => !prev)}
            className="flex items-center gap-2 bg-[#F4EBD3] border-2 border-[#c9bfa8] hover:bg-[#DED3C4] text-[#2a2a2a] font-semibold px-5 py-2.5 rounded-2xl transition-colors shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-6h13M9 11H3m6 6H3m6-3H3M20 7l-3-3-3 3" />
            </svg>
            {showResults ? 'Hide Upload Results' : 'View Upload Results'}
          </button>
          <button
            onClick={() => exportUploadResultsCSV(uploadResults)}
            className="flex items-center gap-2 bg-[#525470] hover:bg-[#3e3f5a] text-white font-semibold px-5 py-2.5 rounded-2xl transition-colors shadow-sm"
            title="Download results as CSV"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12v6m0 0l-3-3m3 3l3-3M12 3v9" />
            </svg>
            Download CSV
          </button>
        </div>
      )}

      {/* Upload results table */}
      {uploadDone && showResults && (
        <div className="mb-8">
          <h3 className="text-lg font-bold mb-3 text-[#F4EBD3]">Upload Results</h3>
          <div className="bg-[#F4EBD3] rounded-2xl shadow-md overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-[#c9bfa8]">
                  {['Filename', 'Upload Status', 'Model Label', 'Confidence Score'].map(h => (
                    <th key={h} className="text-left px-8 py-4 text-sm font-bold text-[#525470] whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {uploadResults.map((r, i) => (
                  <tr key={i} className={`border-b border-[#ddd3bc] ${i % 2 === 0 ? '' : 'bg-[#EDE4CC]'} hover:bg-[#DED3C4] transition-colors`}>
                    <td className="px-6 py-3 font-semibold text-sm text-[#2a2a2a] max-w-[180px] truncate" title={r.filename}>
                      {r.filename}
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap">
                      {(() => {
                        let message, style;
                        if (r.already_existed) {
                          message ='Image Is Already in Database';
                          style = 'bg-blue-100 text-blue-700';
                        }
                        else if (r.label === 'needs_expert_review') {
                          message ='Image Requires Further Analysis. Uploaded.';
                          style = 'bg-green-100 text-green-700';
                        }
                        else if (r.label === 'does_not_need_expert_review') {
                          message = 'No Further Analysis Needed for Image. Discarded.';
                          style = 'bg-yellow-100 text-yellow-700';
                        }
                        else {
                          message = 'Upload Failed. Please Try Again';
                          style = 'bg-red-100 text-red-700';
                        }
                        return <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${style}`}>{message}</span>;
                      })()}

                    </td>
                    <td className="px-6 py-3 whitespace-nowrap">
                      {r.label ? (
                        <span className="inline-block px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-700">
                          {r.label.replace(/_/g, ' ')}
                        </span>
                      ) : (
                        <span className="text-[#aaa]">—</span>
                      )}
                    </td>
                    <td className="px-6 py-3 text-sm text-[#555]">
                      {r.confidence != null ? (
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-[#ddd3bc] rounded-full overflow-hidden flex-shrink-0">
                            <div
                              className={`h-full rounded-full ${r.confidence >= 0.75 ? 'bg-green-500' : r.confidence >= 0.5 ? 'bg-yellow-400' : 'bg-red-400'}`}
                              style={{ width: `${Math.min(r.confidence * 100, 100)}%` }}
                            />
                          </div>
                          <span className="font-semibold text-[#2a2a2a] whitespace-nowrap">{(r.confidence * 100).toFixed(1)}%</span>
                        </div>
                      ) : (
                        <span className="text-[#aaa]">—</span>
                      )}
                    </td>
                  </tr>
                ))}
                {uploadResults.length === 0 && (
                  <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-500">No results available.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {uploads.length > 0 && (
        <>
          <h3 className="text-lg font-bold mb-4 text-[#F4EBD3]">Images ({uploads.length})</h3>
          <div className="grid grid-cols-4 gap-6">
            {uploads.map(img => (
              <div key={img.id} className="bg-[#F4EBD3] rounded-2xl shadow-md overflow-hidden group relative">
                <div className="relative">
                  <img src={img.preview} alt={img.name} className="w-full h-40 object-cover" />
                  <button
                    onClick={() => remove(img.id)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-7 h-7 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-sm font-bold"
                  >
                    ✕
                  </button>
                </div>
                <div className="p-3">
                  <p className="font-semibold text-sm text-[#2a2a2a] truncate">{img.name}</p>
                  <p className="text-xs text-[#777] mt-0.5">{img.size}</p>
                  <span className={`inline-block mt-2 text-sm font-bold px-2 py-0.5 rounded-full ${
                    img.status === 'Already Uploaded' ? 'bg-blue-100 text-blue-700' :
                    img.status === 'Uploaded'  ? 'bg-green-100 text-green-700' :
                    img.status === 'Not Uploaded' ? 'bg-yellow-100 text-yellow-700' :
                    img.status === 'Failed'    ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {img.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// Main Admin Page
const TABS = ['User Management', 'Statistics', 'Upload Images'];

export default function Admin() {
  const [activeTab, setActiveTab] = useState('User Management');

  return (
    <div className="min-h-screen bg-[#98A1BC] pb-20 md:pb-6">
      <div className="max-w-7xl mx-auto px-4 pt-8 mb-6">
        <div className="flex gap-2 flex-wrap">
          {TABS.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition-colors shadow-sm ${
                activeTab === tab
                  ? 'bg-[#F4EBD3] text-[#525470] shadow-md'
                  : 'bg-[#7f8aab] text-white hover:bg-[#6b7a99]'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4">
        <div className="bg-[#525470] rounded-3xl p-8 shadow-lg">
          {activeTab === 'User Management' && <UserManagement />}
          {activeTab === 'Statistics'      && <Statistics />}
          {activeTab === 'Upload Images'   && <UploadImages />}
        </div>
      </div>
    </div>
  );
}