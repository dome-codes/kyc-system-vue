<script setup lang="ts">
import type { KycQuestion } from '@/types/kyc';
import { computed, ref, watch } from 'vue';

interface Props {
  onSubmit?: (entity: string, questions: KycQuestion[]) => void
  resetTrigger?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [entity: string, questions: KycQuestion[]]
}>()

// Form state
const entity = ref('')
const country = ref('')
const industry = ref('')
const currentStep = ref<'company' | 'verification' | 'questions'>('company')
const searchResults = ref<any[]>([])
const selectedCompany = ref<any>(null)
const isSearching = ref(false)
const activeTab = ref('standard')

// Questions state
const selectedQuestions = ref<Set<string>>(new Set())
const customQuestions = ref<KycQuestion[]>([])
const showStandardQuestions = ref(true)

// Standard questions (always active)
const standardQuestions: KycQuestion[] = [
  { id: "std_company_name", text: "Vollständiger Firmenname?" },
  { id: "std_legal_form", text: "Rechtsform des Unternehmens?" },
  { id: "std_register_number", text: "Handelsregisternummer?" },
  { id: "std_founded_date", text: "Gründungsdatum?" },
  { id: "std_address", text: "Vollständige Geschäftsadresse?" },
  { id: "std_business_purpose", text: "Geschäftszweck / Unternehmensgegenstand?" },
  { id: "std_share_capital", text: "Stamm-/Grundkapital?" },
  { id: "std_managing_directors", text: "Geschäftsführung / Vorstand?" },
  { id: "std_beneficial_owners", text: "Wirtschaftlich Berechtigte (25%+)?" },
  { id: "std_annual_revenue", text: "Umsatz letztes Geschäftsjahr?" },
  { id: "std_employees_count", text: "Anzahl der Mitarbeiter?" },
  { id: "std_bank_relationships", text: "Bankverbindungen?" },
  { id: "std_tax_number", text: "Steuernummer?" },
  { id: "std_vat_number", text: "USt-IdNr.?" },
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
      { id: 'comp_pep', text: 'PEP (Politisch exponierte Personen) Prüfung?' },
      { id: 'comp_fatca', text: 'FATCA/CRS Compliance?' },
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
      { id: 'fin_debt_ratio', text: 'Verschuldungsgrad?' },
      { id: 'fin_liquidity', text: 'Liquiditätssituation?' },
    ]
  },
  {
    id: 'reputation',
    title: 'Reputation & Medien',
    description: 'Öffentliche Wahrnehmung und Medienpräsenz',
    questions: [
      { id: 'rep_media_coverage', text: 'Medienberichterstattung?' },
      { id: 'rep_legal_issues', text: 'Rechtliche Auseinandersetzungen?' },
      { id: 'rep_regulatory_fines', text: 'Regulatorische Bußgelder?' },
      { id: 'rep_customer_complaints', text: 'Kundenbeschwerden?' },
      { id: 'rep_industry_reputation', text: 'Branchenreputation?' },
    ]
  },
  {
    id: 'operational',
    title: 'Operative Aspekte',
    description: 'Geschäftsprozesse und operative Effizienz',
    questions: [
      { id: 'op_business_model', text: 'Geschäftsmodell und Strategie?' },
      { id: 'op_management_team', text: 'Management-Team und Erfahrung?' },
      { id: 'op_technology', text: 'Technologie-Infrastruktur?' },
      { id: 'op_supply_chain', text: 'Lieferkette und Partner?' },
      { id: 'op_risk_management', text: 'Risikomanagement-Systeme?' },
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
  entity.value.trim() && country.value.trim() && industry.value.trim()
)

    const totalSelected = computed(() => {
      const standardCount = showStandardQuestions.value ? standardQuestions.length : 0
      return standardCount + selectedQuestions.value.size + customQuestions.value.length
    })

const maxQuestions = 50

const isFormValid = computed(() =>
  currentStep.value === 'questions' &&
  selectedCompany.value &&
  totalSelected.value >= 14 &&
  totalSelected.value <= maxQuestions
)

// Methods
const goToStep = (stepId: string) => {
  currentStep.value = stepId as any
}

const handleCompanySearch = async () => {
  if (!isSearchValid.value) return

  isSearching.value = true
  try {
    // Mock search - replace with real API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    searchResults.value = [
      {
        id: '1',
        name: `${entity.value} GmbH`,
        address: 'Musterstraße 123, 12345 Musterstadt',
        industry: industry.value,
        country: country.value
      },
      {
        id: '2',
        name: `${entity.value} AG`,
        address: 'Beispielweg 456, 54321 Beispielstadt',
        industry: industry.value,
        country: country.value
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

    const handleSubmit = () => {
      if (!isFormValid.value) return

      const finalQuestions = [
        ...(showStandardQuestions.value ? standardQuestions : []),
        ...questionGroups.flatMap(g => g.questions).filter(q => selectedQuestions.value.has(q.id)),
        ...customQuestions.value.filter(q => q.text.trim())
      ]

      const entityName = selectedCompany.value?.name || entity.value

      emit('submit', entityName, finalQuestions)
    }

    // Initialize standard questions as selected
    selectedQuestions.value = new Set(standardQuestions.map(q => q.id))

    // Reset form when resetTrigger changes
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
      selectedQuestions.value = new Set(standardQuestions.map(q => q.id))
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
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Land *</label>
            <input
              v-model="country"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. Deutschland"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Branche *</label>
            <input
              v-model="industry"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. Finanzdienstleistungen"
            />
          </div>
        </div>

        <p class="text-sm text-gray-600 mb-8">
          Geben Sie die grundlegenden Unternehmensinformationen ein, um eine passende Firma zu finden.
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
              {{ totalSelected }}/32
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
              <span>Standard 14</span>
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
        <div class="mb-6">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">Standardfragen anzeigen</span>
            <div class="flex items-center space-x-3">
              <div class="relative inline-block w-12 h-6 align-middle select-none">
              <input
                type="checkbox"
                v-model="showStandardQuestions"
                class="absolute block w-6 h-6 rounded-full bg-white border-2 border-gray-300 appearance-none cursor-pointer transition-transform duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                :style="{ top: '-1px', left: '-1px', transform: showStandardQuestions ? 'translateX(24px)' : 'translateX(0px)' }"
              />
                <label class="block h-6 overflow-hidden rounded-full cursor-pointer transition-colors duration-200 ease-in-out" :style="{ backgroundColor: showStandardQuestions ? '#1E3B64' : '#D1D5DB' }"></label>
              </div>
              <span class="text-sm text-gray-600">14 Fragen</span>
            </div>
          </div>
        </div>

        <!-- Tab Content -->
        <div class="mb-8">
          <!-- Standard Questions Tab -->
          <div v-if="activeTab === 'standard'">
            <div v-if="showStandardQuestions" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="(question, index) in standardQuestions.slice(0, 6)"
                :key="question.id"
                class="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all duration-200"
              >
                <div class="flex items-start space-x-3">
                  <span class="flex-shrink-0 w-6 h-6 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                    {{ index + 1 }}
                  </span>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ question.text }}</p>
                    <p class="text-xs text-gray-500 mt-1">immer enthalten</p>
                  </div>
                </div>
              </div>
            </div>
            <p v-if="showStandardQuestions" class="text-sm text-gray-500 mt-4">
              + 8 weitere Standardfragen werden automatisch hinzugefügt
            </p>
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

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <label
                    v-for="question in group.questions"
                    :key="question.id"
                    class="flex items-start space-x-3 cursor-pointer p-3 rounded-lg hover:bg-white transition-colors"
                  >
                    <input
                      type="checkbox"
                      :checked="selectedQuestions.has(question.id)"
                      @change="toggleQuestion(question.id)"
                      class="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span class="text-sm text-gray-700">{{ question.text }}</span>
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
        <div class="mt-8">
          <button
            @click="handleSubmit"
            :disabled="!isFormValid"
            class="w-full px-8 py-4 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-[1.02] disabled:transform-none"
            style="background-color: #1E3B64;"
            onmouseover="this.style.backgroundColor='#0f2a4a'"
            onmouseout="this.style.backgroundColor='#1E3B64'"
          >
            <div class="flex items-center justify-center space-x-2">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>KYC-Bericht erstellen</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
