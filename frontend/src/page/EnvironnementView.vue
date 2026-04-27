<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { Plus, Globe, Trash2, CheckCircle } from 'lucide-vue-next'
import AppLayout from '../components/AppLayout.vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const environments = ref([])
const categories = ref([])

onMounted(async () => {
    await fetchCategories()
    await fetchEnvironments()
})

const fetchCategories = async () => {
    try {
        const res = await axios.get(`${API_URL}/environnements/categories`)
        categories.value = res.data
    } catch(e) {
        console.error("Erreur chargement categories:", e)
    }
}

const fetchEnvironments = async () => {
    try {
        const res = await axios.get(`${API_URL}/environnements/`)
        environments.value = res.data.map(env => {
            const cat = categories.value.find(c => c.categorie_id === env.categorie_id)
            return {
                id: env.environnement_id,
                name: env.nom,
                urlCentralParam: env.url_central_param,
                description: '',
                type: cat ? cat.nom : 'Autre',
                categorie_id: env.categorie_id
            }
        })
    } catch(e) {
        console.error("Erreur chargement environnements:", e)
    }
}

const groupedEnvironments = computed(() => {
  return environments.value.reduce((groups, env) => {
    const t = env.type || 'Non classé'
    if (!groups[t]) groups[t] = []
    groups[t].push(env)
    return groups
  }, {})
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
      if (onComplete) onComplete()
    }
  }, interval)
}

// Add Modal State
const showAddModal = ref(false)
const newEnv = ref({ name: '', urlCentralParam: '', description: '', categorie_id: '' })
const isAdding = ref(false)
const addSuccessMessage = ref('')
const addErrorMessage = ref('')

const openAddModal = () => {
  showAddModal.value = true
  addSuccessMessage.value = ''
  addErrorMessage.value = ''
  isAdding.value = false
  progressValue.value = 0
  if (categories.value.length > 0) {
     newEnv.value = { name: '', urlCentralParam: '', description: '', categorie_id: categories.value[0].categorie_id }
  } else {
     newEnv.value = { name: '', urlCentralParam: '', description: '', categorie_id: '' }
  }
}

const saveNewEnv = async () => {
  isAdding.value = true
  addSuccessMessage.value = ''
  addErrorMessage.value = ''
  
  try {
     const payload = {
        nom: newEnv.value.name,
        url_central_param: newEnv.value.urlCentralParam,
        categorie_id: newEnv.value.categorie_id
     }
     
     progressValue.value = 50;

     await axios.post(`${API_URL}/environnements/`, payload)
     
     progressValue.value = 100;
     isAdding.value = false;
     addSuccessMessage.value = `Environnement enregistré avec succès !`
     
     await fetchEnvironments()
     
     setTimeout(() => {
        showAddModal.value = false
     }, 1500)
     
  } catch (err) {
     isAdding.value = false
     addErrorMessage.value = err.response?.data?.detail || "Erreur lors de la validation du service : assurez-vous que le CentralParam est WCF valide."
  }
}

const showInfoModal = ref(false)
const selectedEnv = ref(null)
const isEditing = ref(false)
const isUpdating = ref(false)
const updateSuccessMessage = ref('')
const updateErrorMessage = ref('')

const openInfoModal = (env) => {
  selectedEnv.value = { ...env, categorie_id: env.categorie_id }
  isEditing.value = false
  isUpdating.value = false
  updateSuccessMessage.value = ''
  updateErrorMessage.value = ''
  progressValue.value = 0
  showInfoModal.value = true
}

const updateEnv = async () => {
    isUpdating.value = true
    updateSuccessMessage.value = ''
    updateErrorMessage.value = ''
    
    simulateProgress(1000, () => {
        isUpdating.value = false
        updateErrorMessage.value = "Modification non supportée par le backend pour le moment."
    })
}

const deleteEnv = async (id) => {
    if (confirm('La suppression n\'est pas encore supportée par le backend. Simuler localement ?')) {
        environments.value = environments.value.filter(e => e.id !== id)
    }
}
</script>

