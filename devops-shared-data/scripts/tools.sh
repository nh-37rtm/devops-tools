
set -eux


function setup_docker_dedicated_user()
{

    echo "Docker app user is : ${DOCKER_APP_USER}"
   
    useradd -ms /bin/bash ${DOCKER_APP_USER}
    usermod -aG sudo ${DOCKER_APP_USER}
    passwd --delete ${DOCKER_APP_USER}

}


function load_vars()
{

    # usage example

    # loads and exports variables defined inside shell
    # https://unix.stackexchange.com/questions/581230/why-doesnt-read-command-work-with-echo-and-piping
    # in the dev container the build environement should be available
    # load_vars < <(echo "$BUILD_TIME_ENV")
    # these should be available from build layer

    # https://stackoverflow.com/questions/46483941/source-configuration-file-avoiding-any-execution?rq=3
    while IFS='=' read -r conf_name conf_value
    do
        if test -z "$conf_name"
        then
            continue
        fi
        export "$conf_name"="$conf_value"
    done
}


