<script setup>
import { ref } from 'vue'
import { LogIn, User, Lock, AlertCircle, CheckCircle } from 'lucide-vue-next'
import { login } from '../api/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')
const success = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Veuillez remplir tous les champs'
    return
  }

  isLoading.value = true
  error.value = ''
  
  try {
    const data = await login(username.value, password.value)
    success.value = true
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data))
    
    setTimeout(() => {
      // Redirection après succès
      console.log('Connexion réussie:', data)
    }, 1500)
  } catch (err) {
    error.value = err
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div :class="$style.loginContainer">
    <div :class="[$style.glassCard, $style.loginCard]">
      <div :class="$style.header">
        <div :class="$style.logoWrapper">
          <LogIn :size="32" :class="$style.primaryIcon" />
        </div>
        <h1 :class="$style.title">Bienvenue</h1>
        <p :class="$style.subtitle">Connectez-vous à votre compte COREAS</p>
      </div>

      <form @submit.prevent="handleLogin" :class="$style.loginForm">
        <div :class="$style.inputGroup">
          <label for="username" :class="$style.inputLabel">Nom d'utilisateur</label>
          <div :class="$style.inputWrapper">
            <User :size="18" :class="$style.fieldIcon" />
            <input 
              id="username" 
              v-model="username" 
              type="text" 
              placeholder="votre.nom"
              :disabled="isLoading"
              :class="$style.inputField"
            />
          </div>
        </div>

        <div :class="$style.inputGroup">
          <label for="password" :class="$style.inputLabel">Mot de passe</label>
          <div :class="$style.inputWrapper">
            <Lock :size="18" :class="$style.fieldIcon" />
            <input 
              id="password" 
              v-model="password" 
              type="password" 
              placeholder="••••••••"
              :disabled="isLoading"
              :class="$style.inputField"
            />
          </div>
        </div>

        <div v-if="error" :class="[$style.statusMsg, $style.errorMsg]">
          <AlertCircle :size="18" />
          <span>{{ error }}</span>
        </div>

        <div v-if="success" :class="[$style.statusMsg, $style.successMsg]">
          <CheckCircle :size="18" />
          <span>Connexion réussie ! Préparation de l'espace...</span>
        </div>

        <button type="submit" :class="$style.btnSubmit" :disabled="isLoading || success">
          <span v-if="!isLoading && !success">Se connecter</span>
          <span v-else-if="isLoading">Connexion en cours...</span>
          <span v-else>Entrée...</span>
        </button>
      </form>

      <div :class="$style.footer">
        <p>© 2026 SaphirV3 - COREAS Infrastructure</p>
      </div>
    </div>
  </div>
</template>

<style module src="./LoginView.module.css"></style>
