import { ref } from 'vue'

const LOCALE_KEY = 'worksight_locale'

export const locales = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '中文' },
  { code: 'ar', label: 'العربية' },
  { code: 'fr', label: 'Français' },
  { code: 'es', label: 'Español' }
]

const messages = {
  en: {
    appName: 'WorkSight',
    // nav
    dashboard: 'Dashboard', employees: 'Employees', attendance: 'Attendance', alerts: 'Alerts',
    logout: 'Log out', systemOnline: 'System online',
    // login
    welcomeBack: 'Welcome back',
    signInSubtitle: 'Sign in to the WorkSight management portal',
    createAccountTitle: 'Create account',
    signUpSubtitle: 'Set up your company workspace in seconds',
    username: 'Username', password: 'Password', email: 'Email',
    companyName: 'Company name', companyNameOptional: 'Company name (optional)',
    usernamePlaceholder: 'e.g. alice', chooseUsername: 'Choose a username',
    emailPlaceholder: 'you@company.com', passwordPlaceholder: '••••••••',
    passwordHint: 'At least 6 characters',
    signIn: 'Sign in', signingIn: 'Signing in…',
    createAccount: 'Create account', creatingAccount: 'Creating account…',
    noAccount: "Don't have an account?", haveAccount: 'Already have an account?',
    createOne: 'Create one', signInLink: 'Sign in',
    loginFailed: 'Login failed', registerFailed: 'Registration failed',
    // dashboard
    today: 'Today', checkedIn: 'Checked in', notCheckedIn: 'Not checked in',
    onTime: 'On time', late: 'Late',
    totalEmployees: 'Total employees', presentToday: 'Present today',
    lateArrivals: 'Late arrivals', overtimeHours: 'Overtime',
    attendanceTrend: 'Attendance trend', present: 'Present', absent: 'Absent',
    checkedInPct: 'checked in',
    // employees
    searchEmployees: 'Search employees…', addEmployee: '+ Add employee',
    employee: 'Employee', code: 'Code', department: 'Department',
    position: 'Position', contact: 'Contact', faceId: 'Face ID',
    registered: 'Registered', notSet: 'Not set', delete: 'Delete',
    addEmployeeTitle: 'Add employee', employeeCode: 'Employee code',
    firstName: 'First name', lastName: 'Last name', phone: 'Phone',
    cancel: 'Cancel', save: 'Save', saving: 'Saving…',
    loadingEmployees: 'Loading employees…', noEmployees: 'No employees found.',
    deleteConfirm: 'Delete {name}? This cannot be undone.',
    // attendance
    records: 'records', searchByEmployee: 'Search by employee…',
    date: 'Date', checkIn: 'Check in', checkOut: 'Check out',
    worked: 'Worked', overtime: 'Overtime', undertime: 'Undertime',
    status: 'Status',
    loadingAttendance: 'Loading attendance records…', noAttendance: 'No attendance records found.',
    // alerts
    activeAlerts: 'Active alerts', total: 'total',
    loadingAlerts: 'Loading alerts…', noAlerts: 'No alerts — everything looks good.'
  },
  zh: {
    appName: 'WorkSight',
    dashboard: '仪表盘', employees: '员工管理', attendance: '考勤记录', alerts: '预警通知',
    logout: '退出登录', systemOnline: '系统在线',
    welcomeBack: '欢迎回来',
    signInSubtitle: '登录 WorkSight 管理平台',
    createAccountTitle: '创建账户',
    signUpSubtitle: '几秒钟即可创建您的企业工作区',
    username: '用户名', password: '密码', email: '邮箱',
    companyName: '公司名称', companyNameOptional: '公司名称（可选）',
    usernamePlaceholder: '例如：alice', chooseUsername: '请输入用户名',
    emailPlaceholder: 'you@company.com', passwordPlaceholder: '••••••••',
    passwordHint: '至少 6 个字符',
    signIn: '登录', signingIn: '登录中…',
    createAccount: '创建账户', creatingAccount: '创建中…',
    noAccount: '还没有账户？', haveAccount: '已有账户？',
    createOne: '立即注册', signInLink: '登录',
    loginFailed: '登录失败', registerFailed: '注册失败',
    today: '今日', checkedIn: '已签到', notCheckedIn: '未签到',
    onTime: '准时', late: '迟到',
    totalEmployees: '员工总数', presentToday: '今日出勤',
    lateArrivals: '迟到人数', overtimeHours: '加班',
    attendanceTrend: '出勤趋势', present: '出勤', absent: '缺勤',
    checkedInPct: '已签到',
    searchEmployees: '搜索员工…', addEmployee: '+ 添加员工',
    employee: '员工', code: '工号', department: '部门',
    position: '职位', contact: '联系方式', faceId: '人脸识别',
    registered: '已录入', notSet: '未设置', delete: '删除',
    addEmployeeTitle: '添加员工', employeeCode: '员工编号',
    firstName: '名', lastName: '姓', phone: '电话',
    cancel: '取消', save: '保存', saving: '保存中…',
    loadingEmployees: '正在加载员工…', noEmployees: '未找到员工。',
    deleteConfirm: '删除 {name}？此操作不可撤销。',
    records: '条记录', searchByEmployee: '按员工搜索…',
    date: '日期', checkIn: '签到时间', checkOut: '签退时间',
    worked: '工作时长', overtime: '加班', undertime: '不足时长',
    status: '状态',
    loadingAttendance: '正在加载考勤记录…', noAttendance: '暂无考勤记录。',
    activeAlerts: '活跃预警', total: '共',
    loadingAlerts: '正在加载预警…', noAlerts: '暂无预警 — 一切正常。'
  },
  ar: {
    appName: 'WorkSight',
    dashboard: 'لوحة التحكم', employees: 'الموظفون', attendance: 'الحضور', alerts: 'التنبيهات',
    logout: 'تسجيل الخروج', systemOnline: 'النظام متصل',
    welcomeBack: 'مرحبًا بعودتك',
    signInSubtitle: 'قم بتسجيل الدخول إلى بوابة إدارة WorkSight',
    createAccountTitle: 'إنشاء حساب',
    signUpSubtitle: 'أنشئ مساحة عمل شركتك في ثوانٍ',
    username: 'اسم المستخدم', password: 'كلمة المرور', email: 'البريد الإلكتروني',
    companyName: 'اسم الشركة', companyNameOptional: 'اسم الشركة (اختياري)',
    usernamePlaceholder: 'مثال: alice', chooseUsername: 'اختر اسم مستخدم',
    emailPlaceholder: 'you@company.com', passwordPlaceholder: '••••••••',
    passwordHint: '6 أحرف على الأقل',
    signIn: 'تسجيل الدخول', signingIn: 'جارٍ تسجيل الدخول…',
    createAccount: 'إنشاء حساب', creatingAccount: 'جارٍ إنشاء الحساب…',
    noAccount: 'ليس لديك حساب؟', haveAccount: 'لديك حساب بالفعل؟',
    createOne: 'أنشئ حسابًا', signInLink: 'تسجيل الدخول',
    loginFailed: 'فشل تسجيل الدخول', registerFailed: 'فشل التسجيل',
    today: 'اليوم', checkedIn: 'سجّل الحضور', notCheckedIn: 'لم يسجّل الحضور',
    onTime: 'في الوقت', late: 'متأخر',
    totalEmployees: 'إجمالي الموظفين', presentToday: 'الحاضرون اليوم',
    lateArrivals: 'المتأخرون', overtimeHours: 'ساعات إضافية',
    attendanceTrend: 'اتجاه الحضور', present: 'حاضر', absent: 'غائب',
    checkedInPct: 'سجّلوا الحضور',
    searchEmployees: 'ابحث عن موظف…', addEmployee: '+ إضافة موظف',
    employee: 'الموظف', code: 'الرقم الوظيفي', department: 'القسم',
    position: 'المنصب', contact: 'التواصل', faceId: 'بصمة الوجه',
    registered: 'مسجّل', notSet: 'غير مسجّل', delete: 'حذف',
    addEmployeeTitle: 'إضافة موظف', employeeCode: 'الرقم الوظيفي',
    firstName: 'الاسم الأول', lastName: 'اسم العائلة', phone: 'الهاتف',
    cancel: 'إلغاء', save: 'حفظ', saving: 'جارٍ الحفظ…',
    loadingEmployees: 'جارٍ تحميل الموظفين…', noEmployees: 'لا يوجد موظفون.',
    deleteConfirm: 'حذف {name}؟ لا يمكن التراجع عن هذا الإجراء.',
    records: 'سجلات', searchByEmployee: 'ابحث حسب الموظف…',
    date: 'التاريخ', checkIn: 'الحضور', checkOut: 'الانصراف',
    worked: 'العمل', overtime: 'إضافي', undertime: 'ناقص',
    status: 'الحالة',
    loadingAttendance: 'جارٍ تحميل سجلات الحضور…', noAttendance: 'لا توجد سجلات حضور.',
    activeAlerts: 'التنبيهات النشطة', total: 'إجمالي',
    loadingAlerts: 'جارٍ تحميل التنبيهات…', noAlerts: 'لا توجد تنبيهات — كل شيء على ما يرام.'
  },
  fr: {
    appName: 'WorkSight',
    dashboard: 'Tableau de bord', employees: 'Employés', attendance: 'Présence', alerts: 'Alertes',
    logout: 'Se déconnecter', systemOnline: 'Système en ligne',
    welcomeBack: 'Bon retour',
    signInSubtitle: 'Connectez-vous au portail de gestion WorkSight',
    createAccountTitle: 'Créer un compte',
    signUpSubtitle: 'Configurez votre espace entreprise en quelques secondes',
    username: "Nom d'utilisateur", password: 'Mot de passe', email: 'E-mail',
    companyName: "Nom de l'entreprise", companyNameOptional: "Nom de l'entreprise (facultatif)",
    usernamePlaceholder: 'ex. alice', chooseUsername: "Choisissez un nom d'utilisateur",
    emailPlaceholder: 'vous@entreprise.com', passwordPlaceholder: '••••••••',
    passwordHint: 'Au moins 6 caractères',
    signIn: 'Se connecter', signingIn: 'Connexion…',
    createAccount: 'Créer le compte', creatingAccount: 'Création…',
    noAccount: "Pas encore de compte ?", haveAccount: 'Vous avez déjà un compte ?',
    createOne: 'Créez-en un', signInLink: 'Se connecter',
    loginFailed: 'Échec de la connexion', registerFailed: "Échec de l'inscription",
    today: "Aujourd'hui", checkedIn: 'Pointés', notCheckedIn: 'Non pointés',
    onTime: "À l'heure", late: 'En retard',
    totalEmployees: 'Employés au total', presentToday: 'Présents aujourd’hui',
    lateArrivals: 'Retards', overtimeHours: 'Heures sup.',
    attendanceTrend: 'Tendance de présence', present: 'Présent', absent: 'Absent',
    checkedInPct: 'pointés',
    searchEmployees: 'Rechercher des employés…', addEmployee: '+ Ajouter un employé',
    employee: 'Employé', code: 'Code', department: 'Département',
    position: 'Poste', contact: 'Contact', faceId: 'Reconnaissance faciale',
    registered: 'Enregistré', notSet: 'Non défini', delete: 'Supprimer',
    addEmployeeTitle: 'Ajouter un employé', employeeCode: 'Code employé',
    firstName: 'Prénom', lastName: 'Nom', phone: 'Téléphone',
    cancel: 'Annuler', save: 'Enregistrer', saving: 'Enregistrement…',
    loadingEmployees: 'Chargement des employés…', noEmployees: 'Aucun employé trouvé.',
    deleteConfirm: 'Supprimer {name} ? Cette action est irréversible.',
    records: 'enregistrements', searchByEmployee: 'Rechercher par employé…',
    date: 'Date', checkIn: 'Arrivée', checkOut: 'Départ',
    worked: 'Travaillé', overtime: 'Supplément', undertime: 'Manquant',
    status: 'Statut',
    loadingAttendance: 'Chargement des présences…', noAttendance: 'Aucun enregistrement de présence.',
    activeAlerts: 'Alertes actives', total: 'au total',
    loadingAlerts: 'Chargement des alertes…', noAlerts: 'Aucune alerte — tout va bien.'
  },
  es: {
    appName: 'WorkSight',
    dashboard: 'Panel', employees: 'Empleados', attendance: 'Asistencia', alerts: 'Alertas',
    logout: 'Cerrar sesión', systemOnline: 'Sistema en línea',
    welcomeBack: 'Bienvenido de nuevo',
    signInSubtitle: 'Inicia sesión en el portal de gestión WorkSight',
    createAccountTitle: 'Crear cuenta',
    signUpSubtitle: 'Configura el espacio de tu empresa en segundos',
    username: 'Usuario', password: 'Contraseña', email: 'Correo electrónico',
    companyName: 'Nombre de la empresa', companyNameOptional: 'Nombre de la empresa (opcional)',
    usernamePlaceholder: 'p. ej. alice', chooseUsername: 'Elige un nombre de usuario',
    emailPlaceholder: 'tu@empresa.com', passwordPlaceholder: '••••••••',
    passwordHint: 'Al menos 6 caracteres',
    signIn: 'Iniciar sesión', signingIn: 'Iniciando sesión…',
    createAccount: 'Crear cuenta', creatingAccount: 'Creando cuenta…',
    noAccount: '¿No tienes cuenta?', haveAccount: '¿Ya tienes una cuenta?',
    createOne: 'Crea una', signInLink: 'Iniciar sesión',
    loginFailed: 'Error al iniciar sesión', registerFailed: 'Error al registrarse',
    today: 'Hoy', checkedIn: 'Registrados', notCheckedIn: 'Sin registrar',
    onTime: 'A tiempo', late: 'Tarde',
    totalEmployees: 'Empleados totales', presentToday: 'Presentes hoy',
    lateArrivals: 'Llegadas tarde', overtimeHours: 'Horas extra',
    attendanceTrend: 'Tendencia de asistencia', present: 'Presente', absent: 'Ausente',
    checkedInPct: 'registrados',
    searchEmployees: 'Buscar empleados…', addEmployee: '+ Añadir empleado',
    employee: 'Empleado', code: 'Código', department: 'Departamento',
    position: 'Puesto', contact: 'Contacto', faceId: 'Reconocimiento facial',
    registered: 'Registrado', notSet: 'Sin configurar', delete: 'Eliminar',
    addEmployeeTitle: 'Añadir empleado', employeeCode: 'Código de empleado',
    firstName: 'Nombre', lastName: 'Apellido', phone: 'Teléfono',
    cancel: 'Cancelar', save: 'Guardar', saving: 'Guardando…',
    loadingEmployees: 'Cargando empleados…', noEmployees: 'No se encontraron empleados.',
    deleteConfirm: '¿Eliminar a {name}? Esta acción no se puede deshacer.',
    records: 'registros', searchByEmployee: 'Buscar por empleado…',
    date: 'Fecha', checkIn: 'Entrada', checkOut: 'Salida',
    worked: 'Trabajado', overtime: 'Extra', undertime: 'Faltante',
    status: 'Estado',
    loadingAttendance: 'Cargando registros de asistencia…', noAttendance: 'No hay registros de asistencia.',
    activeAlerts: 'Alertas activas', total: 'en total',
    loadingAlerts: 'Cargando alertas…', noAlerts: 'Sin alertas — todo en orden.'
  }
}

const locale = ref(localStorage.getItem(LOCALE_KEY) || 'en')

function applyDirection() {
  document.documentElement.dir = locale.value === 'ar' ? 'rtl' : 'ltr'
}
applyDirection()

export function useI18n() {
  function t(key, params) {
    let text = messages[locale.value]?.[key] ?? messages.en[key] ?? key
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        text = text.replace(`{${k}}`, v)
      }
    }
    return text
  }

  function setLocale(code) {
    if (!messages[code]) return
    locale.value = code
    localStorage.setItem(LOCALE_KEY, code)
    applyDirection()
  }

  return { t, locale, setLocale, locales }
}
