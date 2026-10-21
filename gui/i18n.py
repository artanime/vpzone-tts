"""Soporte de idiomas (i18n) para la interfaz de VPZone TTS.

Idiomas disponibles: español, inglés, francés y ruso.
El idioma activo se guarda en la config (`language`) y también se puede
cambiar en caliente desde la interfaz.
"""

DEFAULT_LANGUAGE = "es"

# Nombre nativo de cada idioma (se muestra tal cual en el selector).
LANGUAGE_NAMES = {
    "es": "Español",
    "en": "English",
    "fr": "Français",
    "ru": "Русский"
}

LANGUAGE_BY_NAME = {name: code for code, name in LANGUAGE_NAMES.items()}

TRANSLATIONS = {

    "es": {
        "header.connection.connected": "Chat: conectado",
        "header.connection.disconnected": "Chat: desconectado",
        "header.connection.error": "Chat: error",
        "header.tts.active": "TTS: activo",
        "header.tts.stopped": "TTS: detenido",
        "header.queue": "Cola: {size}",
        "header.provider": "Proveedor: {name}",

        "settings.title": "Configuración",
        "settings.language": "Idioma",
        "settings.platform": "Plataforma",
        "settings.channel": "Canal",
        "settings.channel.placeholder": "nombre del canal",
        "settings.apply": "Aplicar",
        "settings.provider": "Proveedor",
        "settings.voice": "Voz",
        "settings.refresh": "Actualizar",
        "settings.volume": "Volumen: {value}%",
        "settings.speed": "Velocidad: {value}x",
        "settings.read_username": "Leer nombre del usuario",
        "settings.start": "Iniciar TTS",
        "settings.stop": "Detener",
        "settings.connect": "Conectar chat",
        "settings.disconnect": "Desconectar",
        "settings.woupi_account": "Cuenta Woupi",
        "voice.default": "Predeterminada",

        "filters.title": "Filtros",
        "filters.length": "Longitud máxima",
        "filters.url": "Quitar enlaces",
        "filters.emoji": "Convertir emojis",
        "filters.duplicate": "Anti repetición",
        "filters.spam": "Anti spam",
        "filters.replace": "Reemplazar texto",

        "test.title": "Probar voz",
        "test.placeholder": "Escribe algo para escuchar la voz...",
        "test.speak": "Hablar",
        "test.clear": "Vaciar cola",

        "log.title": "Actividad",
        "log.clear": "Limpiar",

        "log.ready": "Interfaz lista. Ajusta el canal y conecta.",
        "log.ws_hint": "Los mensajes del chat se leen cuando el WebSocket conecte.",
        "log.channel.empty": "Canal vacío, no se aplicó.",
        "log.channel.dubious": "Slug dudoso: usa minúsculas, 3-32 caracteres (a-z, 0-9, _ o -).",
        "log.channel.set": "Canal configurado: {channel}",
        "log.provider.selected": "Proveedor seleccionado: {provider}",
        "log.voice.selected": "Voz seleccionada: {voice}",
        "log.filter.on": "Filtro '{name}' activado",
        "log.filter.off": "Filtro '{name}' desactivado",
        "log.voices.updating": "Actualizando lista de voces...",
        "log.tts.started": "Motor TTS iniciado",
        "log.tts.stopped": "Motor TTS detenido",
        "log.already.connected": "Ya conectado al chat.",
        "log.connecting": "Conectando al chat...",
        "log.disconnected": "Desconectado del chat",
        "log.queue.cleared": "Cola vaciada ({count} mensajes)",
        "log.ws.connected": "WebSocket conectado al chat",
        "log.ws.notconnected": "WebSocket no conectado",
        "log.connection.error": "Error de conexión: {error}",
        "log.queued": "En cola: {text}",
        "log.blocked": "Bloqueado ({reason}): {text}",
        "log.speaking": "Hablando: {text}",
        "log.plugins.loaded": "Plugins: {count} cargados, {active} activos",
        "log.plugins.none": "Plugins: ninguno",
        "log.save.error": "No se pudo guardar la config: {error}",
        "log.language.changed": "Idioma cambiado: {language}",
        "log.platform.changed": "Plataforma cambiada: {platform}",

        "woupi.title": "Conectar con Woupi",
        "woupi.intro": "Autoriza esta aplicación en tu cuenta de Woupi. El proceso es seguro: no se comparten contraseñas ni se guardan secretos en el programa.",
        "woupi.client_id": "Client ID (público)",
        "woupi.client_id.placeholder": "client_id de la app pública",
        "woupi.connect": "Generar código",
        "woupi.code": "Tu código:",
        "woupi.open_browser": "Abrir navegador",
        "woupi.waiting": "Esperando que autorices en el navegador...",
        "woupi.success": "¡Autorizado! Conectando...",
        "woupi.error": "No se pudo autorizar: {error}",
        "woupi.close": "Cerrar",
        "woupi.missing_client": "Falta el Client ID de la app pública de Woupi.",
        "log.woupi.account": "Autorizando acceso a Woupi...",
        "log.woupi.connected": "Woupi autorizado correctamente"
    },

    "en": {
        "header.connection.connected": "Chat: connected",
        "header.connection.disconnected": "Chat: disconnected",
        "header.connection.error": "Chat: error",
        "header.tts.active": "TTS: active",
        "header.tts.stopped": "TTS: stopped",
        "header.queue": "Queue: {size}",
        "header.provider": "Provider: {name}",

        "settings.title": "Settings",
        "settings.language": "Language",
        "settings.platform": "Platform",
        "settings.channel": "Channel",
        "settings.channel.placeholder": "channel name",
        "settings.apply": "Apply",
        "settings.provider": "Provider",
        "settings.voice": "Voice",
        "settings.refresh": "Refresh",
        "settings.volume": "Volume: {value}%",
        "settings.speed": "Speed: {value}x",
        "settings.read_username": "Read username",
        "settings.start": "Start TTS",
        "settings.stop": "Stop",
        "settings.connect": "Connect chat",
        "settings.disconnect": "Disconnect",
        "settings.woupi_account": "Woupi account",
        "voice.default": "Default",

        "filters.title": "Filters",
        "filters.length": "Max length",
        "filters.url": "Remove links",
        "filters.emoji": "Convert emojis",
        "filters.duplicate": "Anti-repeat",
        "filters.spam": "Anti-spam",
        "filters.replace": "Replace text",

        "test.title": "Test voice",
        "test.placeholder": "Type something to hear the voice...",
        "test.speak": "Speak",
        "test.clear": "Clear queue",

        "log.title": "Activity",
        "log.clear": "Clear",

        "log.ready": "Interface ready. Set the channel and connect.",
        "log.ws_hint": "Chat messages are read when the WebSocket connects.",
        "log.channel.empty": "Empty channel, not applied.",
        "log.channel.dubious": "Suspicious slug: use lowercase, 3-32 chars (a-z, 0-9, _ or -).",
        "log.channel.set": "Channel set: {channel}",
        "log.provider.selected": "Provider selected: {provider}",
        "log.voice.selected": "Voice selected: {voice}",
        "log.filter.on": "Filter '{name}' enabled",
        "log.filter.off": "Filter '{name}' disabled",
        "log.voices.updating": "Refreshing voice list...",
        "log.tts.started": "TTS engine started",
        "log.tts.stopped": "TTS engine stopped",
        "log.already.connected": "Already connected to chat.",
        "log.connecting": "Connecting to chat...",
        "log.disconnected": "Disconnected from chat",
        "log.queue.cleared": "Queue cleared ({count} messages)",
        "log.ws.connected": "WebSocket connected to chat",
        "log.ws.notconnected": "WebSocket not connected",
        "log.connection.error": "Connection error: {error}",
        "log.queued": "Queued: {text}",
        "log.blocked": "Blocked ({reason}): {text}",
        "log.speaking": "Speaking: {text}",
        "log.plugins.loaded": "Plugins: {count} loaded, {active} active",
        "log.plugins.none": "Plugins: none",
        "log.save.error": "Could not save config: {error}",
        "log.language.changed": "Language changed: {language}",
        "log.platform.changed": "Platform changed: {platform}",

        "woupi.title": "Connect with Woupi",
        "woupi.intro": "Authorize this app on your Woupi account. The process is secure: no passwords are shared and no secrets are stored in the program.",
        "woupi.client_id": "Client ID (public)",
        "woupi.client_id.placeholder": "public app client_id",
        "woupi.connect": "Generate code",
        "woupi.code": "Your code:",
        "woupi.open_browser": "Open browser",
        "woupi.waiting": "Waiting for you to authorize in the browser...",
        "woupi.success": "Authorized! Connecting...",
        "woupi.error": "Could not authorize: {error}",
        "woupi.close": "Close",
        "woupi.missing_client": "Missing the public Woupi app Client ID.",
        "log.woupi.account": "Requesting Woupi access...",
        "log.woupi.connected": "Woupi authorized successfully"
    },

    "fr": {
        "header.connection.connected": "Chat : connecté",
        "header.connection.disconnected": "Chat : déconnecté",
        "header.connection.error": "Chat : erreur",
        "header.tts.active": "TTS : actif",
        "header.tts.stopped": "TTS : arrêté",
        "header.queue": "File : {size}",
        "header.provider": "Moteur : {name}",

        "settings.title": "Paramètres",
        "settings.language": "Langue",
        "settings.platform": "Plateforme",
        "settings.channel": "Chaîne",
        "settings.channel.placeholder": "nom de la chaîne",
        "settings.apply": "Appliquer",
        "settings.provider": "Moteur",
        "settings.voice": "Voix",
        "settings.refresh": "Actualiser",
        "settings.volume": "Volume : {value} %",
        "settings.speed": "Vitesse : {value}x",
        "settings.read_username": "Lire le nom de l'utilisateur",
        "settings.start": "Démarrer TTS",
        "settings.stop": "Arrêter",
        "settings.connect": "Connecter le chat",
        "settings.disconnect": "Déconnecter",
        "settings.woupi_account": "Compte Woupi",
        "voice.default": "Par défaut",

        "filters.title": "Filtres",
        "filters.length": "Longueur max",
        "filters.url": "Supprimer les liens",
        "filters.emoji": "Convertir les emojis",
        "filters.duplicate": "Anti-répétition",
        "filters.spam": "Anti-spam",
        "filters.replace": "Remplacer le texte",

        "test.title": "Tester la voix",
        "test.placeholder": "Écrivez quelque chose pour écouter la voix...",
        "test.speak": "Parler",
        "test.clear": "Vider la file",

        "log.title": "Activité",
        "log.clear": "Effacer",

        "log.ready": "Interface prête. Réglez la chaîne et connectez.",
        "log.ws_hint": "Les messages du chat sont lus lorsque le WebSocket se connecte.",
        "log.channel.empty": "Chaîne vide, non appliquée.",
        "log.channel.dubious": "Slug douteux : minuscules, 3-32 caractères (a-z, 0-9, _ ou -).",
        "log.channel.set": "Chaîne configurée : {channel}",
        "log.provider.selected": "Moteur sélectionné : {provider}",
        "log.voice.selected": "Voix sélectionnée : {voice}",
        "log.filter.on": "Filtre '{name}' activé",
        "log.filter.off": "Filtre '{name}' désactivé",
        "log.voices.updating": "Actualisation de la liste des voix...",
        "log.tts.started": "Moteur TTS démarré",
        "log.tts.stopped": "Moteur TTS arrêté",
        "log.already.connected": "Déjà connecté au chat.",
        "log.connecting": "Connexion au chat...",
        "log.disconnected": "Déconnecté du chat",
        "log.queue.cleared": "File vidée ({count} messages)",
        "log.ws.connected": "WebSocket connecté au chat",
        "log.ws.notconnected": "WebSocket non connecté",
        "log.connection.error": "Erreur de connexion : {error}",
        "log.queued": "En file : {text}",
        "log.blocked": "Bloqué ({reason}) : {text}",
        "log.speaking": "Lecture : {text}",
        "log.plugins.loaded": "Plugins : {count} chargés, {active} actifs",
        "log.plugins.none": "Plugins : aucun",
        "log.save.error": "Impossible d'enregistrer la config : {error}",
        "log.language.changed": "Langue changée : {language}",
        "log.platform.changed": "Plateforme changée : {platform}",

        "woupi.title": "Se connecter à Woupi",
        "woupi.intro": "Autorisez cette application sur votre compte Woupi. Le processus est sûr : aucun mot de passe n'est partagé et aucun secret n'est stocké dans le programme.",
        "woupi.client_id": "Client ID (public)",
        "woupi.client_id.placeholder": "client_id de l'app publique",
        "woupi.connect": "Générer le code",
        "woupi.code": "Votre code :",
        "woupi.open_browser": "Ouvrir le navigateur",
        "woupi.waiting": "En attente de votre autorisation dans le navigateur...",
        "woupi.success": "Autorisé ! Connexion...",
        "woupi.error": "Impossible d'autoriser : {error}",
        "woupi.close": "Fermer",
        "woupi.missing_client": "Client ID de l'application publique Woupi manquant.",
        "log.woupi.account": "Demande d'accès à Woupi...",
        "log.woupi.connected": "Woupi autorisé avec succès"
    },

    "ru": {
        "header.connection.connected": "Чат: подключён",
        "header.connection.disconnected": "Чат: отключён",
        "header.connection.error": "Чат: ошибка",
        "header.tts.active": "TTS: активен",
        "header.tts.stopped": "TTS: остановлен",
        "header.queue": "Очередь: {size}",
        "header.provider": "Провайдер: {name}",

        "settings.title": "Настройки",
        "settings.language": "Язык",
        "settings.platform": "Платформа",
        "settings.channel": "Канал",
        "settings.channel.placeholder": "имя канала",
        "settings.apply": "Применить",
        "settings.provider": "Провайдер",
        "settings.voice": "Голос",
        "settings.refresh": "Обновить",
        "settings.volume": "Громкость: {value}%",
        "settings.speed": "Скорость: {value}x",
        "settings.read_username": "Читать имя пользователя",
        "settings.start": "Запустить TTS",
        "settings.stop": "Остановить",
        "settings.connect": "Подключить чат",
        "settings.disconnect": "Отключить",
        "settings.woupi_account": "Аккаунт Woupi",
        "voice.default": "По умолчанию",

        "filters.title": "Фильтры",
        "filters.length": "Макс. длина",
        "filters.url": "Удалять ссылки",
        "filters.emoji": "Преобразовать эмодзи",
        "filters.duplicate": "Анти-повтор",
        "filters.spam": "Анти-спам",
        "filters.replace": "Заменять текст",

        "test.title": "Проверка голоса",
        "test.placeholder": "Введите текст, чтобы услышать голос...",
        "test.speak": "Говорить",
        "test.clear": "Очистить очередь",

        "log.title": "Активность",
        "log.clear": "Очистить",

        "log.ready": "Интерфейс готов. Укажите канал и подключитесь.",
        "log.ws_hint": "Сообщения чата читаются при подключении WebSocket.",
        "log.channel.empty": "Пустой канал, не применён.",
        "log.channel.dubious": "Подозрительный slug: строчные, 3-32 символа (a-z, 0-9, _ или -).",
        "log.channel.set": "Канал настроен: {channel}",
        "log.provider.selected": "Провайдер выбран: {provider}",
        "log.voice.selected": "Голос выбран: {voice}",
        "log.filter.on": "Фильтр '{name}' включён",
        "log.filter.off": "Фильтр '{name}' выключен",
        "log.voices.updating": "Обновление списка голосов...",
        "log.tts.started": "Движок TTS запущен",
        "log.tts.stopped": "Движок TTS остановлен",
        "log.already.connected": "Уже подключено к чату.",
        "log.connecting": "Подключение к чату...",
        "log.disconnected": "Отключено от чата",
        "log.queue.cleared": "Очередь очищена ({count} сообщений)",
        "log.ws.connected": "WebSocket подключён к чату",
        "log.ws.notconnected": "WebSocket не подключён",
        "log.connection.error": "Ошибка подключения: {error}",
        "log.queued": "В очереди: {text}",
        "log.blocked": "Заблокировано ({reason}): {text}",
        "log.speaking": "Чтение: {text}",
        "log.plugins.loaded": "Плагины: {count} загружено, {active} активно",
        "log.plugins.none": "Плагины: нет",
        "log.save.error": "Не удалось сохранить конфиг: {error}",
        "log.language.changed": "Язык изменён: {language}",
        "log.platform.changed": "Платформа изменена: {platform}",

        "woupi.title": "Подключить Woupi",
        "woupi.intro": "Авторизуйте это приложение в вашем аккаунте Woupi. Процесс безопасен: пароли не передаются и секреты не хранятся в программе.",
        "woupi.client_id": "Client ID (публичный)",
        "woupi.client_id.placeholder": "client_id публичного приложения",
        "woupi.connect": "Создать код",
        "woupi.code": "Ваш код:",
        "woupi.open_browser": "Открыть браузер",
        "woupi.waiting": "Ожидание авторизации в браузере...",
        "woupi.success": "Авторизовано! Подключение...",
        "woupi.error": "Не удалось авторизовать: {error}",
        "woupi.close": "Закрыть",
        "woupi.missing_client": "Отсутствует Client ID публичного приложения Woupi.",
        "log.woupi.account": "Запрос доступа к Woupi...",
        "log.woupi.connected": "Woupi успешно авторизован"
    }
}


class Translator:

    def __init__(self, language=DEFAULT_LANGUAGE):

        self.language = language if language in TRANSLATIONS else DEFAULT_LANGUAGE

    def set_language(self, language):

        if language in TRANSLATIONS:
            self.language = language

    def t(self, key, **kwargs):
        """Devuelve el texto traducido (con formato opcional)."""

        table = TRANSLATIONS.get(self.language) or TRANSLATIONS[DEFAULT_LANGUAGE]

        template = table.get(key)

        if template is None:
            template = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)

        if not kwargs:
            return template

        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template


# Instancia global usada por toda la interfaz.
i18n = Translator()
