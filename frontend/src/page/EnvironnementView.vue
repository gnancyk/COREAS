<script setup>
import { ref, computed } from 'vue'
import { Plus, Globe, Trash2, CheckCircle } from 'lucide-vue-next'
import AppLayout from '../components/AppLayout.vue'

const environments = ref([
  { id: 1, name: 'Production Principale', urlCentralParam: 'http://prod.central/param', description: 'Environnement de production critique', type: 'Production' },
  { id: 2, name: 'CIE Test', urlCentralParam: 'http://preprod.central/param', description: 'Environnement de test', type: 'CIE' },
  { id: 3, name: 'SODECI Recette', urlCentralParam: 'http://staging.central/param', description: 'Validation QA', type: 'SODECI' }
])

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
      onComplete()
    }
  }, interval)
}

// Add Modal State
const showAddModal = ref(false)
const newEnv = ref({ name: '', urlCentralParam: '', description: '', type: 'Production' })
const isAdding = ref(false)
const addSuccessMessage = ref('')

// ... etc rest of logic unmodified
const showInfoModal = ref(false)
const selectedEnv = ref(null)
const isEditing = ref(false)
const isUpdating = ref(false)
const updateSuccessMessage = ref('')

const deleteEnv = (id) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cet environnement ?')) {
    environments.value = environments.value.filter(e => e.id !== id)
  }
}

const openAddModal = () => {
  showAddModal.value = true
  addSuccessMessage.value = ''
  isAdding.value = false
  progressValue.value = 0
  newEnv.value = { name: '', urlCentralParam: '', description: '', type: 'Production' }
}

const saveNewEnv = () => {
  isAdding.value = true
  addSuccessMessage.value = ''
  
  simulateProgress(1500, () => {
    isAdding.value = false
    const numParams = Math.floor(Math.random() * 10) + 1
    addSuccessMessage.value = `Environnement enregistré parfaitement avec ${numParams} paramètre(s) issus du centralparam.`
    
    setTimeout(() => {
      environments.value.push({
        id: Date.now(),
        ...newEnv.value
      })
      showAddModal.value = false
    }, 2000)
  })
}

const openInfoModal = (env) => {
  selectedEnv.value = { ...env }
  isEditing.value = false
  isUpdating.value = false
  updateSuccessMessage.value = ''
  progressValue.value = 0
  showInfoModal.value = true
}

const updateEnv = () => {
  isUpdating.value = true
  updateSuccessMessage.value = ''
  
  simulateProgress(1200, () => {
    isUpdating.value = false
    updateSuccessMessage.value = 'Modification valable !'
    const index = environments.value.findIndex(e => e.id === selectedEnv.value.id)
    if(index !== -1) {
      environments.value[index] = { ...selectedEnv.value }
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

          <form v-else @submit.prevent="saveNewEnv" :class="$style.modalForm">
            <div :class="$style.formGroup">
              <label>Nom</label>
              <input v-model="newEnv.name" type="text" placeholder="Ex: Production" required :disabled="isAdding" />
            </div>
            <div :class="$style.formGroup">
              <label>Type / Groupe</label>
              <select v-model="newEnv.type" required :disabled="isAdding">
                <option value="Production">Production</option>
                <option value="CIE">CIE</option>
                <option value="SODECI">SODECI</option>
                <option value="Autre">Autre</option>
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
