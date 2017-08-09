import configparser

"""options to parse (name: default value):
### Application-wide settings
    secret_string:                              blank       # Here should be a random secret string for encrypting
                                                            # users' cookies. By default it's random-generated
                                                            # each time application starts. That means that all user
                                                            # sessions/cookies become invalid each time application
                                                            # restarts. If you want to store user sessions after
                                                            # application restarts you should specify an
                                                            # alphanumeric string here.
    user_session_expires:                       never       # Possible values are minutes (integer) or "never"

### Login settings
    same_credentials_for_all_servers:           yes

### XenServer/XenCloudPlatform settings
    pool_url:                                   blank       # Here should be https URL leading to XenServer or XCP
                                                            # server or pool (e.g. https://172.31.0.10:443/)
    pool_description:                           blank       # Here should be description for the pool as it is shown to
                                                            # users

### VM installation settings
    installation_instructions_deploy_method:    local       # variants: ftp, sftp
    installation_instructions_deploy_path:      ./install_instructions/
                                                            # for ftp and sftp here should be path to server
    installation_instructions_login_username:   blank       # username to login with (for ftp and sftp method)
    installation_instructions_login_method:     password    # NOTE: dangerous. Possible values: [password, key]
    installation_instructions_login_password:   blank       # if previous value is "password" you should specify pass.

    installation_instructions_prefix_for_xen:   blank       # There should be http or anonymous ftp path
                                                            # (e.g. http://example.com/preseed/)

### Reverse proxy settings
    reverse_proxy_engine:                       nginx       #TODO: apache2, lighttpd, varnish-cache
    proxy_params_location:                      /etc/nginx/proxy_params
    ssl_params_location:                        /etc/nginx/ssl_params
    additional_params_location:                 blank       # here could be uwsgi_params etc (may be needed for specific
                                                            # deploy if all the applications for your backend are
                                                            # homogeneous and should have the same parameters)

"""