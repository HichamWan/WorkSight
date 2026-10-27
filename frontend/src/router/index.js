import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../auth'
import { can } from '../roles'

import AppLayout from '../layouts/AppLayout.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import EmployeesView from '../views/EmployeesView.vue'
import EmployeeDetailView from '../views/EmployeeDetailView.vue'
import AttendanceView from '../views/AttendanceView.vue'
import AlertsView from '../views/AlertsView.vue'
import ReportsView from '../views/ReportsView.vue'
import SettingsView from '../views/SettingsView.vue'

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
        { path: 'employees/:id', name: 'employee-detail', component: EmployeeDetailView },
        { path: 'attendance', name: 'attendance', component: AttendanceView },
        { path: 'alerts', name: 'alerts', component: AlertsView, meta: { permission: 'viewAlerts' } },
        { path: 'reports', name: 'reports', component: ReportsView, meta: { permission: 'viewReports' } },
        { path: 'settings', name: 'settings', component: SettingsView }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const { isAuthenticated, user } = useAuth()
  if (to.name !== 'login' && !isAuthenticated()) return { name: 'login' }
  if (to.name === 'login' && isAuthenticated()) return { name: 'dashboard' }

  // Block routes the user's role is not allowed to see.
  if (to.meta?.permission && !can(to.meta.permission, user.value)) {
    return { name: 'dashboard' }
  }
})

export default router
