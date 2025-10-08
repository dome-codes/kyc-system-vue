<script setup lang="ts">
import { useKycStore } from '@/stores/kyc';
import type { KycQuestion } from '@/types/kyc';
import { computed, ref, watch } from 'vue';

interface Props {
  onSubmit?: (entity: string, questions: KycQuestion[]) => void
  resetTrigger?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [entity: string, questions: KycQuestion[], land?: string, branche?: string]
}>()

// Store
const kycStore = useKycStore()

// Form state
const entity = ref('')
const country = ref('')
const industry = ref('')
const currentStep = ref<'company' | 'verification' | 'questions'>('company')
const searchResults = ref<any[]>([])
const selectedCompany = ref<any>(null)
const isSearching = ref(false)
const isResearching = ref(false)
const activeTab = ref('standard')
const showReportPopup = ref(false)
const currentReport = ref<any>(null)

// Questions state
const selectedQuestions = ref<Set<string>>(new Set())
const selectedStandardQuestions = ref<Set<string>>(new Set())
const customQuestions = ref<KycQuestion[]>([])
const showStandardQuestions = ref(true)

// Standard questions (always active) - mapped zu Backend-IDs
const standardQuestions: KycQuestion[] = [
  { id: "1", text: "Vollständiger Firmenname?" },
  { id: "2", text: "Rechtsform des Unternehmens?" },
  { id: "3", text: "Handelsregisternummer?" },
  { id: "4", text: "Gründungsdatum?" },
  { id: "5", text: "Vollständige Geschäftsadresse?" },
  { id: "6", text: "Geschäftszweck / Unternehmensgegenstand?" },
  { id: "7", text: "Geschäftsführung / Vorstand?" },
  { id: "8", text: "Wirtschaftlich Berechtigte (25%+)?" },
  { id: "9", text: "Umsatz letztes Geschäftsjahr?" },
  { id: "10", text: "Anzahl der Mitarbeiter?" },
]

// Question groups
const questionGroups = [
  {
    id: 'compliance',
    title: 'Compliance & Regulierung',
    description: 'Rechtliche und regulatorische Aspekte',
    questions: [
      { id: 'comp_aml', text: 'Anti-Money-Laundering (AML) Verfahren?' },
      { id: 'comp_kyc', text: 'KYC-Prozesse und Dokumentation?' },
      { id: 'comp_sanctions', text: 'Sanktionslisten-Prüfung?' },
    ]
  },
  {
    id: 'financial',
    title: 'Finanzielle Stabilität',
    description: 'Finanzielle Gesundheit und Stabilität',
    questions: [
      { id: 'fin_credit_rating', text: 'Kreditrating und Bonität?' },
      { id: 'fin_financial_statements', text: 'Jahresabschlüsse der letzten 3 Jahre?' },
      { id: 'fin_cash_flow', text: 'Cashflow-Analyse?' },
    ]
  },
  {
    id: 'reputation',
    title: 'Reputation & Medien',
    description: 'Öffentliche Wahrnehmung und Medienpräsenz',
    questions: [
      { id: 'rep_media_coverage', text: 'Medienberichterstattung?' },
      { id: 'rep_legal_issues', text: 'Rechtliche Auseinandersetzungen?' },
    ]
  }
]

// Computed
const steps = [
  { id: 'company', title: 'Unternehmensdaten', description: 'Grunddaten eingeben' },
  { id: 'verification', title: 'Unternehmensauswahl', description: 'Passende Firma wählen' },
  { id: 'questions', title: 'Fragenauswahl', description: 'Compliance-Fragen wählen' }
]

const currentStepIndex = computed(() => steps.findIndex(step => step.id === currentStep.value))

const canGoBack = computed(() => currentStepIndex.value > 0)
const canGoForward = computed(() => currentStepIndex.value < steps.length - 1)

const isSearchValid = computed(() =>
  entity.value.trim().length > 0  // Nur Firmenname ist Pflicht
)

    const totalSelected = computed(() => {
      const standardCount = showStandardQuestions.value ? selectedStandardQuestions.value.size : 0
      return standardCount + selectedQuestions.value.size + customQuestions.value.length
    })

const maxQuestions = 30

