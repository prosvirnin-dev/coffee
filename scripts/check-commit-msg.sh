#!/bin/sh
# Заголовок коммита — Conventional Commits без области: «тип: что сделано», без точки в конце, до 72 знаков
# (длиннее GitHub обрезает заголовок в списке коммитов).
#
# Хук commit-msg: его зовет pre-commit, путь к файлу сообщения приходит первым аргументом. Слияния, откаты и правки
# для autosquash называет сам git — их заголовки не проверяются.

title=$(grep -v '^#' "$1" | grep -m 1 '[^[:space:]]')

fail() {
    printf '%s\n  %s\n' "$1" "$title"
    exit 1
}

case $title in
    'Merge '* | 'Revert "'* | 'fixup! '* | 'squash! '*) exit 0 ;;
esac

printf '%s\n' "$title" | grep -Eq '^(feat|fix|refactor|perf|docs|test|build|ci|chore)!?: [^[:space:]]' ||
    fail 'Нужен вид «тип: что сделано». Типы: feat fix refactor perf docs test build ci chore.'

case $title in
    *.) fail 'Точка в конце заголовка не нужна.' ;;
esac

# Знаки, а не байты: кириллица в UTF-8 занимает по два байта.
length=$(printf '%s' "$title" | LC_ALL=C.UTF-8 wc -m | tr -d ' ')
[ "$length" -le 72 ] || fail "Заголовок длиннее 72 знаков: $length."
