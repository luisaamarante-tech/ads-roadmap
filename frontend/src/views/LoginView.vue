<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { env } from '@/utils/env';

const router = useRouter();

const username = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);

function handleLogin() {
  error.value = '';

  if (!username.value || !password.value) {
    error.value = 'Please fill in all fields.';
    return;
  }

  isLoading.value = true;

  // Small delay for UX feedback
  setTimeout(() => {
    if (
      username.value === env.authUsername &&
      password.value === env.authPassword
    ) {
      sessionStorage.setItem('roadmap_auth', '1');
      router.push({ name: 'roadmap' });
    } else {
      error.value = 'Invalid username or password.';
      isLoading.value = false;
    }
  }, 300);
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-card__logo">
        <span class="login-card__brand">VTEX Ads</span>
        <span class="login-card__brand-suffix"> Roadmap</span>
      </div>

      <h1 class="login-card__title">Sign in</h1>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="login-form__field">
          <label for="username" class="login-form__label">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="login-form__input"
            autocomplete="username"
            :disabled="isLoading"
            placeholder="Enter your username"
          />
        </div>

        <div class="login-form__field">
          <label for="password" class="login-form__label">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="login-form__input"
            autocomplete="current-password"
            :disabled="isLoading"
            placeholder="Enter your password"
          />
        </div>

        <p v-if="error" class="login-form__error" role="alert">
          {{ error }}
        </p>

        <button
          type="submit"
          class="login-form__submit"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    180deg,
    #f8fafa 0%,
    #fff 100%
  );
  padding: 1rem;
}

.login-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 24px rgb(0 0 0 / 6%);
}

.login-card__logo {
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.login-card__brand {
  color: #F71963;
  font-weight: 700;
}

.login-card__brand-suffix {
  color: #67738b;
}

.login-card__title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  text-align: center;
  margin: 0 0 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-form__field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.login-form__label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #3b414d;
}

.login-form__input {
  padding: 0.75rem 1rem;
  border: 1px solid #d0d3d9;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #1a1a1a;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.login-form__input:focus {
  border-color: #F71963;
  box-shadow: 0 0 0 3px rgb(247 25 99 / 10%);
}

.login-form__input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.login-form__error {
  font-size: 0.8125rem;
  color: #e63c3c;
  margin: 0;
  text-align: center;
}

.login-form__submit {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #F71963;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.login-form__submit:hover:not(:disabled) {
  background: #dd1259;
}

.login-form__submit:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}
</style>