const isFormValid = computed(() => {
  if (currentStep.value === 'company') {
    return entity.value.trim().length > 0
  }
  if (currentStep.value === 'verification') {
    return selectedCompany.value !== null
  }
  if (currentStep.value === 'questions') {
    return selectedCompany.value !== null &&
           totalSelected.value >= 1 &&
           totalSelected.value <= maxQuestions
  }
  return false
})

// Methods
const goToStep = (stepId: string) => {
  currentStep.value = stepId as any
}

const formatAddress = (item: any) => {
  // Zeige echte Adresse wenn verfügbar
  if (item.street && item.city) {
    return `${item.street}, ${item.city}`
  } else if (item.city) {
    return item.city
  } else if (item.street) {
    return item.street
  } else {
    // Fallback: Zeige Branche und Land
    return `${item.branche} • ${item.land}`
  }
}

const handleCompanySearch = async () => {
  if (!isSearchValid.value) return

  isSearching.value = true
  try {
    console.log('🔍 Searching for company:', entity.value)

		// Rufe Backend API auf für echte Unternehmenssuche
		const response = await fetch('http://localhost:8000/verify', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				mieter: entity.value,
				fragen: [1, 2], // Basis-Fragen für Verifizierung
				land: country.value || 'Deutschland',
				branche: industry.value || null
			})
		})

		const result = await response.json()
		console.log('✅ Backend response:', result)

		// Konvertiere Backend-Ergebnisse zu Frontend-Format
		if (result.vorschlaege && result.vorschlaege.length > 0) {
			searchResults.value = result.vorschlaege.map((item: any) => ({
				id: item.id,
				name: item.name,
				address: formatAddress(item), // Zeige echte Adresse wenn verfügbar
				industry: item.branche,
				country: item.land,
				url: item.url,
				street: item.street,
				city: item.city
			}))
			console.log('🎯 Found companies:', searchResults.value)

			goToStep('verification')
		} else {
			// Fallback falls keine Ergebnisse
			searchResults.value = [
				{
					id: 'fallback_1',
					name: `${entity.value} GmbH`,
					address: `${industry.value || 'Unbekannt'} • ${country.value || 'Deutschland'}`,
					industry: industry.value || 'Unbekannt',
					country: country.value || 'Deutschland'
				}
			]
			goToStep('verification')
		}

  } catch (error) {
    console.error('❌ Search error:', error)

    // Fallback bei Fehlern
    searchResults.value = [
      {
        id: 'error_fallback_1',
        name: `${entity.value} GmbH`,
        address: `${industry.value || 'Unbekannt'} • ${country.value || 'Deutschland'}`,
        industry: industry.value || 'Unbekannt',
        country: country.value || 'Deutschland'
      }
    ]
    goToStep('verification')
  } finally {
    isSearching.value = false
  }
}

const handleCompanySelect = (company: any) => {
  selectedCompany.value = company
  goToStep('questions')
}

const toggleQuestion = (questionId: string) => {
  if (selectedQuestions.value.has(questionId)) {
    selectedQuestions.value.delete(questionId)
  } else {
    selectedQuestions.value.add(questionId)
  }
}

const toggleStandardQuestion = (questionId: string) => {
  if (selectedStandardQuestions.value.has(questionId)) {
    selectedStandardQuestions.value.delete(questionId)
  } else {
    selectedStandardQuestions.value.add(questionId)
  }
}

const toggleGroup = (groupId: string, add: boolean) => {
  const group = questionGroups.find(g => g.id === groupId)
  if (!group) return

  group.questions.forEach(question => {
    if (add) {
      selectedQuestions.value.add(question.id)
    } else {
      selectedQuestions.value.delete(question.id)
    }
  })
}

const addCustomQuestion = () => {
  const id = `custom_${Date.now()}`
  customQuestions.value.push({
    id,
    text: ''
  })
}

