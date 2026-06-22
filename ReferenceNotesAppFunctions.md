# Bitácora de Desarrollo - Fast Track Club

Este documento centraliza el conocimiento técnico, las implementaciones clave y el contexto arquitectónico de la aplicación para referencia futura.

---

## 🏎️ Descripción General del Proyecto
**Fast Track Club** es una plataforma de telemetría de alto rendimiento.
- **Arquitectura**: MVVM con Jetpack Compose.
- **Base de Datos**: Room (Persistencia de usuarios, vehículos, viajes y logros).
- **Seguimiento**: `LocationTrackingService` (Foreground Service) que calcula velocidad y Fuerzas G mediante GPS.
- **Mapas**: Integración con MapLibre para visualización de rutas con heatmaps de velocidad.
- **Android Auto**: Extensión de la experiencia al vehículo mediante la Car App Library.

---

## 🛠️ Implementaciones por Módulo

### 1. Telemetría y Servicio de Ubicación (`LocationTrackingService.kt`)
- **Cálculo de Fuerzas G**: Se deriva de la diferencia de velocidad (`m/s`) entre actualizaciones de GPS dividida por el tiempo y la constante de gravedad ($9.81 m/s^2$).
- **Sincronización Total**: El servicio emite mediante `BroadcastReceiver` (acción `SPEED_UPDATE`) no solo la velocidad, sino también el tiempo transcurrido (`elapsedTimeMs`) y la distancia acumulada.
- **Notificaciones**: Implementa canales de notificación para cumplir con los requisitos de Foreground Services en Android 13+.

### 2. Interfaz de Usuario y Mapas
- **MapLibre (Crash Fix)**: Se corrigió el error `vk::createInstanceUnique` mediante el uso de `textureMode(true)` en `MapLibreMapOptions`.
- **Exportación/Importación QR**: Optimización mediante compresión **GZIP** y fotos Base64 de baja resolución (8x8 px).
- **Análisis de Datos IA**: Se implementó una función de exportación completa en formato **JSON** (`ExportUtils.kt`) que consolida el perfil, garaje y todas las sesiones de telemetría de alta frecuencia para su análisis externo.

### 3. Android Auto (`RaceTrackerCarScreen.kt`)
- **Diseño "Cockpit Spotify"**: Rediseño visual con imagen lateral del vehículo, foto de perfil en el Action Strip y datos de telemetría en formato XL (Títulos de fila).
- **Reglas de Distracción**: El panel está limitado a **exactamente 2 filas** cuando incluye botones de acción para evitar cierres forzados.
- **Categoría POI**: Clasificada oficialmente como `POI`. Se añadió un botón de "MAPA" para cumplir con la funcionalidad esperada por Google en esta categoría.
- **Suavizado de Lenguaje**: Se renombró "DUELOS" a **"TEST DE RENDIMIENTO"** para cumplir con las políticas de seguridad vial.

### 4. Revisión de Google Play (Tester User)
- **Credenciales**: Usuario `user` / Contraseña `12345678`.
- **Auto-provisión Universal**: El usuario y vehículo de pruebas se crean directamente en el `onCreate` de la base de datos (`AppDatabase.kt`), asegurando que existan aunque el revisor abra primero Android Auto.
- **Auto-Login Forzado**: La app en el coche detecta si no hay sesión y auto-conecta al usuario de pruebas para evitar pantallas vacías.

---

## 📝 Historial de Sesiones y Ajustes Recientes

### Sesión: Cumplimiento de Políticas y Rediseño "Cockpit Pro"
- **Problema**: Rechazo de Google por credenciales no funcionales y falta de funciones de búsqueda en categoría POI.
- **Solución Realizada**: 
    - Se movió la creación del tester a la capa de persistencia (DB).
    - Se implementó la carga de **Bitmaps** (fotos de perfil/coche) escalados para Android Auto.
    - Se suavizó el lenguaje de la UI para evitar términos de "carreras".
    - Sincronización milimétrica del cronómetro entre móvil y coche.

### Sesión: Estabilización Final de Android Auto
- **Problema**: Cierres repetidos reportados por Google Play.
- **Solución Realizada**: 
    - Se restauró la conexión entre el servicio y `RaceTrackerCarScreen`.
    - Se limitó el `Pane` a **exactamente 2 filas**.
    - Se aseguró que toda actualización de UI se ejecute en `Dispatchers.Main`.

---

## 💡 Notas Técnicas para el Futuro
- **Filtro de GPS**: El cálculo de Fuerzas G es sensible al ruido. Considerar filtro de media móvil.
- **QR Complexity**: Explorar formatos binarios más eficientes si se requiere subir la resolución de la foto.

## Debug android auto
- cd %LOCALAPPDATA%\Android\Sdk\platform-tools
- -  .\adb forward --remove-all
- -  .\adb forward tcp:5277 tcp:5277
- cd %LOCALAPPDATA%\Android\Sdk\extras\google\auto
- - .\desktop-head-unit.exe
