<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
      <div class="container mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button
              @click="$router.push('/')"
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
            </button>
            <div class="h-10 w-10 rounded-full flex items-center justify-center" style="background-color: #1E3B64">
              <span class="text-white font-bold text-lg">O</span>
            </div>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">KYC-Berichte Übersicht</h1>
              <p class="text-sm text-gray-500">Alle bestätigten Due Diligence Berichte</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="$router.push('/')"
              class="flex items-center space-x-2 px-4 py-2 text-white rounded-lg transition-colors"
              style="background-color: #1E3B64"
              onmouseover="this.style.backgroundColor='#0f2a4a'"
              onmouseout="this.style.backgroundColor='#1E3B64'"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              <span>Neuer Bericht</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex justify-center px-4 py-8">
      <div class="max-w-4xl w-full">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200 text-center">
            <div class="text-3xl font-bold text-gray-900 mb-2">{{ kycStore.confirmedReports.length }}</div>
            <div class="text-sm text-gray-600">Gesamtberichte</div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200 text-center">
            <div class="text-3xl font-bold text-gray-900 mb-2">{{ averageQuestions }}</div>
            <div class="text-sm text-gray-600">Durchschnittliche Fragen</div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200 text-center">
            <div class="text-3xl font-bold text-gray-900 mb-2">{{ lastReportDate }}</div>
            <div class="text-sm text-gray-600">Letzter Bericht</div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200 text-center">
            <div class="text-3xl font-bold text-gray-900 mb-2">100%</div>
            <div class="text-sm text-gray-600">Compliance-Rate</div>
          </div>
        </div>

        <!-- Reports List -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="p-6 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">Bestätigte Berichte</h2>
                <p class="text-sm text-gray-600 mt-1">Alle abgeschlossenen KYC-Compliance-Berichte</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-500">{{ kycStore.confirmedReports.length }} Berichte</span>
              </div>
            </div>
          </div>

          <div v-if="kycStore.confirmedReports.length === 0" class="p-12 text-center">
            <p class="text-gray-500 text-lg">Noch keine Berichte vorhanden</p>
            <p class="text-gray-400 text-sm mt-1">Erstellen Sie Ihren ersten KYC-Bericht</p>
            <button
              @click="$router.push('/')"
              class="mt-4 px-6 py-3 text-white rounded-lg transition-colors"
              style="background-color: #1E3B64"
              onmouseover="this.style.backgroundColor='#0f2a4a'"
              onmouseout="this.style.backgroundColor='#1E3B64'"
            >
              Ersten Bericht erstellen
            </button>
          </div>

          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="(report, index) in kycStore.confirmedReports.slice().reverse()"
              :key="report.id || index"
              class="p-6 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h3 class="text-lg font-semibold text-gray-900">{{ report.entity }}</h3>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                      Bestätigt
                    </span>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                    <div>
                      <span class="font-medium">Fragen:</span>
                      {{ Object.keys(report.answers).length }} abgeschlossen
                    </div>
                    <div>
                      <span class="font-medium">Erstellt:</span>
                      {{ formatDate(report.timestamp) }}
                    </div>
                    <div v-if="report.id">
                      <span class="font-medium">ID:</span>
                      <span class="font-mono text-xs">{{ report.id }}</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2 ml-6">
                  <button
                    @click="viewReport(report)"
                    class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Anzeigen
                  </button>
                  <button
                    @click="downloadReportPDF(report)"
                    class="px-4 py-2 text-white rounded-lg transition-colors"
                    style="background-color: #1E3B64"
                    onmouseover="this.style.backgroundColor='#0f2a4a'"
                    onmouseout="this.style.backgroundColor='#1E3B64'"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useKycStore } from '@/stores/kyc'
import type { KycReport } from '@/types/kyc'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const kycStore = useKycStore()

const averageQuestions = computed(() => {
  if (kycStore.confirmedReports.length === 0) return 0
  const total = kycStore.confirmedReports.reduce((sum, report) => sum + Object.keys(report.answers).length, 0)
  return Math.round(total / kycStore.confirmedReports.length)
})

const lastReportDate = computed(() => {
  if (kycStore.confirmedReports.length === 0) return 'Keine'
  const lastReport = kycStore.confirmedReports[kycStore.confirmedReports.length - 1]
  if (!lastReport.timestamp) return 'Unbekannt'
  return new Date(lastReport.timestamp).toLocaleDateString('de-DE')
})

const formatDate = (timestamp?: string): string => {
  if (!timestamp) return 'Unbekannt'
  return new Date(timestamp).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewReport = (report: KycReport) => {
  // Set current report and navigate to overview
  kycStore.currentReport = report
  router.push(`/report/${report.id || 'current'}`)
}

const downloadReportPDF = (report: KycReport) => {
  import('@/utils/pdfGenerator').then(({ generateKycReportPDF }) => {
    generateKycReportPDF(report)
  })
}
</script>