const removeCustomQuestion = (index: number) => {
  customQuestions.value.splice(index, 1)
}

    const handleSubmit = async () => {
      if (!isFormValid.value) return

      isResearching.value = true

      try {
        // Verwende die Standard-Fragen aus dem Store direkt
        const finalQuestions = showStandardQuestions.value
          ? standardQuestions.filter(q => selectedStandardQuestions.value.has(q.id))
          : []

        // Verwende die ausgewählte Firma für die Recherche
        const companyToResearch = selectedCompany.value?.name || entity.value
        const companyCountry = selectedCompany.value?.country || country.value || 'Deutschland'
        const companyBranche = selectedCompany.value?.industry || industry.value

        console.log('🚀 Starting research with questions:', finalQuestions.map(q => parseInt(q.id)))
        console.log('📤 Request data:', {
          mieter: companyToResearch,
          fragen: finalQuestions.map(q => parseInt(q.id)),
          land: companyCountry,
          branche: companyBranche
        })

        // Direkt den Research-Endpunkt aufrufen mit der ausgewählten Firma
        const response = await fetch('http://localhost:8000/research', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            mieter: companyToResearch,
            fragen: finalQuestions.map(q => parseInt(q.id)),
            land: companyCountry,
            branche: companyBranche
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const rawResult = await response.json()
        console.log('✅ Raw research response:', rawResult)

        // Konvertiere Backend-Response zu Frontend-Report-Format
        const reportAnswers = Object.fromEntries(
          rawResult.antworten.map((antwort: any) => [
            antwort.frage_id,
            {
              answer: antwort.antwort,
              source: antwort.quelle,
              verificationStatus: 'verified' as const,
              confidence: 'high' as const,
              quelle: antwort.quelle // Für PDF-Kompatibilität
            }
          ])
        )

        const reportData = {
          id: `report_${Date.now()}`,
          entity: companyToResearch,
          answers: reportAnswers, // Jetzt als { frage_id: answer_object } Format
          sources: Object.fromEntries(rawResult.antworten.map((a: any) => [a.frage_id, a.quelle])),
          status: 'pending_confirmation' as const,
          timestamp: new Date().toISOString(),
          questions: finalQuestions,
          summary: `Recherche für ${companyToResearch} mit ${finalQuestions.length} Fragen abgeschlossen`
        }

        // Direkt das Report-Popup mit den Backend-Daten anzeigen
        currentReport.value = reportData
        showReportPopup.value = true

        console.log('🎉 Report-Popup displayed:', {
          reportData,
          showReportPopup: showReportPopup.value,
          currentReport: currentReport.value
        })

      } catch (error) {
        console.error('❌ Research error:', error)

        // Bei Fehler einfach eine Fehlermeldung zeigen
        console.error('❌ Research failed, no report will be shown')
      } finally {
        isResearching.value = false
      }
    }

    selectedStandardQuestions.value = new Set(standardQuestions.map(q => q.id))

    // Handler für Report-Bestätigung - WICHTIG: Bericht zur Liste hinzufügen!
    const handleReportConfirm = (report: any) => {
      console.log('✅ Report confirmed, adding to store:', report)
      kycStore.confirmReport(report) // ← Das war der fehlende Aufruf!
      showReportPopup.value = false
      // Optional: Zur Reports-Übersicht navigieren
      // router.push('/reports')
    }

    const handleReportCancel = () => {
      showReportPopup.value = false
    }

    const generatePDF = () => {
      if (currentReport.value) {
        // Direkt die PDF-Funktion vom kycStore verwenden
        kycStore.generateReportPDF(currentReport.value)
      }
    }

    const getQuestionText = (questionId: string) => {
      // Konvertiere Backend-ID (z.B. "q1") zu Standard-Frage
      const questionNumber = parseInt(questionId.replace('q', ''))

      // Standard-Fragen Mapping
      const standardQuestionsMap: Record<number, string> = {
        1: "Vollständiger Firmenname?",
        2: "Rechtsform des Unternehmens?",
        3: "Handelsregisternummer?",
        4: "Gründungsdatum?",
        5: "Vollständige Geschäftsadresse?",
        6: "Geschäftszweck / Unternehmensgegenstand?",
        7: "Geschäftsführung / Vorstand?",
        8: "Wirtschaftlich Berechtigte (25%+)?",
        9: "Umsatz letztes Geschäftsjahr?",
        10: "Anzahl der Mitarbeiter?",
        11: "Risiko-Bewertung?",
        12: "Compliance-Status?",
        13: "Finanzierungsstatus?",
        14: "Presse / Ruf",
        15: "Insolvenzzeichen?"
      }

      return standardQuestionsMap[questionNumber] || `Frage ${questionId}`
    }

    watch(() => props.resetTrigger, () => {
      if (props.resetTrigger) {
        resetForm()
      }
    })

    const resetForm = () => {
      entity.value = ''
      country.value = ''
      industry.value = ''
      currentStep.value = 'company'
      searchResults.value = []
      selectedCompany.value = null
      isSearching.value = false
      activeTab.value = 'standard'
      selectedStandardQuestions.value = new Set(standardQuestions.map(q => q.id))
      selectedQuestions.value = new Set()
      customQuestions.value = []
      showStandardQuestions.value = true
    }
</script>

<template>
  <div class="space-y-8">
    <!-- Step Navigation -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <!-- Current Step Only -->
          <div
            class="flex items-center space-x-3 px-4 py-3 rounded-lg text-white"
            style="background-color: #1E3B64"
          >
            <div class="w-6 h-6 rounded-full bg-white flex items-center justify-center text-xs font-medium" style="color: #1E3B64">
              {{ currentStepIndex + 1 }}
            </div>
            <div class="text-left">
              <div class="text-sm font-medium">{{ steps[currentStepIndex].title }}</div>
              <div class="text-xs opacity-75">{{ steps[currentStepIndex].description }}</div>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex items-center space-x-2">
          <button
            v-if="canGoBack"
            type="button"
            @click="goToStep(steps[currentStepIndex - 1].id)"
            class="flex items-center gap-1 px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Zurück
          </button>
          <button
            v-if="canGoForward && currentStep === 'company'"
            type="button"
            @click="goToStep('verification')"
            :disabled="!isSearchValid"
            class="flex items-center gap-1 px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Weiter
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="bg-white rounded-lg shadow-sm">
      <!-- Step 1: Company Information -->
      <div v-if="currentStep === 'company'" class="p-8">
        <div class="flex items-center mb-4">
          <svg class="h-5 w-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Unternehmensinformationen</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Firmenname *</label>
            <input
              v-model="entity"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. Musterfirma GmbH"
              @keyup.enter="handleCompanySearch"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Standort (optional)</label>
            <input
              v-model="country"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. München, Deutschland oder nur Berlin (leer = Deutschland)"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Branche (optional)</label>
            <input
              v-model="industry"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. Finanzdienstleistungen (leer = unbekannt)"
            />
          </div>
        </div>

        <p class="text-sm text-gray-600 mb-8">
          Geben Sie mindestens den Firmennamen ein. Land und Branche helfen bei der Verfeinerung der Suche, sind aber optional.
        </p>

        <div class="flex justify-end">
          <button
            @click="handleCompanySearch"
            :disabled="!isSearchValid || isSearching"
            class="px-4 py-2 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            style="background-color: #1E3B64"
            onmouseover="this.style.backgroundColor='#0f2a4a'"
            onmouseout="this.style.backgroundColor='#1E3B64'"
          >
            <span v-if="isSearching">Suche läuft...</span>
            <span v-else>Unternehmen suchen</span>
          </button>
        </div>
      </div>

      <!-- Step 2: Company Selection -->
      <div v-if="currentStep === 'verification'" class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Unternehmensauswahl</h3>
        <p class="text-gray-600 mb-4">Wählen Sie das passende Unternehmen aus den Suchergebnissen:</p>

        <div class="space-y-3">
          <div
            v-for="company in searchResults"
            :key="company.id"
            @click="handleCompanySelect(company)"
            class="p-4 border border-gray-200 rounded-lg cursor-pointer transition-colors"
            style="--hover-border: #1E3B64; --hover-bg: rgba(30, 59, 100, 0.1);"
            onmouseover="this.style.borderColor='#1E3B64'; this.style.backgroundColor='rgba(30, 59, 100, 0.1)'"
            onmouseout="this.style.borderColor=''; this.style.backgroundColor=''"
          >
            <h4 class="font-medium text-gray-900">{{ company.name }}</h4>
            <p class="text-sm text-gray-600">{{ company.address }}</p>
            <p class="text-sm text-gray-500">{{ company.industry }} • {{ company.country }}</p>
          </div>
        </div>
      </div>

      <!-- Step 3: Question Selection -->
      <div v-if="currentStep === 'questions'" class="p-8">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center space-x-3">
            <svg class="h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Fragen-Auswahl</h3>
              <p class="text-sm text-gray-500">Ausgewähltes Unternehmen: {{ selectedCompany?.name || entity }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
              {{ totalSelected }}/{{ maxQuestions }}
            </span>
          </div>
        </div>

        <!-- Question Category Tabs -->
        <div class="mb-6">
          <div class="flex items-center space-x-1 border-b border-gray-200">
            <button
              @click="activeTab = 'standard'"
              class="flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors"
              :class="activeTab === 'standard' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>Standard 10</span>
            </button>
            <button
              v-for="group in questionGroups"
              :key="group.id"
              @click="activeTab = group.id"
              class="flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors"
              :class="activeTab === group.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            >
              <span>{{ group.title }} {{ group.questions.length }}</span>
            </button>
          </div>
        </div>

        <!-- Toggle for Standard Questions -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">Standardfragen anzeigen</span>
            <div class="flex items-center space-x-14">
              <div class="relative inline-block w-12 h-6 align-middle select-none">
              <input
                type="checkbox"
                v-model="showStandardQuestions"
                class="absolute block w-6 h-6 rounded-full bg-white border-2 border-gray-300 appearance-none cursor-pointer transition-transform duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                :style="{ top: '-1px', left: '-1px', transform: showStandardQuestions ? 'translateX(24px)' : 'translateX(0px)' }"
              />
                <label class="block h-6 overflow-hidden rounded-full cursor-pointer transition-colors duration-200 ease-in-out" :style="{ backgroundColor: showStandardQuestions ? '#1E3B64' : '#D1D5DB' }"></label>
              </div>
              <span class="text-sm text-gray-600">10 Fragen</span>
            </div>
          </div>
        </div>

        <!-- Tab Content -->
        <div class="mb-8">
          <!-- Standard Questions Tab -->
          <div v-if="activeTab === 'standard'">
            <div v-if="showStandardQuestions" class="space-y-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="font-medium text-gray-900">Standardfragen</h4>
                    <p class="text-sm text-gray-600">Grundlegende Unternehmensinformationen</p>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">
                      {{ selectedStandardQuestions.size }}/{{ standardQuestions.length }}
                    </span>
                    <button
                      @click="selectedStandardQuestions = new Set(standardQuestions.map(q => q.id))"
                      class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                    >
                      Alle hinzufügen
                    </button>
                    <button
                      @click="selectedStandardQuestions = new Set()"
                      class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Alle entfernen
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label
                    v-for="(question, index) in standardQuestions"
                    :key="question.id"
                    class="flex items-center space-x-6 cursor-pointer p-4 rounded-lg hover:bg-white transition-all duration-200 border border-transparent hover:border-gray-200 hover:shadow-sm"
                  >
                    <div class="flex-shrink-0 relative">
                      <input
                        type="checkbox"
                        :checked="selectedStandardQuestions.has(question.id)"
                        @change="toggleStandardQuestion(question.id)"
                        class="sr-only"
                      />
                      <div
                        class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-200 cursor-pointer"
                        :class="selectedStandardQuestions.has(question.id)
                          ? 'bg-blue-600 text-white'
                          : 'bg-blue-50 text-blue-600 border-2 border-blue-200 hover:border-blue-300'"
                      >
                        {{ index + 1 }}
                      </div>
                    </div>
                    <div class="flex-1 pl-2">
                      <span class="text-sm text-gray-700 leading-relaxed">{{ question.text }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8">
              <p class="text-gray-500">Standardfragen sind deaktiviert</p>
            </div>
          </div>

          <!-- Group Questions Tab -->
          <div v-else>
            <div
              v-for="group in questionGroups.filter(g => g.id === activeTab)"
              :key="group.id"
              class="space-y-4"
            >
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="font-medium text-gray-900">{{ group.title }}</h4>
                    <p class="text-sm text-gray-600">{{ group.description }}</p>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">
                      {{ group.questions.filter(q => selectedQuestions.has(q.id)).length }}/{{ group.questions.length }}
                    </span>
                    <button
                      @click="toggleGroup(group.id, true)"
                      class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                    >
                      Alle hinzufügen
                    </button>
                    <button
                      @click="toggleGroup(group.id, false)"
                      class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      Alle entfernen
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label
                    v-for="(question, index) in group.questions"
                    :key="question.id"
                    class="flex items-center space-x-6 cursor-pointer p-4 rounded-lg hover:bg-white transition-all duration-200 border border-transparent hover:border-gray-200 hover:shadow-sm"
                  >
                    <div class="flex-shrink-0 relative">
                      <input
                        type="checkbox"
                        :checked="selectedQuestions.has(question.id)"
                        @change="toggleQuestion(question.id)"
                        class="sr-only"
                      />
                      <div
                        class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-200 cursor-pointer"
                        :class="selectedQuestions.has(question.id)
                          ? 'bg-blue-600 text-white'
                          : 'bg-blue-50 text-blue-600 border-2 border-blue-200 hover:border-blue-300'"
                      >
                        {{ index + 1 }}
                      </div>
                    </div>
                    <div class="flex-1 pl-2">
                      <span class="text-sm text-gray-700 leading-relaxed">{{ question.text }}</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Custom Questions Section -->
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h4 class="font-semibold text-gray-900 text-lg">Eigene Zusatzfragen</h4>
              <p class="text-sm text-gray-600 mt-1">Fügen Sie spezifische Fragen hinzu</p>
            </div>
            <button
              @click="addCustomQuestion"
              class="px-4 py-2 text-sm text-white rounded-lg transition-colors"
              style="background-color: #1E3B64;"
              onmouseover="this.style.backgroundColor='#0f2a4a'"
              onmouseout="this.style.backgroundColor='#1E3B64'"
            >
              + Frage hinzufügen
            </button>
          </div>

          <div v-if="customQuestions.length === 0" class="text-center py-8">
            <p class="text-gray-500">Noch keine eigenen Fragen hinzugefügt</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="(question, index) in customQuestions"
              :key="question.id"
              class="flex items-center space-x-3 bg-white rounded-lg p-4 shadow-sm border border-gray-200"
            >
              <input
                v-model="question.text"
                type="text"
                class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Eigene Frage eingeben..."
              />
              <button
                @click="removeCustomQuestion(index)"
                class="p-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>


        <!-- Submit Button -->
        <div class="mt-8 flex justify-center">
          <button
            @click="handleSubmit"
            :disabled="!isFormValid || isResearching"
            class="px-8 py-3 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-base font-medium shadow-md hover:shadow-lg transform hover:scale-[1.02] disabled:transform-none"
            style="background-color: #1E3B64;"
            onmouseover="this.style.backgroundColor='#0f2a4a'"
            onmouseout="this.style.backgroundColor='#1E3B64'"
          >
            <div class="flex items-center justify-center space-x-2">
              <!-- Lade-Spinner wenn Recherche läuft -->
              <div v-if="isResearching" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <!-- Check-Icon wenn nicht aktiv -->
              <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>{{ isResearching ? 'Recherche läuft...' : 'Mieter Recherche starten' }}</span>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Report Popup -->
    <div v-if="showReportPopup && currentReport" class="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="flex-shrink-0 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">Mieter Recherche Bericht</h2>
            <p class="text-sm text-gray-500">{{ currentReport.entity }}</p>
          </div>
          <button @click="showReportPopup = false" class="text-gray-400 hover:text-gray-600">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <div v-for="(answer, questionId) in currentReport.answers" :key="questionId" class="mb-6">
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="font-semibold text-gray-900 mb-2">{{ getQuestionText(String(questionId)) }}</h3>
              <p class="text-gray-700 mb-3">{{ answer.answer }}</p>
              <div v-if="answer.source" class="flex items-center space-x-2">
                <span class="text-sm text-gray-500">Quelle:</span>
                <a :href="answer.source" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm underline">
                  {{ answer.source }}
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 flex gap-4">
          <button
            @click="handleReportCancel"
            class="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Schließen
          </button>
          <button
            @click="generatePDF"
            class="flex-1 px-4 py-2 text-white rounded-md transition-colors"
            style="background-color: #1E3B64"
          >
            PDF herunterladen
          </button>
          <button
            @click="handleReportConfirm(currentReport)"
            class="flex-1 px-4 py-2 text-white rounded-md transition-colors"
            style="background-color: #10B981"
          >
            Bericht bestätigen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
