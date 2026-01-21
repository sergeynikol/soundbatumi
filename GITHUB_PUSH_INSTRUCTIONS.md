# Инструкция: Как запушить проект на GitHub

## Текущее состояние
- **Ветка**: `refactoring-changes` (создана и содержит коммит)
- **Удаленный репозиторий**: `https://github.com/sergeynikol/soundbatumi.git`
- **Статус**: Ветка создана локально, нужна аутентификация для push

---

## Вариант 1: Push через HTTPS с Personal Access Token (Рекомендуется)

### Шаг 1: Создайте Personal Access Token на GitHub

1. Откройте GitHub в браузере: https://github.com
2. Перейдите в **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Нажмите **Generate new token** → **Generate new token (classic)**
4. Задайте имя токена (например: "Sound Batumi Project")
5. Выберите срок действия (например: 90 дней или No expiration)
6. Отметьте права доступа:
   - ✅ `repo` (полный доступ к репозиториям)
7. Нажмите **Generate token**
8. **ВАЖНО**: Скопируйте токен сразу! Он больше не будет показан.

### Шаг 2: Выполните push

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi

# Убедитесь, что используете HTTPS URL
git remote set-url origin https://github.com/sergeynikol/soundbatumi.git

# Выполните push
git push -u origin refactoring-changes
```

**При запросе:**
- **Username**: `sergeynikol`
- **Password**: Вставьте ваш Personal Access Token (НЕ пароль от GitHub!)

---

## Вариант 2: Push через SSH (если настроен SSH ключ)

### Шаг 1: Проверьте наличие SSH ключа

```bash
ls -la ~/.ssh/id_rsa.pub
```

Если файл существует, переходите к Шагу 3. Если нет - создайте ключ.

### Шаг 2: Создайте SSH ключ (если его нет)

```bash
# Создайте SSH ключ
ssh-keygen -t ed25519 -C "your_email@example.com"

# Или используйте RSA
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Нажмите Enter для всех вопросов (или задайте пароль)
```

### Шаг 3: Добавьте SSH ключ на GitHub

```bash
# Скопируйте публичный ключ
cat ~/.ssh/id_rsa.pub
# Или для ed25519:
cat ~/.ssh/id_ed25519.pub
```

1. Скопируйте весь вывод команды (начинается с `ssh-rsa` или `ssh-ed25519`)
2. Откройте GitHub → **Settings** → **SSH and GPG keys**
3. Нажмите **New SSH key**
4. Вставьте ключ и сохраните

### Шаг 4: Настройте remote и выполните push

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi

# Измените URL на SSH
git remote set-url origin git@github.com:sergeynikol/soundbatumi.git

# Проверьте подключение
ssh -T git@github.com

# Выполните push
git push -u origin refactoring-changes
```

---

## Вариант 3: Использование GitHub CLI (gh)

### Шаг 1: Установите GitHub CLI (если не установлен)

```bash
# Для Ubuntu/Debian
sudo apt update
sudo apt install gh

# Для других систем: https://cli.github.com/
```

### Шаг 2: Авторизуйтесь

```bash
gh auth login
```

Следуйте инструкциям:
- Выберите `GitHub.com`
- Выберите `HTTPS` или `SSH`
- Выберите способ аутентификации (браузер или токен)

### Шаг 3: Выполните push

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi
git push -u origin refactoring-changes
```

---

## Вариант 4: Использование Git Credential Manager

### Шаг 1: Настройте credential helper

```bash
# Для Linux
git config --global credential.helper store

# Или для кеширования на 1 час
git config --global credential.helper 'cache --timeout=3600'
```

### Шаг 2: Выполните push

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi
git push -u origin refactoring-changes
```

При первом запросе введите:
- Username: `sergeynikol`
- Password: Personal Access Token

---

## Проверка результата

После успешного push:

1. Откройте в браузере: https://github.com/sergeynikol/soundbatumi
2. Вы должны увидеть ветку `refactoring-changes`
3. GitHub предложит создать Pull Request

---

## Создание Pull Request

После push вы можете создать Pull Request:

1. Откройте: https://github.com/sergeynikol/soundbatumi
2. Нажмите на кнопку **Compare & pull request** (если появится)
3. Или перейдите в **Pull requests** → **New pull request**
4. Выберите:
   - **base**: `main`
   - **compare**: `refactoring-changes`
5. Заполните описание и создайте PR

---

## Полезные команды для проверки

```bash
# Проверить текущую ветку
git branch

# Проверить статус
git status

# Проверить удаленные репозитории
git remote -v

# Посмотреть последние коммиты
git log --oneline -5

# Проверить, что ветка запушена
git branch -r
```

---

## Решение проблем

### Ошибка: "Authentication failed"
- Проверьте правильность токена/пароля
- Убедитесь, что токен имеет права `repo`

### Ошибка: "Permission denied (publickey)"
- Проверьте, что SSH ключ добавлен на GitHub
- Проверьте подключение: `ssh -T git@github.com`

### Ошибка: "Repository not found"
- Проверьте, что репозиторий существует
- Проверьте права доступа к репозиторию

---

## Текущий коммит в ветке

```
ae4c2bb Refactoring: исправление моделей, шаблонов и улучшение кода
```

Включает изменения в:
- Моделях (исправление опечаток)
- Шаблонах
- Настройках
- Зависимостях
