#!/usr/bin/env bash

# Publish selected assets from this repository to the public website repository.
# The deliberately small YAML reader supports the list of source/target mappings
# documented in scripts/publishAssets.yml. Replace manifestRead() if richer YAML is needed.

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
readonly DEFAULT_MANIFEST="${SCRIPT_DIR}/publishAssets.yml"

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
pullRequestUrl=''

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
    gitIntegrate
    summaryDisplay
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
Usage: scripts/publishAssets.sh [OPTIONS]

Publish the mappings in scripts/publishAssets.yml to the website repository.

Options:
  -y, --confirm         publish changes (default: safe preview)
  --verbose             show individual rsync changes and Git commands
  --force               allow dirty source and destination worktrees
  --commit              commit published paths on the current local branch
  --push                create a branch, commit, push, and open a pull request
  --destination PATH    website repository (default: ~/Source/clanneolasWebsite)
  --manifest PATH       manifest file (default: scripts/publishAssets.yml)
  -h, --help            show this help

--push implies --commit and only creates a branch and pull request when files
change. Without --commit or --push, --confirm leaves changes local and
uncommitted in the destination repository.

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
    local commandName

    for commandName in git rsync; do
        command -v "${commandName}" >/dev/null 2>&1 || {
            outputError "required command not found: ${commandName}"
            exit "${EXIT_DEPENDENCY}"
        }
    done

    if [[ "${PUSH}" == true ]] && ! command -v gh >/dev/null 2>&1; then
        outputError 'required command not found: gh'
        exit "${EXIT_DEPENDENCY}"
    fi
}

## logging

loggingInitialize() {
    local logUtilsPath

    command -v python3 >/dev/null 2>&1 || {
        printf 'Error: required command not found: python3\n' >&2
        exit "${EXIT_DEPENDENCY}"
    }
    if ! logUtilsPath="$(
        python3 -c 'import importlib.util; spec = importlib.util.find_spec("organiseMyProjects"); print(next(iter(spec.submodule_search_locations)) + "/logUtils.sh" if spec and spec.submodule_search_locations else "")'
    )"; then
        printf 'Error: unable to locate organiseMyProjects/logUtils.sh.\n' >&2
        exit "${EXIT_DEPENDENCY}"
    fi
    [[ -f "${logUtilsPath}" ]] || {
        printf 'Error: organiseMyProjects/logUtils.sh was not found.\n' >&2
        exit "${EXIT_DEPENDENCY}"
    }

    # shellcheck source=/dev/null
    source "${logUtilsPath}"
    setApplication 'publishAssets' "${PUBLISH_ASSETS_LOG_DIR:-}"
}

## manifest

