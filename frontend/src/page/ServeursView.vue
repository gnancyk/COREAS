<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { Plus, Server, Trash2, CheckCircle, ChevronDown } from 'lucide-vue-next'
import AppLayout from '../components/AppLayout.vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const serveurs = ref([])
const environnements = ref([])

onMounted(async () => {
  await fetchEnvironnements()
  await fetchServeurs()
})

const fetchEnvironnements = async () => {
    try {
        const res = await axios.get(`${API_URL}/environnements/`)
        environnements.value = res.data.map(e => ({ id: e.environnement_id, name: e.nom }))
    } catch(e) {
        console.error("Erreur environnements:", e)
    }
}

const fetchServeurs = async () => {
    try {
        const res = await axios.get(`${API_URL}/environnements/serveurs`)
        serveurs.value = res.data.map(srv => ({
            id: srv.serveur_id,
            name: srv.nom_serveur,
            ip: srv.adresse_ip || srv.nom_hote || 'N/A',
            username: srv.identifiant || '',
            password: srv.mot_de_passe || '',
            description: srv.description || '',
            type: srv.role ? srv.role.nom : 'Autre',
            env_id: srv.environnement_id
        }))
    } catch(e) {
        console.error("Erreur serveurs:", e)
    }
}

const openEnvironments = ref(new Set())
const toggleEnv = (key) => {
  const newSet = new Set(openEnvironments.value)
  if(newSet.has(key)) newSet.delete(key)
  else newSet.add(key)
  openEnvironments.value = newSet
}

const serveursGroupedByEnv = computed(() => {
  const groups = {}
  environnements.value.forEach(env => {
    groups[env.id] = { name: env.name, serveurs: [] }
  })
  groups['Autre'] = { name: 'Autre (Non assigné)', serveurs: [] }
  
  serveurs.value.forEach(srv => {
    if (srv.env_id && groups[srv.env_id]) {
        groups[srv.env_id].serveurs.push(srv)
    } else {
        groups['Autre'].serveurs.push(srv)
    }
  })

  return groups
})

// Progress utility
const progressValue = ref(0)
const simulateProgress = (duration, onComplete) => {
  progressValue.value = 0
  const interval = 50
  const step = 100 / (duration / interval)
  const timer = setInterval(() => {
    progressValue.value += step
    if (progressValue.value >= 100) {
      clearInterval(timer)
      progressValue.value = 100
      onComplete()
    }
  }, interval)
}

// Add Modal State
const showAddModal = ref(false)
const newSrv = ref({ name: '', ip: '', username: '', password: '', description: '', type: 'Web' })
const isAdding = ref(false)
const addSuccessMessage = ref('')

// Info/Edit Modal State
const showInfoModal = ref(false)
const selectedSrv = ref(null)
const isEditing = ref(false)
const isUpdating = ref(false)
const updateSuccessMessage = ref('')

const deleteSrv = async (id) => {
  if (confirm('Confirmer la suppression de ce serveur ?')) {
    try {
      await axios.delete(`${API_URL}/environnements/serveurs/${id}`)
      serveurs.value = serveurs.value.filter(s => s.id !== id)
    } catch (err) {
      alert(err.response?.data?.detail || 'Erreur lors de la suppression.')
    }
  }
}

const openAddModal = () => {
  showAddModal.value = true
  addSuccessMessage.value = ''
  isAdding.value = false
  progressValue.value = 0
  newSrv.value = { name: '', ip: '', username: '', password: '', description: '', type: 'Base de données' }
}

const saveNewSrv = () => {
  isAdding.value = true
  addSuccessMessage.value = ''
  
  simulateProgress(1500, () => {
    isAdding.value = false
    addSuccessMessage.value = `Serveur ajouté avec succès.`
    
    setTimeout(() => {
      serveurs.value.push({
        id: Date.now(),
        ...newSrv.value
      })
      showAddModal.value = false
    }, 2000)
  })
}

