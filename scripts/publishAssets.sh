#!/usr/bin/env bash

# Publish selected assets from this repository to the public website repository.
# The deliberately small YAML reader supports the list of source/target mappings
# documented in publish-assets.yml. Replace manifestRead() if richer YAML is needed.

set -Eeuo pipefail

readonly EXIT_USAGE=2
readonly EXIT_DEPENDENCY=3
readonly EXIT_REPOSITORY=4
readonly EXIT_DIRTY=5
readonly EXIT_MANIFEST=6
readonly EXIT_PUBLISH=7
readonly EXIT_GIT=8

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SOURCE_REPO="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
readonly DEFAULT_DESTINATION="${HOME}/Source/clanneolasWebsite"
readonly DEFAULT_MANIFEST="${SOURCE_REPO}/publishAssets.yml"

dryRun=1
VERBOSE=false
FORCE=false
COMMIT=false
PUSH=false
DESTINATION_REPO="${CLANN_EOLAS_WEBSITE_REPO:-${DEFAULT_DESTINATION}}"
MANIFEST="${DEFAULT_MANIFEST}"

declare -a PUBLISH_SOURCES=()
declare -a PUBLISH_TARGETS=()
declare -a RSYNC_OUTPUT=()
FILES_COPIED=0
FILES_UPDATED=0
FILES_REMOVED=0

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
    readonly GREEN=$'\033[32m'
    readonly YELLOW=$'\033[33m'
    readonly BOLD=$'\033[1m'
    readonly RESET=$'\033[0m'
else
    readonly GREEN=''
    readonly YELLOW=''
    readonly BOLD=''
    readonly RESET=''
fi

## workflow

main() {
    loggingInitialize
    argumentsParse "$@"
    dependenciesValidate
    manifestRead "${MANIFEST}"
    repositoriesValidate
    pathsValidate

    outputDisplayHeader
    repositoryDisplay "Source Repository" "${SOURCE_REPO}"
    repositoryDisplay "Destination Repository" "${DESTINATION_REPO}"
    repositoriesRequireClean
    publishMappings
    summaryDisplay
    gitIntegrate
    log_done 'asset publication complete'
}

## arguments

argumentsParse() {
    while (($# > 0)); do
        case "$1" in
            -y|--confirm) dryRun='' ;;
            --verbose) VERBOSE=true ;;
            --force) FORCE=true ;;
            --commit) COMMIT=true ;;
            --push)
                PUSH=true
                COMMIT=true
                ;;
            --destination)
                (($# >= 2)) || usageError '--destination requires a path'
                DESTINATION_REPO=$2
                shift
                ;;
            --manifest)
                (($# >= 2)) || usageError '--manifest requires a path'
                MANIFEST=$2
                shift
                ;;
            -h|--help)
                usageDisplay
                exit 0
                ;;
            *) usageError "unknown option: $1" ;;
        esac
        shift
    done

    if [[ -n "${dryRun}" && ("${COMMIT}" == true || "${PUSH}" == true) ]]; then
        usageError '--commit and --push require --confirm'
    fi
}

usageDisplay() {
    cat <<'EOF'
Usage: scripts/publish-assets.sh [OPTIONS]

Publish the mappings in publish-assets.yml to the website repository.

Options:
  -y, --confirm         publish changes (default: safe preview)
  --verbose             show individual rsync changes and Git commands
  --force               allow dirty source and destination worktrees
  --commit              commit published paths in the destination repository
  --push                commit, then push the destination branch
  --destination PATH    website repository (default: ~/Source/clanneolasWebsite)
  --manifest PATH       manifest file (default: publish-assets.yml)
  -h, --help            show this help

The CLANN_EOLAS_WEBSITE_REPO environment variable can also set the destination.
EOF
}

usageError() {
    outputError "$1"
    usageDisplay >&2
    exit "${EXIT_USAGE}"
}

## dependencies

