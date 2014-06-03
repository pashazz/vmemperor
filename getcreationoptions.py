### This module fetches options required for VM creation ###
###

### Get options using plain xe protocol (for one session/pool(host) at one time)


def get_creation_options_fallback(session):
    print ("Getting creation options in fallback mode")
    api = session.xenapi
