<template>
  <unnnic-modal
    v-if="showModal"
    :text="'New Request'"
    scheme="neutral"
    @close="handleClose"
  >
    <div class="feature-request-form">
      <p class="feature-request-form__description">
        Bring a problem or opportunity to the VTEX Ads team. We'll review,
        triage and add it to our backlog.
      </p>

      <form aria-label="Feature request form" @submit.prevent="handleSubmit">
        <!-- Title -->
        <div class="form-field">
          <unnnic-input
            id="title-input"
            v-model="form.title"
            :label="'What is the problem or opportunity?'"
            :placeholder="'Brief summary of the problem'"
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
            :label="'Context and business impact'"
            :placeholder="'Describe the context, who is affected and what the business impact is'"
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

        <!-- Module Selection -->
        <div class="form-field">
          <label for="module-select" class="form-field__label">
            Media <span aria-hidden="true">*</span>
          </label>
          <div v-if="isLoadingModules" class="form-field__loading">
            Loading media types...
          </div>
          <p v-else-if="modules.length === 0" class="form-field__empty-modules">
            Media types will appear as items are added to the roadmap.
          </p>
          <select
            v-else
            id="module-select"
            v-model="form.moduleId"
            class="form-field__select"
            required
            :disabled="isSubmitting"
            :aria-required="true"
            :aria-invalid="!!errors.moduleId"
            :aria-describedby="errors.moduleId ? 'module-error' : undefined"
          >
            <option value="" disabled>Select a media type</option>
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

        <!-- Product Pillar -->
        <div class="form-field">
          <label for="pillar-select" class="form-field__label">
            Product Pillar <span aria-hidden="true">*</span>
          </label>
          <select
            id="pillar-select"
            v-model="form.pillar"
            class="form-field__select"
            required
            :disabled="isSubmitting"
            :aria-required="true"
            :aria-invalid="!!errors.pillar"
            :aria-describedby="errors.pillar ? 'pillar-error' : undefined"
          >
            <option value="" disabled>Select a pillar</option>
            <option value="Campaign Creation">Campaign Creation</option>
            <option value="Management & Optimization">Management &amp; Optimization</option>
            <option value="Billing & Invoicing">Billing &amp; Invoicing</option>
            <option value="Reporting & Analytics">Reporting &amp; Analytics</option>
            <option value="Daily Operations">Daily Operations</option>
            <option value="Other">Other</option>
          </select>
          <span
            v-if="errors.pillar"
            id="pillar-error"
            class="form-field__error"
            role="alert"
            >{{ errors.pillar }}</span
          >
        </div>

        <!-- Contact Email -->
        <div class="form-field">
          <unnnic-input
            id="email-input"
            v-model="form.contactEmail"
            :label="'Contact Email'"
            :placeholder="'your@vtex.com'"
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
          <button
            type="button"
            class="form-actions__cancel"
            :disabled="isSubmitting"
            @click="handleClose"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="form-actions__submit"
            :class="{ 'form-actions__submit--active': isFormValid && !isSubmitting }"
            :disabled="isSubmitting || !isFormValid"
            @click="handleSubmit"
          >
            {{ isSubmitting ? 'Submitting...' : 'Submit Request' }}
          </button>
        </div>

        <!-- Success message -->
        <div v-if="successMessage" class="success-message">
          <div class="success-message__title">✅ Request received! 🎉</div>
          <p class="success-message__body">
            Your request has been added to the VTEX Ads product backlog.
            Our team will review and prioritize it.
          </p>
          <p v-if="issueUrl && issueKey" class="success-message__link">
            <a
              :href="issueUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="success-message__jira-link"
            >View your request in Jira → {{ issueKey }}</a>
          </p>
          <button
            type="button"
            class="success-message__close"
            @click="handleClose"
          >
            Close
          </button>
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
  pillar: '',
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
    form.value.pillar &&
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
    errors.value.moduleId = 'Media type is required';
  }

  if (!form.value.pillar) {
    errors.value.pillar = 'Product pillar is required';
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
    pillar: '',
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
  color: #9ca3af;
  font-size: 0.8125rem;
  line-height: 1.5;
  text-align: center;
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

.form-field__empty-modules {
  padding: 0.75rem;
  color: #67738b;
  font-size: 0.875rem;
  font-style: italic;
  margin: 0;
  border: 1px dashed #e8e8e8;
  border-radius: 8px;
  background: #f8f8f8;
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
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.form-actions__cancel {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.5rem 0.75rem;
  transition: color 0.2s;
}

.form-actions__cancel:hover:not(:disabled) {
  color: #6b7280;
}

.form-actions__cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions__submit {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: not-allowed;
  background: #e5e7eb;
  color: #9ca3af;
  transition: background 0.2s, color 0.2s;
}

.form-actions__submit--active {
  background: #F71963;
  color: #fff;
  cursor: pointer;
}

.form-actions__submit--active:hover {
  background: #dd1259;
}

.success-message {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  text-align: center;
}

.success-message__title {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.success-message__body {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.75rem;
}

.success-message__link {
  margin: 0 0 1rem;
}

.success-message__jira-link {
  color: #F71963;
  font-weight: 500;
  text-decoration: none;
}

.success-message__jira-link:hover {
  text-decoration: underline;
}

.success-message__close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.success-message__close:hover {
  color: #6b7280;
}

.error-message {
  margin-top: 1rem;
}
</style>
