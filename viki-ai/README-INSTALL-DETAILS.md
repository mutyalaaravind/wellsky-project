Git
- Create a new SSH key
        ssh-keygen -t ed25519 -C "eric.coiner@wellsky.com"
        #Add it to ssh-agent
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_ed25519

- Add the public key to Github
        - Go to Settings | SSH and GPG keys
        - Click "New SSH Key"
        - Copy the contents of the public key into the form
- Install "git" and "gh"
        - Run "gh auth login"
                -GitHub Enterprise Server
                -github.com
                - ssh
                -Login using webbrowser

- Install VS Code
- Install pipenv
- Install pyenv
        - Install Python 3.11.5

- Install docker
        # Do the add docker apt repo and install through apt
        -Fix permissions
                sudo groupadd docker
                sudo usermod -aG docker $USER

                Log out and back in to gain the new group or run this instead:
                newgrp docker

- Install docker-compose
        # Need to install the plugin first
        sudo curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose-2.23.0
        sudo chmod a+x /usr/local/bin/docker-compose-2.23.0
        sudo ln -s /usr/local/bin/docker-compose-2.23.0 /user/local/bin/docker-compose
        sudo ln -s /usr/local/bin/docker-compose-2.23.0 /usr/bin/docker-compose

