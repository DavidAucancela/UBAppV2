# Documentación: Incidente de Secretos en Git

**Fecha:** Febrero 2026  
**Problema:** GitHub bloqueó el push porque el archivo `.env` contenía secretos (API Key de OpenAI).  
**Objetivo:** Explicar qué pasó y qué se hizo para solucionarlo.

---

## Índice

1. [¿Qué es un secreto y por qué importa?](#1-qué-es-un-secreto-y-por-qué-importa)
2. [¿Qué pasó exactamente?](#2-qué-pasó-exactamente)
3. [Conceptos de Git que necesitas entender](#3-conceptos-de-git-que-necesitas-entender)
4. [Pasos que se ejecutaron (resumen)](#4-pasos-que-se-ejecutaron-resumen)
5. [Explicación detallada de cada paso](#5-explicación-detallada-de-cada-paso)
6. [Buenas prácticas para el futuro](#6-buenas-prácticas-para-el-futuro)

---

## 1. ¿Qué es un secreto y por qué importa?

Un **secreto** es cualquier dato que no debe ser público:

- Contraseñas
- API Keys (como la de OpenAI)
- Tokens de acceso
- Claves de bases de datos

**Problema:** Si subes un secreto a GitHub (o cualquier repositorio público), cualquiera puede verlo. Alguien podría usar tu API Key, gastar tu crédito, o acceder a tus datos.

**Solución de GitHub:** GitHub escanea cada push y bloquea si detecta patrones de secretos conocidos (API keys, contraseñas, etc.). Eso es lo que te pasó.

---

## 2. ¿Qué pasó exactamente?

1. El archivo `.env` (que contiene tu API Key de OpenAI) fue **commiteado** en el pasado.
2. Ese commit quedó en el **historial** de Git.
3. Al hacer `git push`, GitHub revisó todos los commits que ibas a subir.
4. Detectó la API Key en el commit `500f20154bf61a6799cc1b321ccc9540effaa562` y **bloqueó el push**.

**Importante:** Aunque luego agregues `.env` al `.gitignore`, el archivo **sigue en el historial**. Git guarda una copia de cada versión de cada archivo en cada commit. Por eso no basta con “dejar de trackear” el archivo: hay que **reescribir el historial** para borrarlo de todos los commits.

---

## 3. Conceptos de Git que necesitas entender

### Working directory (directorio de trabajo)

- Es la carpeta donde trabajas.
- Aquí están los archivos que editas.

### Staging area (índice)

- Zona intermedia entre tu carpeta y el repositorio.
- `git add` mueve archivos aquí.
- `git commit` guarda lo que está en el índice en un nuevo commit.

### Commit

- Un “foto” del estado del proyecto en un momento dado.
- Tiene un hash único (ej: `500f20154bf61a6799cc1b321ccc9540effaa562`).
- Los commits forman una cadena: cada uno apunta al anterior.

### Historial

- Secuencia de commits desde el primero hasta el actual.
- Git guarda el contenido de cada archivo en cada commit.
- Si un archivo fue commiteado alguna vez, queda en el historial aunque luego lo borres.

### .gitignore

- Archivo que indica a Git qué archivos **no** debe trackear.
- Solo afecta a archivos que **nunca** fueron commiteados.
- Si un archivo ya está en el historial, agregarlo a `.gitignore` no lo borra del pasado.

### Stash

- Guarda temporalmente cambios sin hacer commit.
- Útil para “apartar” cambios, hacer otra cosa, y luego recuperarlos.

---

## 4. Pasos que se ejecutaron (resumen)

| Paso | Comando | ¿Qué hace? |
|------|---------|-------------|
| 1 | Crear `.gitignore` en la raíz | Evita que `.env` se vuelva a subir en el futuro |
| 2 | `git reset HEAD .env` | Quita `.env` del área de staging |
| 3 | `git stash push -u -m "guardar .env temporalmente"` | Guarda tus cambios locales (incluido `.env`) temporalmente |
| 4 | `git filter-branch ...` | Reescribe el historial eliminando `.env` de todos los commits |
| 5 | `git stash pop` | Recupera tu `.env` local |
| 6 | Resolver conflicto | Mantener tu `.env` en disco sin trackearlo |
| 7 | `git push origin main --force-with-lease` | Sube el historial reescrito al remoto |

---

## 5. Explicación detallada de cada paso

### Paso 1: Crear `.gitignore` en la raíz

**Problema:** Solo existía `.gitignore` en `backend/`, no en la raíz. El `.env` de la raíz no estaba ignorado.

**Solución:** Se creó un `.gitignore` en la raíz con:

```
.env
.env.local
.env.*.local
```

Así Git ignora `.env` y variantes en futuros `git add`.

---

### Paso 2: `git reset HEAD .env`

**Qué hace:** Quita `.env` del área de staging (índice). El archivo sigue en tu disco, pero deja de estar “preparado” para el próximo commit.

**Por qué:** Para poder ejecutar `filter-branch` necesitamos un directorio de trabajo “limpio” (sin cambios sin commitear).

---

### Paso 3: `git stash push -u -m "guardar .env temporalmente"`

**Qué hace:** Guarda temporalmente todos los cambios (incluido `.env`) en un “stash”. Tu working directory queda limpio.

**Parámetros:**
- `-u`: incluye archivos no trackeados
- `-m "mensaje"`: descripción del stash

**Por qué:** `filter-branch` no puede ejecutarse si hay cambios sin commitear. El stash nos permite guardar esos cambios, limpiar el directorio, y luego recuperarlos.

---

### Paso 4: `git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty HEAD`

**Qué hace:** Recorre todos los commits de la rama `main` y los reescribe. En cada commit ejecuta `git rm --cached .env`, es decir, elimina `.env` del índice de ese commit.

**Parámetros:**
- `--force`: permite sobrescribir el backup anterior de `filter-branch`
- `--index-filter "comando"`: comando que se ejecuta en cada commit
- `git rm --cached --ignore-unmatch .env`: elimina `.env` del índice; `--ignore-unmatch` evita error si el archivo no existe en ese commit
- `--prune-empty`: elimina commits que queden vacíos
- `HEAD`: rama a procesar

**Resultado:** El historial se reescribe. Los commits tienen nuevos hashes. El archivo `.env` ya no aparece en ningún commit.

---

### Paso 5: `git stash pop`

**Qué hace:** Recupera los cambios guardados en el stash y los aplica de nuevo al working directory.

**Conflicto:** Al hacer `pop`, Git detectó que `.env` fue “eliminado” en el historial (por `filter-branch`) pero “modificado” en el stash. Eso genera un conflicto.

**Resolución:** Queremos mantener tu `.env` en disco y que Git no lo trackee. Por eso se usó `git checkout stash -- .env` para recuperar el archivo del stash y `git reset HEAD .env` para que no esté en el índice.

---

### Paso 6: Resolver el conflicto y mantener `.env` local

**Comandos usados:**

```bash
git restore --staged .env
git checkout stash -- .env
git reset HEAD .env
git stash drop
```

**Resultado:** Tu `.env` vuelve a estar en tu disco, pero Git ya no lo trackea. El `.gitignore` evita que se vuelva a agregar.

---

### Paso 7: `git push origin main --force-with-lease`

**Por qué `--force`:** Al reescribir el historial con `filter-branch`, los commits nuevos tienen hashes distintos. El historial local ya no coincide con el remoto. Un `git push` normal sería rechazado.

**Por qué `--force-with-lease`:** Es más seguro que `--force` porque comprueba que nadie haya subido más commits al remoto antes de sobrescribir. Si alguien pusheó antes que tú, el push falla.

---

## 6. Buenas prácticas para el futuro

### 1. Nunca subir `.env`

- Siempre incluye `.env` en `.gitignore`
- Usa `.env.example` como plantilla con valores de ejemplo (sin secretos)

### 2. Si subes un secreto por error

1. **Rotar el secreto:** genera una nueva API Key en el proveedor y revoca la antigua.
2. **Quitar el secreto del historial:** con `filter-branch` o `git filter-repo`.
3. **Subir el historial limpio:** con `git push --force-with-lease`.

### 3. Verificar antes de commitear

```bash
git status
```

Revisa qué archivos vas a commitear. Si ves `.env`, no lo hagas.

### 4. Comandos útiles

| Comando | Uso |
|---------|-----|
| `git status` | Ver qué archivos están modificados o en staging |
| `git diff` | Ver cambios concretos |
| `git log --oneline` | Ver historial de commits |
| `git stash` | Guardar cambios temporalmente |
| `git stash pop` | Recuperar cambios guardados |

---

## Resumen final

- **Problema:** `.env` con secretos estaba en el historial de Git.
- **Solución:** Reescribir el historial con `filter-branch` para eliminar `.env` de todos los commits.
- **Prevención:** `.gitignore` en la raíz y nunca commitear `.env`.
- **Acción recomendada:** Rotar la API Key de OpenAI porque pudo haber sido expuesta.

---

*Documento generado para documentar el incidente y servir como referencia futura.*
