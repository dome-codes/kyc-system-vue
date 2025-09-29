<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="border-b border-gray-200 bg-white">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button
              @click="handleBack"
              class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
            </button>
            <div class="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">Interaktiver Fragebogen</h1>
              <p class="text-sm text-gray-500">Erweiterte Fragenauswahl</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <div class="text-center py-12">
          <svg class="h-16 w-16 text-blue-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Interaktiver Fragebogen</h2>
          <p class="text-gray-600 mb-8">
            Diese Seite wird in einer zukünftigen Version erweitert. 
            Verwenden Sie vorerst das Hauptformular für die KYC-Berichterstellung.
          </p>
          <button
            @click="handleBack"
            class="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Zurück zum Hauptformular
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
