<script setup>
import { ref } from 'vue'
import { Plus, List, Trash2, CheckCircle } from 'lucide-vue-next'
import AppLayout from '../components/AppLayout.vue'

const fonctionnalites = ref([
  { id: 1, name: 'Gestion des rôles', description: 'Permet de configurer les rôles', active: true },
  { id: 2, name: 'Audit', description: 'Surveillance des actions', active: true }
])

</script>

<template>
  <AppLayout>
    <div :class="$style.pageHeader">
      <div>
        <h1 :class="$style.pageTitle">Fonctionnalités</h1>
        <p :class="$style.pageSubtitle">Gestion et configuration des fonctionnalités de l'application</p>
      </div>
      <button :class="$style.primaryBtn">
        <Plus :size="20" /> Ajouter une fonctionnalité
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="fonctionnalites.length === 0" :class="$style.emptyState">
      Aucune fonctionnalité configurée.
    </div>

    <div v-else :class="$style.listContainer">
      <div 
        v-for="item in fonctionnalites" 
        :key="item.id" 
        :class="$style.envItem" 
      >
        <div :class="$style.envInfo">
          <div :class="$style.envIconWrapper">
            <List :size="20" :class="$style.envIcon" />
          </div>
          <div :class="$style.envText">
            <span :class="$style.envName">{{ item.name }}</span>
            <span :class="$style.envDesc">{{ item.description }}</span>
          </div>
        </div>
        <button :class="$style.deleteBtn" title="Supprimer">
          <Trash2 :size="18" />
        </button>
      </div>
    </div>
  </AppLayout>
</template>

<style module src="../css/EnvironnementView.module.css"></style>
