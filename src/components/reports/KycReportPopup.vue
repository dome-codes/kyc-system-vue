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
const editableSources = ref<Record<string, string>>({})

// Initialize editable answers and sources
editableAnswers.value = { ...props.report.answers }
editableSources.value = { ...props.report.sources }

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = () => {
  const updatedReport = {
    ...props.report,
    answers: editableAnswers.value,
    sources: editableSources.value
  }
  emit('confirm', updatedReport)
  isEditing.value = false
}

const handleCancel = () => {
  editableAnswers.value = { ...props.report.answers }
  editableSources.value = { ...props.report.sources }
  isEditing.value = false
  emit('cancel')
}

const handleDownloadPDF = () => {
  import('@/utils/pdfGenerator').then(({ generateKycReportPDF }) => {
    const reportWithEditableAnswers = {
      ...props.report,
      answers: editableAnswers.value,
      sources: editableSources.value
    }
    generateKycReportPDF(reportWithEditableAnswers)
  })
}

const totalQuestions = computed(() => Object.keys(editableAnswers.value).length)

const navigateToReportOverview = () => {
  router.push(`/report/${props.report.id || 'current'}`)
}

const handleSendToDMS = () => {
  // Demo function for DMS integration
  alert('Demo: Bericht würde an DMS gesendet/gespeichert werden')
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-5 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[80vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
        <div class="flex items-center space-x-3">
          <div class="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-semibold text-gray-900">Mieter Recherche Bericht</h2>
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
      <div class="overflow-y-auto flex-1 p-6">
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
                </div>
                <div v-if="isEditing">
                  <div class="space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Antwort</label>
                      <textarea
                        v-model="editableAnswers[questionId]"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="3"
                      ></textarea>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Quelle</label>
                      <input
                        v-model="editableSources[questionId]"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="z.B. Handelsregister, Jahresabschluss, Website..."
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Quelle-Link (optional)</label>
                      <input
                        v-model="editableSources[questionId + '_link']"
                        type="url"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="https://..."
                      />
                    </div>
                  </div>
                </div>
                <div v-else>
                  <p class="text-gray-700 mb-2">{{ answer }}</p>
                  <div v-if="editableSources[questionId] || editableSources[questionId + '_link']" class="text-sm text-gray-500 space-y-1">
                    <div v-if="editableSources[questionId]">
                      <span class="font-medium">Quelle:</span> {{ editableSources[questionId] }}
                    </div>
                    <div v-if="editableSources[questionId + '_link']">
                      <span class="font-medium">Link:</span>
                      <a :href="editableSources[questionId + '_link']" target="_blank" class="text-blue-600 hover:text-blue-800 underline">
                        {{ editableSources[questionId + '_link'] }}
                      </a>
                    </div>
                  </div>
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
              Recherche-Hinweise
            </h3>
            <div class="prose max-w-none">
              <p class="text-gray-700">
                Dieser Recherche-Bericht wurde automatisch generiert basierend auf verfügbaren Datenquellen.
                Bitte überprüfen Sie alle Angaben sorgfältig und ergänzen Sie fehlende Informationen
                bei Bedarf. Alle Quellen sind dokumentiert und können nachträglich überprüft werden.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between p-6 border-t border-gray-200 bg-white flex-shrink-0">
        <div class="text-sm text-gray-500">
          Bericht erstellt am {{ report.timestamp ? new Date(report.timestamp).toLocaleString('de-DE') : 'Unbekannt' }}
        </div>

        <div class="flex items-center gap-4">
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
            @click="handleSendToDMS"
            class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            An DMS senden/speichern
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
