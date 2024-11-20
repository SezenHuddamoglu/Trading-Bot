// import { createRouter, createWebHistory } from 'vue-router'

// const router = createRouter({
//   history: createWebHistory(import.meta.env.BASE_URL),
//   routes: [
//     // {
//     //   path: '/',
//     //   name: 'home',
//     //   component: HomeView,
//     // },
//   ],
// })

// export default router

// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../pages/Dashboard.vue'

const routes = [{ path: '/', component: Dashboard }]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
