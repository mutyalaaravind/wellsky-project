#!/bin/bash

#
# This script syncs files from one environment to another.   It excludes the following files from bein copied
#    * files that start with _ (underscore)
#    * files with extensions .tfstate .tfvars 
#    * files whose name are terraform.tf 
#    * directory .terraform
#
#  It will also delete any files in the target environment that do not exist in the source environment
#
#  This must be run from the root of the infrastructure repo which needs to be a git repo
#
#  Usage is promote.sh sourceEnv targetEnv  e.g.
#
#  promote development stage
# 
#  promote stage production
#

sourceEnv=${1^^}
sourceEnvDir="env/$1"
targetEnv=${2^^}
targetEnvDir="env/$2"
gh_exists=
git_username=
git_useremail=


declare -A ENVIRONMENTS=(
	[SANDBOX]=1
	[DEV]=2
	[DEVELOPMENT]=2
	[QA]=3
	[STAGE]=4
	[STAGING]=4
	[PROD]=5
	[PRODUCTION]=5
)

validate_environment() {

	if [ ! -d ".git" ]; then
	        printf "Current directory is not a git repo.  Make sure to run from within a git repo" >&2 
	        exit 1
	fi

	git_username=$(git config --get user.name)
	git_useremail=$(git config --get user.email)

	if [ -z "$git_username" ] || [ -z "$git_useremail" ]; then
		display_missing_git_userinfo
		exit 1
	fi

	if [ ! -d "$sourceEnvDir" ]; then
	        printf "Could not find source environment at %s\n" "$sourceEnvDir" >&2 
	        exit 1
	fi

	if [ ! -d "$targetEnvDir" ]; then
	        printf "Could not find target environment at %s\n" "$targetEnvDir" >&2 
	        exit 1
	fi

	command -v gh &>/dev/null
	declare -g gh_exists=$?
}

# Protect the main environments (Sandbox, Development, Stable, QA, Stage, and Production) but still allow
# users able to promote/create non-main environments from any main environment (ex: from dev to a demo environment).
# I am preventing the same environment name in two clusters, that is uncommon use-case.		
validate_target_enviroment() {	
	if [[ ${targetEnv} == ${sourceEnv} ]]; then
		printf "Source and Target environments must be different.\n" >&2 
		exit 1
	fi

	#if the target is not a "main" environment, do allow promotion
	if [[ -z ${ENVIRONMENTS[$targetEnv]} ]]; then
		return 1	
	fi

	#validate ordering of "main" environment promotion
	if [[ $((ENVIRONMENTS[$sourceEnv] +1)) == $((ENVIRONMENTS[$targetEnv])) ]]; then
		return 1
	fi

	printf "Environment promotion from %s to %s is not allowed.\n" "$sourceEnv" "$targetEnv" >&2 
	exit 1	
}

display_missing_git_userinfo() {

cat << EOF
Unable to detect git username or email.

Run
  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
EOF

}

git_commit() {

	# git
	printf -v BRANCH_NAME "%s_To_%s" $sourceEnv $targetEnv
	printf "Creating branch: %s\n" $BRANCH_NAME
	git checkout -b "$BRANCH_NAME"

	# sync the directories
	rsync -avr --delete --exclude '*.tfvars' --exclude '*.tfstate' --exclude 'backend.tf' --exclude 'terraform.tf' --exclude '*-temp.tf' --exclude '.terraform/' --exclude '_*' $sourceEnvDir/ $targetEnvDir/

	# add untracked files
	git add -A 

	# commit
	git commit --quiet -am "Promote "${sourceEnv^^}" to "${targetEnv^^}""

	push_quiet=
	if [ $gh_exists -eq 0 ]; then
		push_quiet="--quiet"
	fi

	git push $push_quiet --set-upstream origin "$BRANCH_NAME"
}

###########

if [[ $# -ne 2 ]]; then
    printf "Incorrect number of arguments.\n" >&2 
    printf "This script expects 2 argumnets, source environment and target environment.\n"
    exit 2
fi

source=$1
target=$2
sourceEnv=${source^^}
targetEnv=${target^^}

validate_target_enviroment
validate_environment

printf "*** Promoting infrastructure from %s to %s\n\n" "${sourceEnv^^}" "${targetEnv^^}"

git_commit

# check if gh is installed
if [ $gh_exists -eq 0 ]; then
	printf "Creating PR"
    gh pr create --fill
	gh pr view --web
fi
