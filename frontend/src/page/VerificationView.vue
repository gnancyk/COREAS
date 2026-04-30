<script setup>
import { ref, computed } from 'vue'
import { CheckCircle, Plus, Globe, ShieldCheck, PlayCircle } from 'lucide-vue-next'
import AppLayout from '../components/AppLayout.vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

import { onMounted } from 'vue'
import axios from 'axios'
import { auditApi } from '../api/audit'

// --- Data ---
const environments = ref([])

// Modules réels SaphirV3
const modulesDisponibles = ref([
  {
    id: 'batch',
    name: 'Audit Batch & SaphirV3',
    checkpoints: [
      { id: 'batch_dynamic', name: 'Audit Dynamique (.config & Pools IIS)' },
      { id: 'batch_services', name: 'Services Windows SAPHIRV3 (État & Comptes)' },
      { id: 'batch_http', name: 'Disponibilité des Services Web (HTTP 200)' }
    ]
  },
  {
    id: 'crm',
    name: 'Microsoft Dynamics CRM',
    checkpoints: [
      { id: 'crm_services', name: 'Services MSCRM (Async & Sandbox)' }
    ]
  },
  {
    id: 'sql',
    name: 'Expertise SQL Server',
    checkpoints: [
      { id: 'sql_orgid', name: 'Cohérence OrganizationID' },
      { id: 'sql_index', name: 'Fragmentation & Index Manquants' },
      { id: 'sql_triggers', name: 'Vérification des Triggers (gs2e_Trg_*)' }
    ]
  }
])

// --- State ---
const selectedEnvId = ref('')
const selectedModules = ref([])
const selectedCheckpoints = ref([])
const auditResults = ref([])

onMounted(async () => {
  try {
    const res = await axios.get(`${API_URL}/environnements/`)
    environments.value = res.data.map(e => ({ id: e.environnement_id, name: e.nom }))
  } catch(e) {
    console.error("Erreur chargement environnements :", e)
  }
})

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
      if (onComplete) onComplete()
    }
  }, interval)
}

const selectAllModules = () => {
  if (selectedModules.value.length === modulesDisponibles.value.length) {
    selectedModules.value = []
    selectedCheckpoints.value = []
  } else {
    selectedModules.value = modulesDisponibles.value.map(m => m.id)
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
    const mod = modulesDisponibles.value.find(m => m.id === mId)
    mod.checkpoints.forEach(cp => {
      const cpIndex = selectedCheckpoints.value.indexOf(cp.id)
      if (cpIndex !== -1) selectedCheckpoints.value.splice(cpIndex, 1)
    })
  } else {
    selectedModules.value.push(mId)
    const mod = modulesDisponibles.value.find(m => m.id === mId)
    mod.checkpoints.forEach(cp => {
      if (!selectedCheckpoints.value.includes(cp.id)) {
        selectedCheckpoints.value.push(cp.id)
      }
    })
  }
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
    addSuccessMessage.value = `Environnement enregistré.`
    setTimeout(async () => {
        showAddEnvModal.value = false
        const res = await axios.get(`${API_URL}/environnements/`)
        environments.value = res.data.map(e => ({ id: e.environnement_id, name: e.nom }))
    }, 1500)
  })
}

const launchVerification = async () => {
  if (!selectedEnvId.value) return
  isVerifying.value = true
  auditResults.value = []
  progressValue.value = 10
  
  try {
    // 1. Appel Audit Dynamique
    if (selectedCheckpoints.value.includes('batch_dynamic')) {
      const res = await auditApi.launchDynamicAudit(selectedEnvId.value)
      auditResults.value.push({
          type: 'Audit Dynamique',
          data: res.data.results
      })
    }
    progressValue.value = 40

    // 2. Appel Services Batch
    if (selectedCheckpoints.value.includes('batch_services')) {
      const res = await auditApi.verifyBatchServices(selectedEnvId.value)
      auditResults.value.push({
          type: 'Services Windows',
          data: res.data.results
      })
    }
    progressValue.value = 70

    // 3. Appel CRM
    if (selectedCheckpoints.value.includes('crm_services')) {
      const res = await auditApi.verifyCrmServices(selectedEnvId.value)
      auditResults.value.push({
          type: 'Services CRM',
          data: res.data.results
      })
    }
    
    progressValue.value = 100
    setTimeout(() => { isVerifying.value = false }, 500)
    
  } catch (err) {
    console.error("Erreur durant l'audit :", err)
    alert("Une erreur est survenue lors du lancement de l'audit.")
    isVerifying.value = false
    progressValue.value = 0
  }
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
              <span :class="$style.progressText">Vérification en cours (Zéro Saisie)...</span>
            </div>
            
            <button 
              @click="launchVerification" 
              :class="$style.primaryBtn" 
              :disabled="(selectedCheckpoints.length === 0 && !isVerifying) || isVerifying"
            >
              <PlayCircle :size="20" /> 
              {{ isVerifying ? 'Analyse en cours...' : 'Lancer l\'Analyse' }}
            </button>
          </div>

          <!-- Section Résultats -->
          <div v-if="auditResults.length > 0" :class="$style.resultsSection">
            <h2 :class="$style.resultsTitle">Résultats de l'Analyse</h2>
            
            <div v-for="(res, idx) in auditResults" :key="idx" :class="$style.resultBlock">
              <h3 :class="$style.resultType">{{ res.type }}</h3>
              
              <div v-if="res.data.length === 0" :class="$style.emptyInfo">
                  Aucune donnée trouvée ou aucun serveur configuré pour cet environnement.
              </div>

              <table v-else :class="$style.resultsTable">
                <thead>
                  <tr>
                    <th>Serveur</th>
                    <th>Détails de l'analyse</th>
                    <th>État</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- Cas Services (Windows / CRM) -->
                  <template v-if="res.type === 'Services Windows' || res.type === 'Services CRM' ">
                    <tr v-for="(srv, sidx) in res.data" :key="sidx">
                      <td :class="$style.tdServer">{{ srv.server || 'Local' }}</td>
                      <td>
                        <div :class="$style.detailMain">{{ srv.display_name }}</div>
                        <div v-if="srv.start_account" :class="$style.detailSub">Compte: {{ srv.start_account }}</div>
                        <div v-if="srv.error_message" :class="$style.errorMessage">{{ srv.error_message }}</div>
                      </td>
                      <td>
                        <span :class="[srv.is_running ? $style.statusOk : $style.statusError]">
                          {{ srv.status }}
                        </span>
                      </td>
                    </tr>
                  </template>
                  
                  <!-- Cas Audit Dynamique -->
                  <template v-else-if="res.type === 'Audit Dynamique'">
                    <tr v-for="(item, iidx) in res.data" :key="iidx">
                      <td :class="$style.tdServer">{{ item.server }}</td>
                      <td>
                        <div v-if="item.is_reachable">
                          <CheckCircle :size="14" style="display:inline; color:#10b981"/> 
                          Configs trouvées: {{ item.configs_found?.length || 0 }} 
                          / Pools IIS: {{ item.iis_pools?.length || 0 }}
                        </div>
                        <div v-if="item.error_message" :class="$style.errorMessage">
                           {{ item.error_message }}
                        </div>
                      </td>
                      <td>
                        <span :class="[item.is_reachable ? $style.statusOk : $style.statusError]">
                          {{ item.is_reachable ? 'Connecté' : 'Erreur WinRM' }}
                        </span>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
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
