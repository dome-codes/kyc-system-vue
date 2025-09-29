<script setup lang="ts">
import type { KycReport } from '@/types/kyc'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  report: KycReport
  onConfirm?: (report: KycReport) => void
  onCancel?: () => void
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  confirm: [report: KycReport]
  cancel: []
}>()

const isEditing = ref(false)
const editableAnswers = ref<Record<string, string>>({})

// Initialize editable answers
editableAnswers.value = { ...props.report.answers }

const getRiskLevel = (answer: string): 'low' | 'medium' | 'high' => {
  const lowerAnswer = answer.toLowerCase()
  if (lowerAnswer.includes('nicht') || lowerAnswer.includes('keine') || lowerAnswer.includes('unbekannt')) {
    return 'high'
  }
  if (lowerAnswer.includes('teilweise') || lowerAnswer.includes('begrenzt')) {
    return 'medium'
  }
  return 'low'
}

const getRiskBadgeClass = (level: 'low' | 'medium' | 'high') => {
  switch (level) {
    case 'low':
      return 'bg-green-100 text-green-800'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800'
    case 'high':
      return 'bg-red-100 text-red-800'
  }
}

const getRiskLabel = (level: 'low' | 'medium' | 'high') => {
  switch (level) {
    case 'low':
      return 'Niedrig'
    case 'medium':
      return 'Mittel'
    case 'high':
      return 'Hoch'
  }
}

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = () => {
  const updatedReport = {
    ...props.report,
    answers: editableAnswers.value
  }
  emit('confirm', updatedReport)
  isEditing.value = false
}

const handleCancel = () => {
  editableAnswers.value = { ...props.report.answers }
  isEditing.value = false
  emit('cancel')
}

const handleDownloadPDF = () => {
  import('@/utils/pdfGenerator').then(({ generateKycReportPDF }) => {
    const reportWithEditableAnswers = {
      ...props.report,
      answers: editableAnswers.value
    }
    generateKycReportPDF(reportWithEditableAnswers)
  })
}

const totalQuestions = computed(() => Object.keys(editableAnswers.value).length)

const navigateToReportOverview = () => {
  router.push(`/report/${props.report.id || 'current'}`)
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[80vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <div class="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-semibold text-gray-900">KYC Compliance Bericht</h2>
            <p class="text-sm text-gray-500">{{ report.entity }}</p>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <button
            @click="handleDownloadPDF"
            class="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Download
          </button>

          <button
            v-if="!isEditing"
            @click="handleEdit"
            class="flex items-center gap-2 px-3 py-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Bearbeiten
          </button>

          <button
            @click="handleCancel"
            class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="overflow-y-auto max-h-[calc(80vh-140px)] p-6">
        <div class="space-y-6">
          <!-- Company Information -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
              Unternehmensinformationen
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Unternehmen</label>
                <p class="text-gray-900">{{ report.entity }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="report.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                  {{ report.status === 'confirmed' ? 'Bestätigt' : 'Ausstehend' }}
                </span>
              </div>
              <div v-if="report.timestamp">
                <label class="block text-sm font-medium text-gray-700 mb-1">Erstellt</label>
                <p class="text-gray-900">{{ new Date(report.timestamp).toLocaleString('de-DE') }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Anzahl Fragen</label>
                <p class="text-gray-900">{{ totalQuestions }}</p>
              </div>
            </div>
          </div>

          <!-- Risk Summary -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              Risiko-Zusammenfassung
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="text-center p-4 bg-green-50 rounded-lg">
                <div class="text-2xl font-bold text-green-600">
                  {{ Object.values(editableAnswers).filter(answer => getRiskLevel(answer) === 'low').length }}
                </div>
                <div class="text-sm text-green-700">Niedrige Risiken</div>
              </div>
              <div class="text-center p-4 bg-yellow-50 rounded-lg">
                <div class="text-2xl font-bold text-yellow-600">
                  {{ Object.values(editableAnswers).filter(answer => getRiskLevel(answer) === 'medium').length }}
                </div>
                <div class="text-sm text-yellow-700">Mittlere Risiken</div>
              </div>
              <div class="text-center p-4 bg-red-50 rounded-lg">
                <div class="text-2xl font-bold text-red-600">
                  {{ Object.values(editableAnswers).filter(answer => getRiskLevel(answer) === 'high').length }}
                </div>
                <div class="text-sm text-red-700">Hohe Risiken</div>
              </div>
            </div>
          </div>

          <!-- Detailed Findings -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              Detaillierte Ergebnisse
            </h3>
            <div class="space-y-4">
              <div
                v-for="(answer, questionId) in editableAnswers"
                :key="questionId"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-start justify-between mb-2">
                  <h4 class="font-medium text-gray-900">{{ questionId }}</h4>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getRiskBadgeClass(getRiskLevel(answer))">
                    {{ getRiskLabel(getRiskLevel(answer)) }}
                  </span>
                </div>
                <div v-if="isEditing">
                  <textarea
                    v-model="editableAnswers[questionId]"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  ></textarea>
                </div>
                <div v-else>
                  <p class="text-gray-700">{{ answer }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Compliance Notes -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Compliance-Hinweise
            </h3>
            <div class="prose max-w-none">
              <p class="text-gray-700">
                Dieser Bericht wurde automatisch generiert basierend auf verfügbaren Datenquellen.
                Bitte überprüfen Sie alle Angaben sorgfältig und ergänzen Sie fehlende Informationen
                bei Bedarf. Bei Fragen oder Unklarheiten wenden Sie sich an das Compliance-Team.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between p-6 border-t border-gray-200 bg-white">
        <div class="text-sm text-gray-500">
          Bericht erstellt am {{ report.timestamp ? new Date(report.timestamp).toLocaleString('de-DE') : 'Unbekannt' }}
        </div>

        <div class="flex items-center space-x-3">
          <button
            v-if="isEditing"
            @click="handleSave"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Änderungen speichern
          </button>

          <button
            v-if="!isEditing"
            @click="navigateToReportOverview"
            class="px-4 py-2 text-white rounded-md transition-colors"
            style="background-color: #1E3B64"
            onmouseover="this.style.backgroundColor='#0f2a4a'"
            onmouseout="this.style.backgroundColor='#1E3B64'"
          >
            Vollständige Übersicht
          </button>

          <button
            v-if="!isEditing"
            @click="emit('confirm', report)"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            Bericht bestätigen
          </button>

          <button
            @click="handleCancel"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            {{ isEditing ? 'Abbrechen' : 'Schließen' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
