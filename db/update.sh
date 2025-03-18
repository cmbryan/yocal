#!/bin/env sh
 
# Pull changes from remote repository
git pull

# 'Stage' any changes you've made
git add -u

# Show the changes that are 'staged' and ready to be committed
git status

echo "\n*** Please review 'Changes to be committed' above ***"
read -p "Do you want to commit and upload these changes? (y/N): " answer
if [ "$answer" = "y" ]; then
    read -p "Please describe these changes: " commit_msg
    git commit -m "Update changes"
    git push
fi