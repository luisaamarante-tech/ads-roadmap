<template>
  <unnnic-modal
    v-if="showModal"
    :text="'Request Feature'"
    scheme="neutral"
    @close="handleClose"
  >
    <div class="feature-request-form">
      <p class="feature-request-form__description">
        Submit a feature request for the VTEX Agentic CX Roadmap. Our team will
        review and triage your request in the selected module's backlog.
      </p>

      <form aria-label="Feature request form" @submit.prevent="handleSubmit">
        <!-- Module Selection -->
        <div class="form-field">
          <label for="module-select" class="form-field__label">
            Module <span aria-hidden="true">*</span>
          </label>
          <div v-if="isLoadingModules" class="form-field__loading">
            Loading modules...
          </div>
          <select
            v-else
            id="module-select"
            v-model="form.moduleId"
            class="form-field__select"
            required
            :disabled="modules.length === 0 || isSubmitting"
            :aria-required="true"
            :aria-invalid="!!errors.moduleId"
            :aria-describedby="errors.moduleId ? 'module-error' : undefined"
          >
            <option value="" disabled>
              {{
                modules.length === 0
                  ? 'No modules available'
                  : 'Select a module'
              }}
            </option>
            <option
              v-for="module in modules"
              :key="module.id"
              :value="module.id"
            >
              {{ module.name }}
            </option>
          </select>
          <span
            v-if="errors.moduleId"
            id="module-error"
            class="form-field__error"
            role="alert"
            >{{ errors.moduleId }}</span
          >
        </div>

        <!-- Title -->
        <div class="form-field">
          <unnnic-input
            id="title-input"
            v-model="form.title"
            :label="'Title'"
            :placeholder="'Brief summary of your feature request'"
            :maxlength="200"
            :disabled="isSubmitting"
            required
            :aria-required="true"
            :aria-invalid="!!errors.title"
            :aria-describedby="errors.title ? 'title-error' : undefined"
          />
          <span
            v-if="errors.title"
            id="title-error"
            class="form-field__error"
            role="alert"
            >{{ errors.title }}</span
          >
        </div>

        <!-- Description -->
        <div class="form-field">
          <unnnic-text-area
            id="description-input"
            v-model="form.description"
            :label="'Description'"
            :placeholder="'Describe the problem you are trying to solve and the desired outcome'"
            :maxlength="5000"
            :rows="5"
            :disabled="isSubmitting"
            required
            :aria-required="true"
            :aria-invalid="!!errors.description"
            :aria-describedby="
              errors.description ? 'description-error' : undefined
            "
          />
          <span
            v-if="errors.description"
            id="description-error"
            class="form-field__error"
            role="alert"
            >{{ errors.description }}</span
          >
        </div>

        <!-- Contact Email -->
        <div class="form-field">
          <unnnic-input
            id="email-input"
            v-model="form.contactEmail"
            :label="'Contact Email'"
            :placeholder="'your.email@example.com'"
            type="email"
            :disabled="isSubmitting"
            required
            :aria-required="true"
            :aria-invalid="!!errors.contactEmail"
            :aria-describedby="errors.contactEmail ? 'email-error' : undefined"
          />
          <span
            v-if="errors.contactEmail"
            id="email-error"
            class="form-field__error"
            role="alert"
            >{{ errors.contactEmail }}</span
          >
        </div>

        <!-- Honeypot field (hidden) -->
        <input
          v-model="form.website"
          type="text"
          name="website"
          tabindex="-1"
          autocomplete="off"
          aria-hidden="true"
          style="position: absolute; left: -9999px"
        />

        <!-- Submit/Cancel buttons -->
        <div class="form-actions">
          <unnnic-button
            type="secondary"
            :text="'Cancel'"
            :disabled="isSubmitting"
            @click="handleClose"
          />
          <unnnic-button
            type="primary"
            :text="isSubmitting ? 'Submitting...' : 'Submit Request'"
            :disabled="isSubmitting || !isFormValid"
            :loading="isSubmitting"
            @click="handleSubmit"
          />
        </div>

        <!-- Success message -->
        <div v-if="successMessage" class="success-message">
          <unnnic-alert
            :text="successMessage"
            :title="'Feature Request Submitted'"
            type="success"
            @close="handleClose"
          >
            <template v-if="issueUrl" #description>
              <p>
                Your request has been created as
                <a :href="issueUrl" target="_blank" rel="noopener noreferrer">{{
                  issueKey
                }}</a>
              </p>
            </template>
          </unnnic-alert>
        </div>

        <!-- Error message -->
        <div v-if="errorMessage" class="error-message">
          <unnnic-alert
            :text="errorMessage"
            type="error"
            @close="errorMessage = ''"
          />
        </div>
      </form>
    </div>
  </unnnic-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  getFeatureRequestModules,
  createFeatureRequest,
} from '@/services/roadmapService';
import type { Module, FeatureRequestPayload } from '@/types/roadmap';

const props = defineProps<{
  show: boolean;
  availableModules?: Module[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'submitted', issueKey: string): void;
}>();

// Form state
const form = ref<FeatureRequestPayload>({
  moduleId: '',
  title: '',
  description: '',
  contactEmail: '',
  website: '',
});

