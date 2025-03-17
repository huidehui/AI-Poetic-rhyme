import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChatView from '../views/ChatView.vue'
import TravelView from '../views/TravelView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/chat/:poet',
      name: 'chat',
      component: ChatView,
      props: true
    },
    {
      path: '/travel/:poet',
      name: 'travel',
      component: TravelView,
      props: true
    }
  ]
})

export default router
