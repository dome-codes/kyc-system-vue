<script setup lang="ts">
import KycInputForm from '@/components/forms/KycInputForm.vue'
import KycReportPopup from '@/components/reports/KycReportPopup.vue'
import { useKycStore } from '@/stores/kyc'
import type { KycQuestion, KycReport } from '@/types/kyc'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const kycStore = useKycStore()
const router = useRouter()

const isReportPopupOpen = ref(false)
const formResetTrigger = ref(0)

const handleFormSubmit = async (entity: string, questions: KycQuestion[], land?: string, branche?: string) => {
  try {
    await kycStore.createReport(entity, questions, land, branche)
    isReportPopupOpen.value = true
  } catch (error) {
    // Error handling
  }
}

const handleReportConfirm = (report: KycReport) => {
  kycStore.confirmReport(report)
  isReportPopupOpen.value = false
  formResetTrigger.value++
}

const handleReportCancel = () => {
  isReportPopupOpen.value = false
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-8">
            <!-- Logo Container - Default KYC Logo (SVG) -->
            <div class="h-12 w-12 rounded-lg flex items-center justify-center shadow-md">
              <!-- Default KYC Logo -->
              <img src="/logo.svg" alt="KYC Logo" class="h-12 w-12 object-contain" />
            </div>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">KYC Quick Check</h1>
              <p class="text-sm text-gray-500">Unternehmensrecherche</p>
            </div>
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <button
              @click="router.push('/reports')"
              class="text-gray-500 hover:text-gray-700 transition-colors underline"
            >
              {{ kycStore.confirmedReports.length }} Berichte abgeschlossen
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex justify-center px-4 py-8">
      <div class="max-w-4xl w-full">
        <div class="mb-8 text-center w-full">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Unternehmensrecherche Quick Check</h2>
          <p class="text-gray-600 mb-8 max-w-3xl mx-auto text-lg leading-relaxed">
            Führen Sie eine schnelle Unternehmensrecherche durch. Geben Sie Unternehmensinformationen ein und
            erhalten Sie einen kompakten Überblick über relevante Daten und Risikobewertungen.
          </p>
        </div>

        <!-- Error Alert -->
        <div v-if="kycStore.error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <svg class="h-4 w-4 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span class="text-red-700">{{ kycStore.error }}</span>
          </div>
        </div>

        <!-- KYC Form -->
        <KycInputForm @submit="handleFormSubmit" :reset-trigger="formResetTrigger" />

      </div>
    </main>

    <!-- Report Popup -->
    <KycReportPopup
      v-if="isReportPopupOpen && kycStore.currentReport"
      :report="kycStore.currentReport"
      @confirm="handleReportConfirm"
      @cancel="handleReportCancel"
    />
  </div>
</template>
