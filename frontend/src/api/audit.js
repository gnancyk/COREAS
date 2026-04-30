import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const auditApi = {
    // Audit Dynamique (Zéro Saisie)
    launchDynamicAudit(envId) {
        return axios.post(`${API_URL}/batch/audit/environnement/${envId}`)
    },

    // Vérification des Services Windows (Zéro Saisie)
    verifyBatchServices(envId) {
        return axios.post(`${API_URL}/batch/services/environnement/${envId}`)
    },

    // Vérification des Services CRM (Zéro Saisie)
    verifyCrmServices(envId) {
        return axios.post(`${API_URL}/crm/services/environnement/${envId}`)
    },

    // Santé HTTP
    verifyHttpHealth(urls) {
        return axios.post(`${API_URL}/batch/http/sante`, urls)
    }
}
