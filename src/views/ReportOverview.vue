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
              <h1 class="text-xl font-semibold text-gray-900">KYC-Bericht Übersicht</h1>
              <p class="text-sm text-gray-500">{{ report?.entity }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="downloadPDF"
              class="flex items-center space-x-2 px-4 py-2 text-white rounded-lg transition-colors"
              style="background-color: #1E3B64"
              onmouseover="this.style.backgroundColor='#0f2a4a'"
              onmouseout="this.style.backgroundColor='#1E3B64'"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>PDF herunterladen</span>
            </button>
            <button
              @click="confirmReport"
              class="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Bericht bestätigen</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- Report Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Gesamtfragen</p>
                <p class="text-2xl font-bold text-gray-900">{{ report?.summary?.totalQuestions || 0 }}</p>
              </div>
              <div class="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Beantwortet</p>
                <p class="text-2xl font-bold text-green-600">{{ report?.summary?.completedQuestions || 0 }}</p>
              </div>
              <div class="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Risiko-Score</p>
                <p class="text-2xl font-bold" :class="getRiskScoreColor(report?.summary?.riskScore || 0)">
                  {{ report?.summary?.riskScore || 0 }}%
                </p>
              </div>
              <div class="h-12 w-12 rounded-lg flex items-center justify-center" :class="getRiskScoreBgColor(report?.summary?.riskScore || 0)">
                <svg class="h-6 w-6" :class="getRiskScoreIconColor(report?.summary?.riskScore || 0)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Compliance-Score</p>
                <p class="text-2xl font-bold" :class="getComplianceScoreColor(report?.summary?.complianceScore || 0)">
                  {{ report?.summary?.complianceScore || 0 }}%
                </p>
              </div>
              <div class="h-12 w-12 rounded-lg flex items-center justify-center" :class="getComplianceScoreBgColor(report?.summary?.complianceScore || 0)">
                <svg class="h-6 w-6" :class="getComplianceScoreIconColor(report?.summary?.complianceScore || 0)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Report Details -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Questions & Answers -->
          <div class="lg:col-span-2">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200">
              <div class="p-6 border-b border-gray-200">
                <h2 class="text-xl font-semibold text-gray-900">Fragen & Antworten</h2>
                <p class="text-sm text-gray-600 mt-1">Detaillierte Analyse der Compliance-Fragen</p>
              </div>
              <div class="p-6">
                <div class="space-y-6">
                  <div
                    v-for="(answer, questionId) in report?.answers"
                    :key="questionId"
                    class="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                  >
                    <div class="flex items-start space-x-3">
                      <div class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {{ getQuestionNumber(questionId) }}
                      </div>
                      <div class="flex-1">
                        <h3 class="font-medium text-gray-900 mb-2">
                          {{ getQuestionText(questionId) }}
                        </h3>
                        <p class="text-gray-600 text-sm leading-relaxed">
                          {{ answer }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-6">
            <!-- Report Info -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200">
              <div class="p-6 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900">Bericht-Informationen</h3>
              </div>
              <div class="p-6 space-y-4">
                <div>
                  <p class="text-sm font-medium text-gray-600">Unternehmen</p>
                  <p class="text-gray-900 font-medium">{{ report?.entity }}</p>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-600">Erstellt am</p>
                  <p class="text-gray-900">{{ formatDate(report?.timestamp) }}</p>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-600">Status</p>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="report?.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                  >
                    {{ report?.status === 'confirmed' ? 'Bestätigt' : 'Ausstehend' }}
                  </span>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-600">Bericht-ID</p>
                  <p class="text-gray-900 font-mono text-sm">{{ report?.id }}</p>
                </div>
              </div>
            </div>

            <!-- Risk Assessment -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200">
              <div class="p-6 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900">Risiko-Bewertung</h3>
              </div>
              <div class="p-6 space-y-4">
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-gray-600">Gesamtrisiko</span>
                    <span class="font-medium" :class="getRiskScoreColor(report?.summary?.riskScore || 0)">
                      {{ report?.summary?.riskScore || 0 }}%
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="h-2 rounded-full transition-all duration-300"
                      :class="getRiskScoreBarColor(report?.summary?.riskScore || 0)"
                      :style="{ width: `${report?.summary?.riskScore || 0}%` }"
                    ></div>
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-gray-600">Compliance</span>
                    <span class="font-medium" :class="getComplianceScoreColor(report?.summary?.complianceScore || 0)">
                      {{ report?.summary?.complianceScore || 0 }}%
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="h-2 rounded-full transition-all duration-300"
                      :class="getComplianceScoreBarColor(report?.summary?.complianceScore || 0)"
                      :style="{ width: `${report?.summary?.complianceScore || 0}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200">
              <div class="p-6 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900">Aktionen</h3>
              </div>
              <div class="p-6 space-y-3">
                <button
                  @click="downloadPDF"
                  class="w-full flex items-center justify-center space-x-2 px-4 py-3 text-white rounded-lg transition-colors"
                  style="background-color: #1E3B64"
                  onmouseover="this.style.backgroundColor='#0f2a4a'"
                  onmouseout="this.style.backgroundColor='#1E3B64'"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <span>PDF herunterladen</span>
                </button>
                <button
                  @click="confirmReport"
                  class="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>Bericht bestätigen</span>
                </button>
                <button
                  @click="$router.push('/')"
                  class="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                  </svg>
                  <span>Zurück zur Startseite</span>
                </button>
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
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const kycStore = useKycStore()

const report = ref<KycReport | null>(null)

onMounted(() => {
  // Get report from store or route params
  if (kycStore.currentReport) {
    report.value = kycStore.currentReport
  } else if (route.params.id) {
    // Load report by ID (for future implementation)
    console.log('Loading report by ID:', route.params.id)
  }
})

const getQuestionNumber = (questionId: string): number => {
  if (!report.value?.questions) return 1
  return report.value.questions.findIndex(q => q.id === questionId) + 1
}

const getQuestionText = (questionId: string): string => {
  if (!report.value?.questions) return 'Unbekannte Frage'
  const question = report.value.questions.find(q => q.id === questionId)
  return question?.text || 'Unbekannte Frage'
}

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

const getRiskScoreColor = (score: number): string => {
  if (score >= 80) return 'text-red-600'
  if (score >= 60) return 'text-orange-600'
  if (score >= 40) return 'text-yellow-600'
  return 'text-green-600'
}

const getRiskScoreBgColor = (score: number): string => {
  if (score >= 80) return 'bg-red-100'
  if (score >= 60) return 'bg-orange-100'
  if (score >= 40) return 'bg-yellow-100'
  return 'bg-green-100'
}

const getRiskScoreIconColor = (score: number): string => {
  if (score >= 80) return 'text-red-600'
  if (score >= 60) return 'text-orange-600'
  if (score >= 40) return 'text-yellow-600'
  return 'text-green-600'
}

const getRiskScoreBarColor = (score: number): string => {
  if (score >= 80) return 'bg-red-500'
  if (score >= 60) return 'bg-orange-500'
  if (score >= 40) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getComplianceScoreColor = (score: number): string => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  if (score >= 40) return 'text-orange-600'
  return 'text-red-600'
}

const getComplianceScoreBgColor = (score: number): string => {
  if (score >= 80) return 'bg-green-100'
  if (score >= 60) return 'bg-yellow-100'
  if (score >= 40) return 'bg-orange-100'
  return 'bg-red-100'
}

const getComplianceScoreIconColor = (score: number): string => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  if (score >= 40) return 'text-orange-600'
  return 'text-red-600'
}

const getComplianceScoreBarColor = (score: number): string => {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  if (score >= 40) return 'bg-orange-500'
  return 'bg-red-500'
}

const downloadPDF = () => {
  if (report.value) {
    import('@/utils/pdfGenerator').then(({ generateKycReportPDF }) => {
      generateKycReportPDF(report.value!)
    })
  }
}

const confirmReport = () => {
  if (report.value) {
    kycStore.confirmReport(report.value)
    router.push('/')
  }
}
</script>