const errors = ref<Record<string, string>>({});
const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const issueKey = ref('');
const issueUrl = ref('');

// Modules - use provided modules or load from API as fallback
const modules = ref<Module[]>([]);
const isLoadingModules = ref(false);

const showModal = computed(() => props.show);

const isFormValid = computed(() => {
  return (
    form.value.moduleId &&
    form.value.title.length >= 3 &&
    form.value.description.length >= 10 &&
    form.value.contactEmail.includes('@')
  );
});

// Load modules when modal opens
watch(
  () => props.show,
  async (newVal) => {
    if (newVal) {
      // Use provided modules if available, otherwise load from API
      if (props.availableModules && props.availableModules.length > 0) {
        modules.value = props.availableModules;
      } else if (modules.value.length === 0) {
        await loadModules();
      }
    }
  },
  { immediate: true },
);

async function loadModules() {
  isLoadingModules.value = true;
  errorMessage.value = '';

  try {
    const response = await getFeatureRequestModules();
    modules.value = response.modules || [];
  } catch {
    errorMessage.value =
      'Failed to load modules. Please try again or contact support.';
    modules.value = [];
  } finally {
    isLoadingModules.value = false;
  }
}

function validateForm(): boolean {
  errors.value = {};

  if (!form.value.moduleId) {
    errors.value.moduleId = 'Module is required';
  }

  if (!form.value.title) {
    errors.value.title = 'Title is required';
  } else if (form.value.title.length < 3) {
    errors.value.title = 'Title must be at least 3 characters';
  } else if (form.value.title.length > 200) {
    errors.value.title = 'Title must be at most 200 characters';
  }

  if (!form.value.description) {
    errors.value.description = 'Description is required';
  } else if (form.value.description.length < 10) {
    errors.value.description = 'Description must be at least 10 characters';
  } else if (form.value.description.length > 5000) {
    errors.value.description = 'Description must be at most 5000 characters';
  }

  if (!form.value.contactEmail) {
    errors.value.contactEmail = 'Contact email is required';
  } else if (!form.value.contactEmail.includes('@')) {
    errors.value.contactEmail = 'Please enter a valid email address';
  }

  return Object.keys(errors.value).length === 0;
}

async function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    // Generate idempotency key
    const idempotencyKey = `${Date.now()}-${Math.random().toString(36).substring(7)}`;

    const response = await createFeatureRequest(form.value, idempotencyKey);

    if (response.success) {
      successMessage.value =
        response.message || 'Feature request submitted successfully!';
      issueKey.value = response.issueKey;
      issueUrl.value = response.issueUrl || '';

      // Emit success event
      emit('submitted', response.issueKey);

      // Reset form
      setTimeout(() => {
        resetForm();
        handleClose();
      }, 3000);
    }
  } catch (error: unknown) {
    const err = error as {
      response?: {
        status?: number;
        data?: { message?: string };
        headers?: Record<string, string>;
      };
    };
    if (err.response?.status === 429) {
      // Rate limit exceeded
      const retryAfter = err.response?.headers?.['retry-after'];
      if (retryAfter) {
        errorMessage.value = `Too many requests. Please wait ${retryAfter} seconds and try again.`;
      } else {
        errorMessage.value =
          'Too many requests. You can submit up to 3 requests per minute and 10 per hour. Please wait and try again.';
      }
    } else if (err.response?.data?.message) {
      errorMessage.value = err.response.data.message;
    } else if (err.response?.status && err.response.status >= 500) {
      errorMessage.value =
        'Service temporarily unavailable. Please try again in a few minutes.';
    } else {
      errorMessage.value =
        'Failed to submit feature request. Please check your information and try again.';
    }
  } finally {
    isSubmitting.value = false;
  }
}

function handleClose() {
  if (!isSubmitting.value) {
    resetForm();
    emit('close');
  }
}

function resetForm() {
  form.value = {
    moduleId: '',
    title: '',
    description: '',
    contactEmail: '',
    website: '',
  };
  errors.value = {};
  successMessage.value = '';
  errorMessage.value = '';
  issueKey.value = '';
  issueUrl.value = '';
}
</script>

<style scoped>
.feature-request-form {
  padding: 1rem;
}

.feature-request-form__description {
  margin-bottom: 1.5rem;
  color: #67738b;
  font-size: 0.875rem;
  line-height: 1.5;
}

.form-field {
  margin-bottom: 1.5rem;
}

.form-field__label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: #3b414d;
}

.form-field__select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d0d3d9;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #3b414d;
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.2s;
}

.form-field__select:hover {
  border-color: #9ca3af;
}

.form-field__select:focus {
  outline: none;
  border-color: #009e96;
  box-shadow: 0 0 0 3px rgb(0 158 150 / 10%);
}

.form-field__loading {
  padding: 0.75rem;
  color: #67738b;
  font-size: 0.875rem;
  font-style: italic;
}

.form-field__error {
  display: block;
  margin-top: 0.25rem;
  color: #e63c3c;
  font-size: 0.75rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.success-message,
.error-message {
  margin-top: 1rem;
}
</style>
