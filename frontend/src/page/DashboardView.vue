<script setup>
import { 
  Server,
  Activity,
  Users,
  Plus
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'

const router = useRouter()
const goToVerification = () => {
  router.push('/verification')
}
</script>

<template>
  <AppLayout>
    <div :class="$style.pageHeader">
      <div>
        <h1 :class="$style.pageTitle">Tableau de bord </h1>
        <p :class="$style.pageSubtitle">Aperçu et suivi des vérifications système</p>
      </div>
      <button :class="$style.primaryBtn" @click="goToVerification">
        <Plus :size="20" />
        Faire une vérification
      </button>
    </div>

    <div :class="$style.statsGrid">
      <div :class="$style.statCard">
        <div :class="$style.statInfo">
          <span :class="$style.statLabel">Environnements</span>
          <span :class="$style.statValue">4</span>
        </div>
      </div>
      <div :class="$style.statCard">
        <div :class="$style.statInfo">
          <span :class="$style.statLabel">Vérifications (Total)</span>
          <span :class="$style.statValue">120</span>
        </div>
      </div>
      <div :class="$style.statCard">
        <div :class="$style.statInfo">
          <span :class="$style.statLabel">En cours</span>
          <span :class="$style.statValue">3</span>
        </div>
      </div>
      <div :class="$style.statCard">
        <div :class="$style.statInfo">
          <span :class="$style.statLabel">Terminées</span>
          <span :class="$style.statValue">117</span>
        </div>
      </div>
    </div>

    <div :class="$style.bottomGrid">
      <div :class="$style.historySection">
        <h3 :class="$style.sectionTitle">Historique Récent</h3>
        <div :class="$style.tableContainer">
          <table :class="$style.historyTable">
            <thead>
              <tr>
                <th>Date</th>
                <th>Cible</th>
                <th>Auteur</th>
                <th>Conclusion</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>24/10/2026</td>
                <td>Production Principale</td>
                <td>Jean Dupont</td>
                <td style="color: #64748b">Toutes les vérifications sont au vert.</td>
                <td><span :class="[$style.statusBadge, $style.statusSuccess]">Terminé</span></td>
              </tr>
              <tr>
                <td>23/10/2026</td>
                <td>Serveur DB-PROD-01</td>
                <td>Admin</td>
                <td style="color: #64748b">Alerte mémoire haute détectée sur cluster.</td>
                <td><span :class="[$style.statusBadge, $style.statusFailed]">Échoué</span></td>
              </tr>
              <tr>
                <td>22/10/2026</td>
                <td>Application Web</td>
                <td>Jean Dupont</td>
                <td style="color: #64748b">Temps de réponse normaux.</td>
                <td><span :class="[$style.statusBadge, $style.statusSuccess]">Terminé</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style module src="../css/DashboardView.module.css"></style>
