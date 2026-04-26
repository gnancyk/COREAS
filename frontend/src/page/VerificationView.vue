<script setup>
import { ref, computed } from 'vue'
import { CheckCircle, Plus, Globe, ShieldCheck, PlayCircle } from 'lucide-vue-next'
import AppLayout from '../components/AppLayout.vue'

// --- Mock Data ---
const environments = ref([
  { id: 1, name: 'Production', urlCentralParam: 'http://prod.central/param', type: 'Production' },
  { id: 2, name: 'Pré-production', urlCentralParam: 'http://preprod.central/param', type: 'CIE' },
  { id: 3, name: 'Staging', urlCentralParam: 'http://staging.central/param', type: 'SODECI' }
])

// Les checkpoints sont maintenant intégrés directement sous chaque module.
const modulesDisponibles = ref([
  { 
    id: 'm1', name: 'Intégrité Base de données', 
    checkpoints: [
      { id: 'c1', name: 'Vérification de la santé du cluster', needsExtra: false, extraLabel: '', extraValue: '' },
      { id: 'c2', name: 'Tests de cohérence mémoire', needsExtra: true, extraLabel: 'Seuil mémoire (GB)', extraValue: '' },
      { id: 'c3', name: 'Vérification backups', needsExtra: true, extraLabel: 'Chemin dossier backup', extraValue: '' }
    ] 
  },
  { 
    id: 'm2', name: 'Sécurité Réseau', 
    checkpoints: [
      { id: 'c4', name: 'Scan des ports', needsExtra: false, extraLabel: '', extraValue: '' },
      { id: 'c5', name: 'Vérification règles Firewall', needsExtra: true, extraLabel: 'IP à tester', extraValue: '' }
    ] 
  },
  { 
    id: 'm3', name: 'Performances API', 
    checkpoints: [
      { id: 'c6', name: 'Test de charge basique', needsExtra: true, extraLabel: 'Nb Utilisateurs virtuels', extraValue: '1000' },
      { id: 'c7', name: 'Latence des endpoints', needsExtra: false, extraLabel: '', extraValue: '' }
    ] 
  }
])

// --- State ---
const selectedEnvId = ref('')
const selectedModules = ref([])
// selectedCheckpoints -> stocke l'id
const selectedCheckpoints = ref([])

const showAddEnvModal = ref(false)
const newEnv = ref({ name: '', urlCentralParam: '', description: '', type: 'Production' })
const isAddingEnv = ref(false)
const addSuccessMessage = ref('')
const progressValue = ref(0)
const isVerifying = ref(false)

// --- Logic ---
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

const openAddEnvModal = () => {
  showAddEnvModal.value = true
  addSuccessMessage.value = ''
  isAddingEnv.value = false
  progressValue.value = 0
  newEnv.value = { name: '', urlCentralParam: '', description: '', type: 'Production' }
}

const saveNewEnv = () => {
  isAddingEnv.value = true
  addSuccessMessage.value = ''
  simulateProgress(1500, () => {
    isAddingEnv.value = false
    const numParams = Math.floor(Math.random() * 10) + 1
    addSuccessMessage.value = `Environnement enregistré parfaitement avec ${numParams} paramètre(s) issus du centralparam.`
    setTimeout(() => {
      const addedId = Date.now()
      environments.value.push({ id: addedId, ...newEnv.value })
      selectedEnvId.value = addedId 
      showAddEnvModal.value = false
    }, 2000)
  })
}

const selectAllModules = () => {
  if (selectedModules.value.length === modulesDisponibles.value.length) {
    selectedModules.value = []
    selectedCheckpoints.value = []
  } else {
    selectedModules.value = modulesDisponibles.value.map(m => m.id)
    // On sélectionne automatique tous leurs checkpoints
    selectedCheckpoints.value = modulesDisponibles.value.reduce((acc, mod) => {
      return [...acc, ...mod.checkpoints.map(c => c.id)]
    }, [])
  }
}

const isModuleSelected = (mId) => selectedModules.value.includes(mId)
const isCheckpointSelected = (cId) => selectedCheckpoints.value.includes(cId)

const toggleModule = (mId) => {
  const index = selectedModules.value.indexOf(mId)
  if (index !== -1) {
    selectedModules.value.splice(index, 1)
    // Deselect all checkpoints for this module
    const mod = modulesDisponibles.value.find(m => m.id === mId)
    mod.checkpoints.forEach(cp => {
      const cpIndex = selectedCheckpoints.value.indexOf(cp.id)
      if (cpIndex !== -1) selectedCheckpoints.value.splice(cpIndex, 1)
    })
  } else {
    selectedModules.value.push(mId)
  }
}

const launchVerification = () => {
  if (!selectedEnvId.value) return
  isVerifying.value = true
  simulateProgress(2500, () => {
    isVerifying.value = false
    alert("Vérification lancée avec succès pour l'environnement !")
    selectedEnvId.value = ''
    selectedModules.value = []
    selectedCheckpoints.value = []
    progressValue.value = 0
  })
}
</script>