<template>
  <AppLayout>
    <div :class="$style.pageHeader">
      <div>
        <h1 :class="$style.pageTitle">Environnements</h1>
        <p :class="$style.pageSubtitle">Gérez et consultez les détails de vos environnements</p>
      </div>
      <button :class="$style.primaryBtn" @click="openAddModal">
        <Plus :size="20" /> Ajouter un environnement
      </button>
    </div>

    <!-- Env List Grouped -->
    <div v-if="environments.length === 0" :class="$style.emptyState">
      Aucun environnement configuré.
    </div>

    <div v-else :class="$style.groupedListWrapper">
      <div v-for="(envs, typeGroup) in groupedEnvironments" :key="typeGroup" :class="$style.groupSection">
        <h3 :class="$style.groupTitle">{{ typeGroup }}</h3>
        
        <div :class="$style.listContainer">
          <div 
            v-for="env in envs" 
            :key="env.id" 
            :class="$style.envItem" 
            @click="openInfoModal(env)"
          >
            <div :class="$style.envInfo">
              <div :class="$style.envIconWrapper">
                <Globe :size="20" :class="$style.envIcon" />
              </div>
              <div :class="$style.envText">
                <span :class="$style.envName">{{ env.name }}</span>
                <span :class="$style.envDesc">{{ env.description }}</span>
              </div>
            </div>
            <button :class="$style.deleteBtn" @click.stop="deleteEnv(env.id)" title="Supprimer">
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
          <h3 :class="$style.modalTitle">Ajouter un environnement</h3>
          
          <div v-if="addSuccessMessage" :class="$style.successBox">
            <CheckCircle :size="28" :class="$style.successIcon" />
            <p>{{ addSuccessMessage }}</p>
          </div>
          <div v-if="addErrorMessage" style="color: red; padding: 10px; background: rgba(255,0,0,0.1); border-radius: 4px; margin-bottom: 10px;">
            <p>{{ addErrorMessage }}</p>
          </div>

          <form v-else @submit.prevent="saveNewEnv" :class="$style.modalForm">
            <div :class="$style.formGroup">
              <label>Nom</label>
              <input v-model="newEnv.name" type="text" placeholder="Ex: Production" required :disabled="isAdding" />
            </div>
            <div :class="$style.formGroup">
              <label>Catégorie</label>
              <select v-model="newEnv.categorie_id" required :disabled="isAdding">
                <option v-for="cat in categories" :key="cat.categorie_id" :value="cat.categorie_id">
                    {{ cat.nom }}
                </option>
              </select>
            </div>
            <div :class="$style.formGroup">
              <label>URL Central Param</label>
              <input v-model="newEnv.urlCentralParam" type="url" placeholder="http://..." required :disabled="isAdding" />
            </div>
            <div :class="$style.formGroup">
              <label>Description</label>
              <textarea v-model="newEnv.description" rows="3" placeholder="Brève description..." :disabled="isAdding"></textarea>
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
            {{ isEditing ? 'Modifier l\'environnement' : 'Détails de l\'environnement' }}
          </h3>
          
          <div v-if="updateSuccessMessage" :class="$style.successBox">
            <CheckCircle :size="28" :class="$style.successIcon" />
            <p>{{ updateSuccessMessage }}</p>
          </div>
          <div v-if="updateErrorMessage" style="color: red; padding: 10px; background: rgba(255,0,0,0.1); border-radius: 4px; margin-bottom: 10px;">
            <p>{{ updateErrorMessage }}</p>
          </div>

          <div v-else :class="$style.modalForm">
            <div :class="$style.formGroup">
              <label>Nom</label>
              <input v-model="selectedEnv.name" type="text" :disabled="!isEditing || isUpdating" />
            </div>
            <div :class="$style.formGroup">
              <label>Type / Groupe</label>
              <select v-model="selectedEnv.type" :disabled="!isEditing || isUpdating">
                <option value="Production">Production</option>
                <option value="CIE">CIE</option>
                <option value="SODECI">SODECI</option>
                <option value="Autre">Autre</option>
              </select>
            </div>
            <div :class="$style.formGroup">
              <label>URL Central Param</label>
              <input v-model="selectedEnv.urlCentralParam" type="url" :disabled="!isEditing || isUpdating" />
            </div>
            <div :class="$style.formGroup">
              <label>Description</label>
              <textarea v-model="selectedEnv.description" rows="3" :disabled="!isEditing || isUpdating"></textarea>
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
                <button type="button" :class="$style.btnCancel" @click="isEditing = false; openInfoModal(environments.find(e => e.id === selectedEnv.id))" :disabled="isUpdating">Annuler</button>
                <button type="button" :class="$style.btnSubmit" @click="updateEnv" :disabled="isUpdating">Valider</button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<style module src="../css/EnvironnementView.module.css"></style>
