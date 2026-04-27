import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour ajouter le token à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

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
    // On tente d'avertir le backend (blacklist du token)
    await api.post('/auth/logout')
  } catch (e) {
    console.warn("Backend logout failed or token already invalid", e)
  } finally {
    // Quoi qu'il arrive, on vide le stockage local pour déconnecter l'utilisateur
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // Optionnel : rediriger vers /login
    window.location.href = '/login'
  }
}

export default api