<template>
  <AppLayout>
    <div :class="$style.pageHeader">
      <div>
        <h1 :class="$style.pageTitle">Nouvelle Vérification</h1>
        <p :class="$style.pageSubtitle">Configurez et lancez une nouvelle vérification système</p>
      </div>
    </div>

    <div :class="$style.verificationCard">
      <!-- 1. Selection Environnement -->
      <section :class="$style.sectionBlock">
        <h2 :class="$style.blockTitle">
          <Globe :size="20" /> 1. Choix de l'environnement
        </h2>
        <div :class="$style.envSelectionRow">
          <select v-model="selectedEnvId" :class="$style.envSelect">
            <option value="" disabled>-- Sélectionnez un environnement --</option>
            <option v-for="env in environments" :key="env.id" :value="env.id">
              {{ env.name }}
            </option>
          </select>
          <span :class="$style.orText">ou</span>
          <button @click="openAddEnvModal" :class="$style.secondaryBtn">
            <Plus :size="18" /> Créer un environnement
          </button>
        </div>
      </section>

      <!-- 2. Configuration des modules (Affiche si un env est choisi) -->
      <transition name="fade">
        <div v-if="selectedEnvId">
          <hr :class="$style.divider" />
          <section :class="$style.sectionBlock">
            <div :class="$style.blockTitleRow">
              <h2 :class="$style.blockTitle">
                <ShieldCheck :size="20" /> 2. Configuration de l'analyse
              </h2>
              <button @click="selectAllModules" :class="$style.actionBtn">
                Tout sélectionner
              </button>
            </div>
            
            <div :class="$style.modulesList">
              <div 
                v-for="mod in modulesDisponibles" 
                :key="mod.id" 
                :class="[$style.moduleWrapper, { [$style.moduleWrapperActive]: isModuleSelected(mod.id) }]"
              >
                <!-- Module Header -->
                <div :class="$style.moduleHeader" @click="toggleModule(mod.id)">
                  <span :class="$style.customCheckbox"></span>
                  <span :class="$style.moduleName">{{ mod.name }}</span>
                </div>

                <!-- Checkpoints / Sous-sections -->
                <div v-if="isModuleSelected(mod.id)" :class="$style.checkpointsArea">
                  <div v-for="cp in mod.checkpoints" :key="cp.id" :class="$style.checkpointRow">
                    <label :class="$style.checkpointLabel">
                      <input type="checkbox" :value="cp.id" v-model="selectedCheckpoints" />
                      <span>{{ cp.name }}</span>
                    </label>
                    
                    <div v-if="cp.needsExtra && isCheckpointSelected(cp.id)" :class="$style.extraInputBox">
                      <label>{{ cp.extraLabel }}</label>
                      <input type="text" v-model="cp.extraValue" placeholder="..." />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <div :class="$style.verificationFooter">
            <div v-if="isVerifying" :class="$style.progressContainer">
              <div :class="$style.progressBar" :style="{ width: progressValue + '%' }"></div>
              <span :class="$style.progressText">Lancement des tests...</span>
            </div>
            
            <button 
              @click="launchVerification" 
              :class="$style.primaryBtn" 
              :disabled="selectedCheckpoints.length === 0 || isVerifying"
            >
              <PlayCircle :size="20" /> 
              {{ isVerifying ? 'Vérification en cours...' : 'Vérifier' }}
            </button>
          </div>
        </div>
      </transition>
    </div>

    <!-- Modale Ajout Environnement (Identique à EnvironnementView) -->
    <Teleport to="body">
      <div v-if="showAddEnvModal" :class="$style.modalBackdrop">
        <div :class="$style.modal">
          <h3 :class="$style.modalTitle">Créer un environnement</h3>
          
          <div v-if="addSuccessMessage" :class="$style.successBox">
            <CheckCircle :size="28" :class="$style.successIcon" />
            <p>{{ addSuccessMessage }}</p>
          </div>

          <form v-else @submit.prevent="saveNewEnv" :class="$style.modalForm">
            <div :class="$style.formGroup">
              <label>Nom</label>
              <input v-model="newEnv.name" type="text" placeholder="Ex: Production" required :disabled="isAddingEnv" />
            </div>
            <div :class="$style.formGroup">
              <label>URL Central Param</label>
              <input v-model="newEnv.urlCentralParam" type="url" placeholder="http://..." required :disabled="isAddingEnv" />
            </div>
            <div :class="$style.formGroup">
              <label>Description</label>
              <textarea v-model="newEnv.description" rows="3" placeholder="Brève description..." :disabled="isAddingEnv"></textarea>
            </div>
            
            <div v-if="isAddingEnv" :class="$style.miniProgressContainer">
              <div :class="$style.miniProgressBar" :style="{ width: progressValue + '%' }"></div>
            </div>

            <div :class="$style.modalActions">
              <button type="button" :class="$style.btnCancel" @click="showAddEnvModal = false" :disabled="isAddingEnv">Annuler</button>
              <button type="submit" :class="$style.btnSubmit" :disabled="isAddingEnv">
                {{ isAddingEnv ? 'Enregistrement...' : 'Okay' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<style module src="../css/VerificationView.module.css"></style>
