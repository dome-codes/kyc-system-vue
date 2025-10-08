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
            <div class="h-10 w-10 rounded-lg flex items-center justify-center shadow-md">
              <img src="/src/assets/logo.png" alt="KYC Logo" class="h-10 w-10 object-contain" />
            </div>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">Mieter Recherche Bericht</h1>
              <p class="text-sm text-gray-500">{{ report?.entity }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="downloadPDF"
              class="p-3 rounded-md transition-colors hover:bg-gray-100"
              title="PDF herunterladen"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #B91C1C">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </button>
            <button
              @click="confirmReport"
              class="p-3 rounded-md transition-colors hover:bg-gray-100"
              title="Bericht bestätigen"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #DC2626">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- Modern Report Header -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 rounded-xl p-8 mb-8 border border-red-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="h-16 w-16 rounded-xl flex items-center justify-center shadow-lg" style="background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%)">
                <svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">{{ report?.entity }}</h1>
                <p class="text-red-600 font-medium">KYC Recherche Bericht</p>
                <p class="text-sm text-gray-600 mt-1">{{ report?.summary?.totalQuestions || 0 }} Fragen • {{ report?.summary?.completedQuestions || 0 }} beantwortet</p>
              </div>
            </div>
            <div class="text-right">
              <div class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-white text-green-700 border border-green-200 shadow-sm">
                <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Bestätigt
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
                <p class="text-sm text-gray-600 mt-1">Detaillierte Analyse der Recherche-Fragen</p>
              </div>
              <div class="p-6">
                <div class="space-y-6">
                  <div
                    v-for="(answer, questionId) in report?.answers"
                    :key="questionId"
                    class="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                  >
                    <div class="flex items-start space-x-3">
                      <div class="flex-shrink-0 w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-medium">
                        {{ getQuestionNumber(questionId) }}
                      </div>
                      <div class="flex-1">
                        <h3 class="font-medium text-gray-900 mb-2">
                          {{ getQuestionText(questionId) }}
                        </h3>
                        <div class="space-y-3">
                          <!-- Answer Text -->
                          <p class="text-gray-700 leading-relaxed">
                            {{ typeof answer === 'object' ? answer.answer : answer }}
                          </p>

                          <!-- Sources -->
                          <div v-if="typeof answer === 'object' && answer.quellen && answer.quellen.length > 0" class="space-y-2">
                            <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Quellen:</p>
                            <div class="space-y-1">
                              <a
                                v-for="(quelle, index) in answer.quellen"
                                :key="index"
                                :href="quelle.url"
                                target="_blank"
                                class="inline-flex items-center text-sm text-red-600 hover:text-red-800 hover:underline"
                              >
                                <svg class="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                                {{ quelle.titel }}
                              </a>
                            </div>
                          </div>

                          <!-- Fallback for old format -->
                          <div v-else-if="typeof answer === 'object' && answer.source" class="text-xs text-gray-500">
                            Quelle: {{ answer.source }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Simplified Sidebar -->
          <div class="space-y-6">
            <!-- Quick Info -->
            <div class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Bericht-Details</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-600">Erstellt:</span>
                  <span class="text-gray-900">{{ formatDate(report?.timestamp) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">ID:</span>
                  <span class="text-gray-900 font-mono text-sm">{{ report?.id?.slice(-8) }}</span>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Aktionen</h3>
              <div class="space-y-3">
                <button
                  @click="downloadPDF"
                  class="w-full flex items-center justify-center space-x-2 px-4 py-3 text-white rounded-lg transition-colors"
                  style="background-color: #DC2626"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <span>PDF herunterladen</span>
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
  }
})

const getQuestionNumber = (questionId: string): number => {
  if (!report.value?.questions) return 1
  const index = report.value.questions.findIndex(q => q.id === questionId)
  return index >= 0 ? index + 1 : 1
}

const getQuestionText = (questionId: string): string => {
  if (!report.value?.questions) return questionId
  const question = report.value.questions.find(q => q.id === questionId)
  return question?.text || questionId
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
