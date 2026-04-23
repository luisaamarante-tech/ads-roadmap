<script setup lang="ts">
// App shell with router view
</script>

<template>
  <div class="app">
    <router-view />
  </div>
</template>

<style>
/* BEM: Block - app (Global styles) */
.app {
  font-family:
    var(--unnnic-font-family, 'Inter'),
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* CSS Reset */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
