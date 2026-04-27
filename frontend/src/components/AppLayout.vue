<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { logoutUser } from '../api/auth'
import { 
  Server,
  Settings, 
  LogOut, 
  Bell, 
  Search,
  CheckCircle,
  Clock,
  Layers,
  Globe,
  ChevronDown,
  Moon,
  Sun
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

// L'utilisateur connecté et formattage
const userStr = localStorage.getItem('user')
const userObj = userStr ? JSON.parse(userStr) : null
const userNameDisplay = userObj ? (userObj.nom_complet || userObj.username || 'Utilisateur') : 'Admin'
const userEmailDisplay = userObj ? (userObj.email || '') : 'admin@gs2e.ci'
const userInitials = userNameDisplay.substring(0, 2).toUpperCase()

const handleLogout = async () => {
  await logoutUser()
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

// User Profile dropdown
const showProfileMenu = ref(false)
const toggleProfile = () => {
  showProfileMenu.value = !showProfileMenu.value
  showNotifMenu.value = false
}

// Notifications dropdown
const showNotifMenu = ref(false)
const notifications = ref([
  { id: 1, text: "La vérification 'PROD-01' a échoué.", time: "Il y a 10 min", read: false },
  { id: 2, text: "Mise à jour du serveur réussie.", time: "Il y a 1 heure", read: false },
  { id: 3, text: "Nouveau module ajouté.", time: "Hier", read: true }
])
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const toggleNotif = () => {
  showNotifMenu.value = !showNotifMenu.value
  showProfileMenu.value = false
}

const markAsRead = (id) => {
  const n = notifications.value.find(n => n.id === id)
  if(n) n.read = true
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}

// Settings modal
const showSettingsModal = ref(false)
const isDarkMode = ref(false)

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  if(isDarkMode.value) {
    document.body.dataset.theme = 'dark'
    // This is where CSS variables would apply
  } else {
    document.body.removeAttribute('data-theme')
  }
}

// Global click handler to close dropdowns
const closeDropdowns = (e) => {
  if (!e.target.closest(`[data-dropdown]`)) {
    showProfileMenu.value = false
    showNotifMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdowns)
})
onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns)
})
</script>

<template>
  <div :class="$style.dashboardContainer">
    <!-- Sidebar -->
    <aside :class="$style.sidebar">
      <div :class="$style.brand">
        <div :class="$style.brandHeader">
          <div :class="$style.brandLogoTitle">
            <img src="../assets/gs2e_logo2.webp" alt="GS2E" :class="$style.logoGs2e" />
            <div :class="$style.brandTitle">
              <h2>COREAS</h2>
            </div>
          </div>
          
          <div :class="$style.brandNotifWrapper" data-dropdown="notifications">
            <button :class="$style.brandNotifBtn" @click="toggleNotif">
              <Bell :size="20" />
              <span v-if="unreadCount > 0" :class="$style.brandBadge">{{ unreadCount }}</span>
            </button>
            <div v-if="showNotifMenu" :class="[$style.dropdownMenu, $style.notifMenuDropdown]">
              <div :class="$style.dropdownHeader">
                <h4>Notifications</h4>
                <button v-if="unreadCount > 0" @click="markAllAsRead" :class="$style.textBtn">Tout marquer comme lu</button>
              </div>
              <div :class="$style.dropdownList">
                <div 
                  v-for="notif in notifications" 
                  :key="notif.id" 
                  :class="[$style.dropdownItem, { [$style.unreadItem]: !notif.read }]" 
                  @click="markAsRead(notif.id)"
                >
                  <p>{{ notif.text }}</p>
                  <small>{{ notif.time }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <nav :class="$style.navMenu">
        <!-- The user considers Dashboard = Accueil, but let's map Dashboard -> Accueil and Environnement as requested -->
        <router-link to="/dashboard" :class="[$style.navLink, { [$style.active]: route.path === '/dashboard' }]">
          <Globe :size="20" /> Accueil
        </router-link>
        <router-link to="/environnement" :class="[$style.navLink, { [$style.active]: route.path === '/environnement' }]">
          <Layers :size="20" /> Environnement
        </router-link>
        <router-link to="/fonctionnalite" :class="[$style.navLink, { [$style.active]: route.path === '/fonctionnalite' }]">
          <Layers :size="20" /> Fonctionnalité
        </router-link>
        <router-link to="/serveurs" :class="[$style.navLink, { [$style.active]: route.path === '/serveurs' }]">
          <Server :size="20" /> Serveurs
        </router-link>
        <router-link to="/verification" :class="[$style.navLink, { [$style.active]: route.path === '/verification' }]">
          <CheckCircle :size="20" /> Vérification
        </router-link>
        <a href="#" :class="$style.navLink">
          <Clock :size="20" /> Historique
        </a>
      </nav>

      <div :class="$style.sidebarFooter">
        <div :class="$style.dropdownWrapper" data-dropdown="profile">
          <div :class="$style.profileWidget" @click="toggleProfile">
            <div :class="$style.profileWidgetAvatar">{{ userInitials }}</div>
            <div :class="$style.profileWidgetInfo">
              <span :class="$style.userName">{{ userNameDisplay }}</span>
              <small :class="$style.userEmail">{{ userEmailDisplay }}</small>
            </div>
            <ChevronDown :size="16" />
          </div>

          <div v-if="showProfileMenu" :class="[$style.dropdownMenu, $style.profileMenuUp]">
            <div :class="$style.profileCard">
              <div :class="$style.profileAvatarLg">{{ userInitials }}</div>
              <div :class="$style.profileInfo">
                <strong>{{ userNameDisplay }}</strong>
                <span>Agent</span>
                <small v-if="userEmailDisplay">{{ userEmailDisplay }}</small>
              </div>
            </div>
            <hr :class="$style.dropdownDivider" />
            <button @click.prevent="showSettingsModal = true" :class="[$style.menuBtn, $style.safeBtn]">
              <Settings :size="16" /> Paramètres d'apparence
            </button>
            <hr :class="$style.dropdownDivider" />
            <button @click="handleLogout" :class="[$style.menuBtn, $style.dangerBtn]">
              <LogOut :size="16" /> Déconnexion
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main :class="$style.mainContent">
      <div :class="$style.contentArea">
        <slot />
      </div>
      
      <!-- Settings Modal -->
      <Teleport to="body">
        <div v-if="showSettingsModal" :class="$style.modalBackdrop" @click.self="showSettingsModal = false">
          <div :class="$style.modal">
            <h3 :class="$style.settingsTitle"><Settings :size="20" /> Paramètres d'apparence</h3>
            
            <div :class="$style.settingsRow">
              <div :class="$style.settingsText">
                <strong>Mode sombre</strong>
                <p>Basculer l'interface en thème sombre</p>
              </div>
              <div :class="$style.toggleSwitch" @click="toggleDarkMode" :data-active="isDarkMode">
                <div :class="$style.toggleKnob"></div>
              </div>
            </div>

            <div :class="$style.modalActions">
              <button @click="showSettingsModal = false" :class="$style.primaryBtn">Fermer</button>
            </div>
          </div>
        </div>
      </Teleport>
    </main>
  </div>
</template>

<style module src="./AppLayout.module.css"></style>
