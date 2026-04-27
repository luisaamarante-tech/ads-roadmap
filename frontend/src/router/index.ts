/**
 * Vue Router configuration for the VTEX Ads Public Roadmap.
 */

import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/roadmap',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
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

// Auth guard: redirect to /login if not authenticated
router.beforeEach((to) => {
  const isAuth = !!sessionStorage.getItem('roadmap_auth');
  if (!isAuth && to.name !== 'login') return { name: 'login' };
  if (isAuth && to.name === 'login') return { name: 'roadmap' };
});

export default router;
