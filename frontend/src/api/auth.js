import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // À ajuster selon l'URL du backend
  headers: {
    'Content-Type': 'application/json'
  }
})

export const login = async (username, password) => {
  try {
    const response = await api.post('/auth/login', {
      username,
      password
    })
    return response.data
  } catch (error) {
    throw error.response?.data?.detail || "Erreur de connexion au serveur"
  }
}

export const logoutUser = async () => {
    try {
        await api.post('/auth/logout')
    } catch (e) {
        console.warn("Backend logout endpoint failed or not fully implemented, clearing local storage...", e)
    }
}

export default api
