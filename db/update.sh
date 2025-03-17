#!/bin/env sh
 
git add -u
git status

echo "\nPlease review 'Changes to be committed' above."
read -p "Do you want to commit and upload these changes? (y/N): " answer
if [ "$answer" = "y" ]; then
    read -p "Please describe these changes: " commit_msg
    git commit -m "Update changes"
    git push
fi