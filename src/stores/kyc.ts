import { kycApi } from '@/api/kyc'
import type { CompanySearchResult, KycQuestion, KycReport } from '@/types/kyc'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useKycStore = defineStore('kyc', () => {
  // State
  const reports = ref<KycReport[]>([])
  const currentReport = ref<KycReport | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchResults = ref<CompanySearchResult[]>([])
  const selectedCompany = ref<CompanySearchResult | null>(null)

  // Getters
  const confirmedReports = computed(() =>
    reports.value.filter(report => report.status === 'confirmed')
  )

  const totalReports = computed(() => reports.value.length)

  // Actions
  const createReport = async (entity: string, questions: KycQuestion[], land?: string, branche?: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await kycApi.createReport(entity, questions, land, branche)

      const newReport: KycReport = {
        id: response.id,
        entity: response.entity,
        answers: response.answers,
        sources: response.sources || {},
        status: "pending_confirmation",
        timestamp: response.timestamp,
        questions: response.questions,
        summary: response.summary
      }

      currentReport.value = newReport
      return newReport
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Ein unerwarteter Fehler ist aufgetreten'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const confirmReport = (report: KycReport) => {
    const confirmedReport = { ...report, status: "confirmed" as const }
    reports.value.push(confirmedReport)
    currentReport.value = confirmedReport
  }

  const deleteReport = (index: number) => {
    reports.value.splice(index, 1)
  }

  const searchCompanies = async (query: string) => {
    isLoading.value = true
    try {
      const results = await kycApi.searchCompanies(query)
      searchResults.value = results
      return results
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Suche fehlgeschlagen'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const selectCompany = (company: CompanySearchResult) => {
    selectedCompany.value = company
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    reports,
    currentReport,
    isLoading,
    error,
    searchResults,
    selectedCompany,

    // Getters
    confirmedReports,
    totalReports,

    // Actions
    createReport,
    confirmReport,
    deleteReport,
    searchCompanies,
    selectCompany,
    clearError
  }
})