manifestRead() {
    local manifestPath=$1
    local line
    local sourcePath=''
    local targetPath=''

    [[ -f "${manifestPath}" ]] || {
        outputError "manifest does not exist: ${manifestPath}"
        exit "${EXIT_MANIFEST}"
    }

    while IFS= read -r line || [[ -n "${line}" ]]; do
        line=${line%%#*}
        if [[ "${line}" =~ ^[[:space:]]*-[[:space:]]source:[[:space:]]*(.+)[[:space:]]*$ ]]; then
            [[ -z "${sourcePath}" ]] || manifestFail 'source is missing its target'
            sourcePath=$(_yamlValueClean "${BASH_REMATCH[1]}")
        elif [[ "${line}" =~ ^[[:space:]]*target:[[:space:]]*(.+)[[:space:]]*$ ]]; then
            [[ -n "${sourcePath}" ]] || manifestFail 'target appears before source'
            targetPath=$(_yamlValueClean "${BASH_REMATCH[1]}")
            PUBLISH_SOURCES+=("${sourcePath}")
            PUBLISH_TARGETS+=("${targetPath}")
            sourcePath=''
            targetPath=''
        elif [[ -n "${line//[[:space:]]/}" && ! "${line}" =~ ^[[:space:]]*publish:[[:space:]]*$ ]]; then
            manifestFail "unsupported YAML: ${line}"
        fi
    done < "${manifestPath}"

    [[ -z "${sourcePath}" ]] || manifestFail 'final source is missing its target'
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
    local sourceStatus
    local destinationStatus

    sourceStatus=$(git -C "${SOURCE_REPO}" status --porcelain)
    destinationStatus=$(git -C "${DESTINATION_REPO}" status --porcelain)
    if [[ -n "${sourceStatus}" || -n "${destinationStatus}" ]]; then
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
    local sourcePath
    local targetPath

    for index in "${!PUBLISH_SOURCES[@]}"; do
        sourcePath=${PUBLISH_SOURCES[index]}
        targetPath=${PUBLISH_TARGETS[index]}
        _relativePathValidate "${sourcePath}" 'source'
        _relativePathValidate "${targetPath}" 'target'
        [[ -d "${SOURCE_REPO}/${sourcePath}" ]] || {
            outputError "configured source folder does not exist: ${sourcePath}"
            exit "${EXIT_MANIFEST}"
        }
        _targetUniqueValidate "${index}" "${targetPath}"
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
    local currentIndex=$1
    local currentTarget=$2
    local priorIndex
    local priorTarget

    for ((priorIndex = 0; priorIndex < currentIndex; priorIndex++)); do
        priorTarget=${PUBLISH_TARGETS[priorIndex]}
        if [[ "${currentTarget}" == "${priorTarget}" || "${currentTarget}" == "${priorTarget}/"* \
            || "${priorTarget}" == "${currentTarget}/"* ]]; then
            outputError "target folders overlap: ${priorTarget} and ${currentTarget}"
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
    local sourcePath=$1
    local targetPath=$2
    local targetDirectory="${DESTINATION_REPO}/${targetPath}"
    local -a arguments=(-a --delete --itemize-changes --out-format='%i|%n%L')
    local output

    [[ -n "${dryRun}" ]] && arguments+=(--dry-run)
    [[ "${VERBOSE}" == true ]] && arguments+=(-v)
    _rsyncExclusionsAdd "${sourcePath}" arguments

    log_doing "publishing ${sourcePath} to ${targetPath}"
    if [[ -z "${dryRun}" ]]; then
        mkdir -p -- "${targetDirectory}"
    fi
    if ! output=$(rsync "${arguments[@]}" -- "${SOURCE_REPO}/${sourcePath}/" "${targetDirectory}/"); then
        outputError "failed to publish ${sourcePath}"
        exit "${EXIT_PUBLISH}"
    fi
    mapfile -t RSYNC_OUTPUT <<< "${output}"
    statisticsAdd RSYNC_OUTPUT
    if [[ "${VERBOSE}" == true && -n "${output}" ]]; then
        printf '%s\n' "${output}"
    fi
    log_done "$(basename -- "${targetPath}") published"
}

_rsyncExclusionsAdd() {
    local sourcePath=$1
    local -n argumentsReference=$2
    local excluded
    local -a excludedPaths=(.git .github .vscode documentation deploy scripts README.md LICENSE)

    for excluded in "${excludedPaths[@]}"; do
        if [[ "${sourcePath}" != "${excluded}" && "${sourcePath}" != "${excluded}/"* ]]; then
            argumentsReference+=(--exclude="${excluded}")
        fi
    done
}

statisticsAdd() {
    local -n linesReference=$1
    local line
    local item
    local name

    for line in "${linesReference[@]}"; do
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
    local baseBranch
    local branchName
    local sourceCommit
    local status
    local -a targetPaths=()
    local targetPath

    [[ "${COMMIT}" == true ]] || return 0
    sourceCommit=$(git -C "${SOURCE_REPO}" rev-parse --short HEAD)
    for targetPath in "${PUBLISH_TARGETS[@]}"; do
        targetPaths+=("${targetPath}")
    done

    status=$(git -C "${DESTINATION_REPO}" status --porcelain -- "${targetPaths[@]}")
    if [[ -z "${status}" ]]; then
        outputWarning 'no published changes to commit'
        return 0
    fi

    if [[ "${PUSH}" == true ]]; then
        baseBranch=$(git -C "${DESTINATION_REPO}" branch --show-current)
        [[ -n "${baseBranch}" ]] || {
            outputError 'destination repository must be on a branch before using --push'
            exit "${EXIT_GIT}"
        }
        branchName="publishAssets/${sourceCommit}-$(date -u +%Y%m%dT%H%M%SZ)"
        log_doing "creating destination branch ${branchName}"
        git -C "${DESTINATION_REPO}" switch -c "${branchName}" || exit "${EXIT_GIT}"
    fi

    [[ "${VERBOSE}" == true ]] && printf '\nStaging configured target folders.\n'
    log_doing 'staging configured target folders'
    git -C "${DESTINATION_REPO}" add -A -- "${targetPaths[@]}" || exit "${EXIT_GIT}"
    log_doing 'committing published asset folders'
    git -C "${DESTINATION_REPO}" commit \
        -m "Publish assets from clanneolas @ ${sourceCommit}" -- "${targetPaths[@]}" \
        || exit "${EXIT_GIT}"
    if [[ "${PUSH}" == true ]]; then
        log_doing "pushing destination branch ${branchName}"
        git -C "${DESTINATION_REPO}" push --set-upstream origin "${branchName}" \
            || exit "${EXIT_GIT}"
        log_doing 'opening pull request'
        pullRequestUrl=$(
            cd -- "${DESTINATION_REPO}"
            gh pr create \
                --base "${baseBranch}" \
                --head "${branchName}" \
                --title "Publish assets from clanneolas @ ${sourceCommit}" \
                --body "Automated asset publication from clanneolas source commit ${sourceCommit}."
        ) || exit "${EXIT_GIT}"
        log_done "pull request opened: ${pullRequestUrl}"
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
    if [[ -z "${dryRun}" && "${COMMIT}" != true ]]; then
        printf '\nAssets published locally. Changes were not committed or pushed.\n'
        printf 'Review them in the destination repository, or rerun with --commit or --push.\n'
    elif [[ -n "${pullRequestUrl}" ]]; then
        printf 'Pull request: %s\n' "${pullRequestUrl}"
    fi
    return 0
}

trap 'outputError "unexpected failure on line ${LINENO}"' ERR

main "$@"