const openInfoModal = (srv) => {
  selectedSrv.value = { ...srv }
  isEditing.value = false
  isUpdating.value = false
  updateSuccessMessage.value = ''
  progressValue.value = 0
  showInfoModal.value = true
}

const updateSrv = () => {
  isUpdating.value = true
  updateSuccessMessage.value = ''
  
  simulateProgress(1200, () => {
    isUpdating.value = false
    updateSuccessMessage.value = 'Informations mises à jour !'
    const index = serveurs.value.findIndex(s => s.id === selectedSrv.value.id)
    if(index !== -1) {
      serveurs.value[index] = { ...selectedSrv.value }
    }
    
    setTimeout(() => {
      showInfoModal.value = false
    }, 1500)
  })
}
</script>

<template>
  <AppLayout>
    <div :class="$style.pageHeader">
      <div>
        <h1 :class="$style.pageTitle">Serveurs</h1>
        <p :class="$style.pageSubtitle">Inventaire et gestion de l'infrastructure serveurs</p>
      </div>
      <button :class="$style.primaryBtn" @click="openAddModal">
        <Plus :size="20" /> Ajouter un serveur
      </button>
    </div>

    <!-- Srv List Grouped -->
    <div v-if="serveurs.length === 0" :class="$style.emptyState">
      Aucun serveur configuré.
    </div>

    <div v-else :class="$style.groupedListWrapper">
      <div v-for="(group, key) in serveursGroupedByEnv" :key="key" :class="$style.groupSection">
        <div :class="$style.groupHeader" @click="toggleEnv(key)">
          <h3 :class="$style.groupTitle">{{ group.name }} ({{ group.serveurs.length }})</h3>
          <ChevronDown :class="[$style.chevronIcon, { [$style.rotatedIcon]: openEnvironments.has(key) }]" :size="20"/>
        </div>
        
        <div v-show="openEnvironments.has(key)" :class="$style.listContainer">
          <!-- Si la liste est vide -->
          <div v-if="group.serveurs.length === 0" :class="$style.emptyStateMini">
             Aucun serveur dans ce groupe.
          </div>
          <div 
            v-for="srv in group.serveurs" 
            :key="srv.id" 
            :class="$style.envItem" 
            @click="openInfoModal(srv)"
          >
            <div :class="$style.envInfo">
              <div :class="$style.envIconWrapper">
                <Server :size="20" :class="$style.envIcon" />
              </div>
              <div :class="$style.envText">
                <span :class="$style.envName">{{ srv.name }}</span>
                <span :class="$style.envDesc">{{ srv.ip }} - Type: {{ srv.type }}</span>
              </div>
            </div>
            <button :class="$style.deleteBtn" @click.stop="deleteSrv(srv.id)" title="Supprimer">
              <Trash2 :size="18" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" :class="$style.modalBackdrop">
        <div :class="$style.modal">
          <h3 :class="$style.modalTitle">Ajouter un serveur</h3>
          
          <div v-if="addSuccessMessage" :class="$style.successBox">
            <CheckCircle :size="28" :class="$style.successIcon" />
            <p>{{ addSuccessMessage }}</p>
          </div>

          <form v-else @submit.prevent="saveNewSrv" :class="$style.modalForm">
            <div :class="$style.formGroupRow">
              <div :class="$style.formGroup">
                <label>Nom du Serveur</label>
                <input v-model="newSrv.name" type="text" placeholder="Ex: DB-PROD-01" required :disabled="isAdding" />
              </div>
              <div :class="$style.formGroup">
                <label>Type</label>
                <select v-model="newSrv.type" required :disabled="isAdding">
                  <option value="Base de données">Base de données</option>
                  <option value="Messagerie">Messagerie</option>
                  <option value="Web">Web</option>
                  <option value="Applicatif">Applicatif</option>
                  <option value="Autre">Autre</option>
                </select>
              </div>
            </div>

            <div :class="$style.formGroup">
              <label>Adresse IP</label>
              <input v-model="newSrv.ip" type="text" placeholder="192.168..." required :disabled="isAdding" />
            </div>

            <div :class="$style.formGroupRow">
              <div :class="$style.formGroup">
                <label>Nom d'utilisateur</label>
                <input v-model="newSrv.username" type="text" placeholder="root" required :disabled="isAdding" />
              </div>
              <div :class="$style.formGroup">
                <label>Mot de passe</label>
                <input v-model="newSrv.password" type="password" placeholder="***" required :disabled="isAdding" />
              </div>
            </div>

            <div :class="$style.formGroup">
              <label>Description</label>
              <textarea v-model="newSrv.description" rows="3" placeholder="Brève description..." :disabled="isAdding"></textarea>
            </div>
            
            <div v-if="isAdding" :class="$style.progressContainer">
              <div :class="$style.progressBar" :style="{ width: progressValue + '%' }"></div>
            </div>

            <div :class="$style.modalActions">
              <button type="button" :class="$style.btnCancel" @click="showAddModal = false" :disabled="isAdding">Annuler</button>
              <button type="submit" :class="$style.btnSubmit" :disabled="isAdding">
                {{ isAdding ? 'Enregistrement...' : 'Okay' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Info/Edit Modal -->
    <Teleport to="body">
      <div v-if="showInfoModal" :class="$style.modalBackdrop" @click.self="showInfoModal = false">
        <div :class="$style.modal">
          <h3 :class="$style.modalTitle">
            {{ isEditing ? 'Modifier le serveur' : 'Détails du serveur' }}
          </h3>
          
          <div v-if="updateSuccessMessage" :class="$style.successBox">
            <CheckCircle :size="28" :class="$style.successIcon" />
            <p>{{ updateSuccessMessage }}</p>
          </div>

          <div v-else :class="$style.modalForm">
            <div :class="$style.formGroupRow">
              <div :class="$style.formGroup">
                <label>Nom du Serveur</label>
                <input v-model="selectedSrv.name" type="text" :disabled="!isEditing || isUpdating" />
              </div>
              <div :class="$style.formGroup">
                <label>Type</label>
                <select v-model="selectedSrv.type" :disabled="!isEditing || isUpdating">
                  <option value="Base de données">Base de données</option>
                  <option value="Messagerie">Messagerie</option>
                  <option value="Web">Web</option>
                  <option value="Applicatif">Applicatif</option>
                  <option value="Autre">Autre</option>
                </select>
              </div>
            </div>

            <div :class="$style.formGroup">
              <label>Adresse IP</label>
              <input v-model="selectedSrv.ip" type="text" :disabled="!isEditing || isUpdating" />
            </div>

            <div :class="$style.formGroupRow">
              <div :class="$style.formGroup">
                <label>Nom d'utilisateur</label>
                <input v-model="selectedSrv.username" type="text" :disabled="!isEditing || isUpdating" />
              </div>
              <div :class="$style.formGroup">
                <label>Mot de passe</label>
                <!-- For security mock, password acts like standard inputs -->
                <input v-model="selectedSrv.password" type="password" :disabled="!isEditing || isUpdating" />
              </div>
            </div>

            <div :class="$style.formGroup">
              <label>Description</label>
              <textarea v-model="selectedSrv.description" rows="3" :disabled="!isEditing || isUpdating"></textarea>
            </div>

            <div v-if="isUpdating" :class="$style.progressContainer">
              <div :class="$style.progressBar" :style="{ width: progressValue + '%' }"></div>
            </div>
            
            <div :class="$style.modalActions">
              <template v-if="!isEditing">
                <button type="button" :class="$style.btnCancel" @click="showInfoModal = false">Okay</button>
                <button type="button" :class="$style.btnEdit" @click="isEditing = true">Modifier</button>
              </template>
              <template v-else>
                <button type="button" :class="$style.btnCancel" @click="isEditing = false; openInfoModal(serveurs.find(e => e.id === selectedSrv.id))" :disabled="isUpdating">Annuler</button>
                <button type="button" :class="$style.btnSubmit" @click="updateSrv" :disabled="isUpdating">Valider</button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<style module src="../css/ServeursView.module.css"></style>