dependenciesValidate() {
    local command_name

    for command_name in git rsync; do
        command -v "${command_name}" >/dev/null 2>&1 || {
            outputError "required command not found: ${command_name}"
            exit "${EXIT_DEPENDENCY}"
        }
    done
}

## logging

loggingInitialize() {
    local log_utils_path

    command -v python3 >/dev/null 2>&1 || {
        printf 'Error: required command not found: python3\n' >&2
        exit "${EXIT_DEPENDENCY}"
    }
    if ! log_utils_path="$(
        python3 -c 'import importlib.util; spec = importlib.util.find_spec("organiseMyProjects"); print(next(iter(spec.submodule_search_locations)) + "/logUtils.sh" if spec and spec.submodule_search_locations else "")'
    )"; then
        printf 'Error: unable to locate organiseMyProjects/logUtils.sh.\n' >&2
        exit "${EXIT_DEPENDENCY}"
    fi
    [[ -f "${log_utils_path}" ]] || {
        printf 'Error: organiseMyProjects/logUtils.sh was not found.\n' >&2
        exit "${EXIT_DEPENDENCY}"
    }

    # shellcheck source=/dev/null
    source "${log_utils_path}"
    setApplication 'publishAssets' "${PUBLISH_ASSETS_LOG_DIR:-}"
}

## manifest

