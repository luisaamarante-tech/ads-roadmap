/**
 * Vue Router configuration for the Weni Public Roadmap.
 */

import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // BASE_URL é usado pelo Vite internamente
  routes: [
    {
      path: '/',
      redirect: '/roadmap',
    },
    {
      path: '/roadmap',
      name: 'roadmap',
      component: () => import('@/views/RoadmapView.vue'),
    },
    // Catch-all redirect to roadmap
    {
      path: '/:pathMatch(.*)*',
      redirect: '/roadmap',
    },
  ],
});

export default router;
