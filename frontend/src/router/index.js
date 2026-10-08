import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../auth'

import AppLayout from '../layouts/AppLayout.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import EmployeesView from '../views/EmployeesView.vue'
import AttendanceView from '../views/AttendanceView.vue'
import AlertsView from '../views/AlertsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: 'employees', name: 'employees', component: EmployeesView },
        { path: 'attendance', name: 'attendance', component: AttendanceView },
        { path: 'alerts', name: 'alerts', component: AlertsView }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const { isAuthenticated } = useAuth()
  if (to.name !== 'login' && !isAuthenticated()) return { name: 'login' }
  if (to.name === 'login' && isAuthenticated()) return { name: 'dashboard' }
})

export default router