manifestRead() {
    local manifest_path=$1
    local line
    local source_path=''
    local target_path=''

    [[ -f "${manifest_path}" ]] || {
        outputError "manifest does not exist: ${manifest_path}"
        exit "${EXIT_MANIFEST}"
    }

    while IFS= read -r line || [[ -n "${line}" ]]; do
        line=${line%%#*}
        if [[ "${line}" =~ ^[[:space:]]*-[[:space:]]source:[[:space:]]*(.+)[[:space:]]*$ ]]; then
            [[ -z "${source_path}" ]] || manifestFail 'source is missing its target'
            source_path=$(_yamlValueClean "${BASH_REMATCH[1]}")
        elif [[ "${line}" =~ ^[[:space:]]*target:[[:space:]]*(.+)[[:space:]]*$ ]]; then
            [[ -n "${source_path}" ]] || manifestFail 'target appears before source'
            target_path=$(_yamlValueClean "${BASH_REMATCH[1]}")
            PUBLISH_SOURCES+=("${source_path}")
            PUBLISH_TARGETS+=("${target_path}")
            source_path=''
            target_path=''
        elif [[ -n "${line//[[:space:]]/}" && ! "${line}" =~ ^[[:space:]]*publish:[[:space:]]*$ ]]; then
            manifestFail "unsupported YAML: ${line}"
        fi
    done < "${manifest_path}"

    [[ -z "${source_path}" ]] || manifestFail 'final source is missing its target'
    ((${#PUBLISH_SOURCES[@]} > 0)) || manifestFail 'no publish mappings found'
}

manifestFail() {
    outputError "invalid manifest: $1"
    exit "${EXIT_MANIFEST}"
}

_yamlValueClean() {
    local value=$1
    value=${value#\"}
    value=${value%\"}
    value=${value#\'}
    value=${value%\'}
    printf '%s\n' "${value%${value##*[![:space:]]}}"
}

## repositories

repositoriesRequireClean() {
    local source_status
    local destination_status

    source_status=$(git -C "${SOURCE_REPO}" status --porcelain)
    destination_status=$(git -C "${DESTINATION_REPO}" status --porcelain)
    if [[ -n "${source_status}" || -n "${destination_status}" ]]; then
        if [[ "${FORCE}" != true ]]; then
            outputError 'a repository has uncommitted changes; use --force to override'
            exit "${EXIT_DIRTY}"
        fi
        outputWarning 'continuing with uncommitted changes because --force was supplied'
    fi
}

repositoriesValidate() {
    repositoryValidate "${SOURCE_REPO}" 'source'
    repositoryValidate "${DESTINATION_REPO}" 'destination'
}

repositoryDisplay() {
    local heading=$1
    local path=$2
    local status

    status=$(git -C "${path}" status --porcelain)
    printf '\n%s%s%s\n\n' "${BOLD}" "${heading}" "${RESET}"
    printf 'Repo:   %s\n' "$(basename -- "$(git -C "${path}" rev-parse --show-toplevel)")"
    printf 'Branch: %s\n' "$(git -C "${path}" branch --show-current)"
    printf 'Commit: %s\n' "$(git -C "${path}" rev-parse --short HEAD)"
    if [[ -z "${status}" ]]; then
        printf 'Status: %sclean%s\n' "${GREEN}" "${RESET}"
    else
        printf 'Status: %sdirty%s\n' "${YELLOW}" "${RESET}"
        [[ "${VERBOSE}" == true ]] && printf '%s\n' "${status}"
    fi
    return 0
}

repositoryValidate() {
    local path=$1
    local role=$2

    [[ -d "${path}" ]] || {
        outputError "${role} directory does not exist: ${path}"
        exit "${EXIT_REPOSITORY}"
    }
    git -C "${path}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
        outputError "${role} directory is not a Git repository: ${path}"
        exit "${EXIT_REPOSITORY}"
    }
}

## paths

pathsValidate() {
    local index
    local source_path
    local target_path

    for index in "${!PUBLISH_SOURCES[@]}"; do
        source_path=${PUBLISH_SOURCES[index]}
        target_path=${PUBLISH_TARGETS[index]}
        _relativePathValidate "${source_path}" 'source'
        _relativePathValidate "${target_path}" 'target'
        [[ -d "${SOURCE_REPO}/${source_path}" ]] || {
            outputError "configured source folder does not exist: ${source_path}"
            exit "${EXIT_MANIFEST}"
        }
        _targetUniqueValidate "${index}" "${target_path}"
    done
}

_relativePathValidate() {
    local path=$1
    local label=$2

    [[ -n "${path}" && "${path}" != /* && "${path}" != '.' && "${path}" != '..' \
        && "${path}" != ../* && "${path}" != */../* && "${path}" != */.. ]] || {
        outputError "${label} must be a safe relative path: ${path}"
        exit "${EXIT_MANIFEST}"
    }
}

_targetUniqueValidate() {
    local current_index=$1
    local current_target=$2
    local prior_index
    local prior_target

    for ((prior_index = 0; prior_index < current_index; prior_index++)); do
        prior_target=${PUBLISH_TARGETS[prior_index]}
        if [[ "${current_target}" == "${prior_target}" || "${current_target}" == "${prior_target}/"* \
            || "${prior_target}" == "${current_target}/"* ]]; then
            outputError "target folders overlap: ${prior_target} and ${current_target}"
            exit "${EXIT_MANIFEST}"
        fi
    done
}

## publishing

publishMappings() {
    local index

    printf '\n%sPublishing%s\n\n' "${BOLD}" "${RESET}"
    for index in "${!PUBLISH_SOURCES[@]}"; do
        publishMapping "${PUBLISH_SOURCES[index]}" "${PUBLISH_TARGETS[index]}"
    done
}

publishMapping() {
    local source_path=$1
    local target_path=$2
    local target_directory="${DESTINATION_REPO}/${target_path}"
    local -a arguments=(-a --delete --itemize-changes --out-format='%i|%n%L')
    local output

    [[ -n "${dryRun}" ]] && arguments+=(--dry-run)
    [[ "${VERBOSE}" == true ]] && arguments+=(-v)
    _rsyncExclusionsAdd "${source_path}" arguments

    log_action "publishing ${source_path} to ${target_path}"
    if [[ -z "${dryRun}" ]]; then
        mkdir -p -- "${target_directory}"
    fi
    if ! output=$(rsync "${arguments[@]}" -- "${SOURCE_REPO}/${source_path}/" "${target_directory}/"); then
        outputError "failed to publish ${source_path}"
        exit "${EXIT_PUBLISH}"
    fi
    mapfile -t RSYNC_OUTPUT <<< "${output}"
    statisticsAdd RSYNC_OUTPUT
    if [[ "${VERBOSE}" == true && -n "${output}" ]]; then
        printf '%s\n' "${output}"
    fi
    log_done "$(basename -- "${target_path}") published"
}

_rsyncExclusionsAdd() {
    local source_path=$1
    local -n arguments_reference=$2
    local excluded
    local -a excluded_paths=(.git .github .vscode documentation deploy scripts README.md LICENSE)

    for excluded in "${excluded_paths[@]}"; do
        if [[ "${source_path}" != "${excluded}" && "${source_path}" != "${excluded}/"* ]]; then
            arguments_reference+=(--exclude="${excluded}")
        fi
    done
}

statisticsAdd() {
    local -n lines_reference=$1
    local line
    local item
    local name

    for line in "${lines_reference[@]}"; do
        [[ "${line}" == *'|'* ]] || continue
        item=${line%%|*}
        name=${line#*|}
        if [[ "${item}" == '*deleting'* ]]; then
            [[ "${name}" == */ ]] || ((FILES_REMOVED += 1))
        elif [[ "${item:1:1}" == 'f' ]]; then
            if [[ "${item}" == *'+++++++++'* ]]; then
                ((FILES_COPIED += 1))
            else
                ((FILES_UPDATED += 1))
            fi
        fi
    done
}

## git

gitIntegrate() {
    local source_commit
    local -a target_paths=()
    local target_path

    [[ "${COMMIT}" == true ]] || return 0
    source_commit=$(git -C "${SOURCE_REPO}" rev-parse --short HEAD)
    for target_path in "${PUBLISH_TARGETS[@]}"; do
        target_paths+=("${target_path}")
    done

    [[ "${VERBOSE}" == true ]] && printf '\nStaging configured target folders.\n'
    log_action 'staging configured target folders'
    git -C "${DESTINATION_REPO}" add -A -- "${target_paths[@]}" || exit "${EXIT_GIT}"
    if git -C "${DESTINATION_REPO}" diff --cached --quiet -- "${target_paths[@]}"; then
        outputWarning 'no published changes to commit'
        return 0
    fi
    log_action 'committing published asset folders'
    git -C "${DESTINATION_REPO}" commit \
        -m "Publish assets from clanneolas @ ${source_commit}" -- "${target_paths[@]}" \
        || exit "${EXIT_GIT}"
    if [[ "${PUSH}" == true ]]; then
        log_action 'pushing destination repository'
        git -C "${DESTINATION_REPO}" push || exit "${EXIT_GIT}"
    fi
}

## output

outputDisplayHeader() {
    printf '%s%s-------------------------------------------------------\n' "${BOLD}" "${GREEN}"
    printf 'Publishing Clann Eolas Assets\n'
    printf '%s-------------------------------------------------------%s\n' "${GREEN}" "${RESET}"
    log_doing 'publishing Clann Eolas assets'
    [[ -n "${dryRun}" ]] && outputWarning 'preview: no files will be changed; use --confirm to publish'
    return 0
}

outputError() {
    log_error "$1"
}

outputWarning() {
    log_warn "$1"
}

summaryDisplay() {
    printf '\n%sSummary%s\n\n' "${BOLD}" "${RESET}"
    printf 'Files copied:  %d\n' "${FILES_COPIED}"
    printf 'Files updated: %d\n' "${FILES_UPDATED}"
    printf 'Files removed: %d\n' "${FILES_REMOVED}"
    [[ -n "${dryRun}" ]] && printf '(projected changes; preview)\n'
    return 0
}

trap 'outputError "unexpected failure on line ${LINENO}"' ERR

main "$@"
