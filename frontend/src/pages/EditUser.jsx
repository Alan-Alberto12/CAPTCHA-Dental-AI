import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

export default function EditUser() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: ''
  });

  // Fetch current user data
  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setFormData({
            email: userData.email || '',
            username: userData.username || '',
            first_name: userData.first_name || '',
            last_name: userData.last_name || ''
          });
        } else {
          localStorage.removeItem('token');
          navigate('/login');
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
        setError('Failed to load user data');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUpdating(true);
    setError('');
    setSuccess('');

    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/editUser', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSuccess('Profile updated successfully!');
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating user:', error);
      setError('An error occurred while updating your profile');
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#98A1BC]">
      <Header />
        <div className="fixed inset-0 flex justify-center items-center">
          <div className="flex flex-col gap-4 w-150 p-6 bg-[#555879] rounded-xl shadow-lg">
            <h2 className="text-center text-3xl font-bold text-[#F4EBD3]">Enter Information to Update</h2>

            {error && (
              <div className="p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="p-2 bg-green-100 border border-green-400 text-green-700 rounded text-sm">
                {success}
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="border p-2 rounded text-[#555879] bg-[#F4EBD3]"
                  placeholder="Update Email"
                  required
                />
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="border p-2 rounded text-[#555879] bg-[#F4EBD3]"
                  placeholder="Update Username"
                  required
                  minLength={3}
                  maxLength={50}
                />
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="border p-2 rounded text-[#555879] bg-[#F4EBD3]"
                  placeholder="Update First Name"
                />
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="border p-2 rounded text-[#555879] bg-[#F4EBD3]"
                  placeholder="Update Last Name"
                />

                <button
                  type="submit"
                  disabled={updating}
                  className="border p-2 rounded-xl bg-[#F4EBD3] text-[#555879] font-bold hover:bg-[#D4C4A8] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {updating ? 'Saving...' : 'Save'}
                </button>
            </form>
          </div>
        </div>
    </div>
  )
}
